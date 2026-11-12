from __future__ import annotations

import io
import json
import os
import subprocess
import unittest
from contextlib import redirect_stderr, redirect_stdout
from email.message import Message
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.error import HTTPError
from urllib.parse import parse_qs

from snowflake.scripts import deploy_connector as deployment
from snowflake.scripts import validate_connection as probe

ENDPOINT = (
    "https://myorg-myaccount.snowflakecomputing.com/api/v2/databases/"
    "MY_DATABASE/schemas/MY_SCHEMA/mcp-servers/MY_MCP_SERVER"
)
TOOL = {"name": "approved_tool", "inputSchema": {"type": "object"}}


class Response(io.BytesIO):
    def __init__(self, body=b"", content_type="application/json", status=200, session=None):
        super().__init__(body)
        self.status = status
        self.headers = Message()
        self.headers["Content-Type"] = content_type
        if session is not None:
            self.headers["MCP-Session-Id"] = session


def rpc_response(request_id, result, stream=False, session=None):
    body = json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}).encode()
    if stream:
        return Response(
            b": heartbeat\r\n\r\ndata: " + body + b"\r\n\r\ndata: [DONE]\r\n\r\n",
            "text/event-stream",
            session=session,
        )
    return Response(body, session=session)


def initialization():
    return rpc_response(
        1,
        {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}},
        session="test-session",
    )


class ConnectionValidationTests(unittest.TestCase):
    def test_components_and_full_url_select_the_same_endpoint(self):
        self.assertEqual(
            probe.build_url("myorg-myaccount", "MY_DATABASE", "MY_SCHEMA", "MY_MCP_SERVER"),
            ENDPOINT,
        )
        self.assertEqual(probe.validate_url(ENDPOINT), ENDPOINT)
        for url in (
            ENDPOINT.replace("https:", "http:"),
            ENDPOINT.replace("myorg-myaccount", "myorg_myaccount"),
            ENDPOINT.replace(".snowflakecomputing.com", ".example.com"),
            ENDPOINT.replace("https://", "https://user:password@"),
            ENDPOINT + "?token=do-not-send",
            ENDPOINT + "#fragment",
            ENDPOINT.rsplit("/", 1)[0],
        ):
            with self.subTest(url=url), self.assertRaises(probe.ValidationError):
                probe.validate_url(url)
        with self.assertRaises(probe.ValidationError):
            probe.build_url("myorg-myaccount", "DB/OTHER", "MY_SCHEMA", "MY_MCP_SERVER")

    @patch.object(probe, "build_opener")
    def test_lifecycle_pagination_and_sse_tool_call_preserve_headers(self, build_opener):
        opener = build_opener.return_value
        opener.open.side_effect = [
            initialization(),
            Response(status=202),
            rpc_response(2, {"tools": [TOOL], "nextCursor": "page-two"}),
            rpc_response(3, {"tools": [], "nextCursor": None}, stream=True),
            rpc_response(4, {"content": [{"type": "text", "text": "private-result"}]}, stream=True),
        ]
        output = io.StringIO()
        with redirect_stdout(output):
            probe.validate_connection(ENDPOINT, "test-access-token", "approved_tool", {"text": "test"})
        requests = [call.args[0] for call in opener.open.call_args_list]
        self.assertEqual(len(requests), 5)
        for request in requests:
            self.assertEqual(request.full_url, ENDPOINT)
            self.assertEqual(request.get_method(), "POST")
            self.assertEqual(request.get_header("Authorization"), "Bearer test-access-token")
            self.assertEqual(request.get_header("Accept"), "application/json, text/event-stream")
        for request in requests[1:]:
            self.assertEqual(request.get_header("Mcp-session-id"), "test-session")
            self.assertEqual(request.get_header("Mcp-protocol-version"), "2025-06-18")
        messages = [json.loads(request.data) for request in requests]
        self.assertNotIn("id", messages[1])
        self.assertEqual(messages[1]["method"], "notifications/initialized")
        self.assertEqual(messages[3]["params"], {"cursor": "page-two"})
        self.assertEqual(messages[4]["method"], "tools/call")
        self.assertEqual(messages[4]["params"], {"name": "approved_tool", "arguments": {"text": "test"}})
        self.assertNotIn("test-access-token", output.getvalue())
        self.assertNotIn("private-result", output.getvalue())

    @patch.object(probe, "build_opener")
    def test_discovery_does_not_invoke_tools_without_opt_in(self, build_opener):
        opener = build_opener.return_value
        opener.open.side_effect = [
            initialization(), Response(status=202), rpc_response(2, {"tools": [TOOL]})
        ]
        with redirect_stdout(io.StringIO()):
            probe.validate_connection(ENDPOINT, "test-token", None, {})
        self.assertEqual(opener.open.call_count, 3)

    @patch.object(probe, "build_opener")
    def test_empty_tools_and_tool_errors_are_failures(self, build_opener):
        for tools, tool, call_result, expected in (
            ([], None, None, "No visible tools"),
            ([TOOL], "approved_tool", {"isError": True}, "isError"),
            ([{"name": "broken"}], None, None, "input schemas"),
        ):
            with self.subTest(expected=expected):
                build_opener.return_value.open.side_effect = [
                    initialization(),
                    Response(status=202),
                    rpc_response(2, {"tools": tools}),
                    rpc_response(3, call_result),
                ]
                with redirect_stdout(io.StringIO()), self.assertRaisesRegex(
                    probe.ValidationError, expected
                ):
                    probe.validate_connection(ENDPOINT, "test-token", tool, {})

    def test_json_rpc_errors_and_incomplete_sse_are_failures(self):
        for response, expected in (
            (Response(b"data: [DONE]\n\n", "text/event-stream"), "without the matching"),
            (Response(b'{"jsonrpc":"2.0","id":9,"result":{}}'), "does not match"),
            (
                Response(b'{"jsonrpc":"2.0","id":1,"error":{"code":-32602}}'),
                "JSON-RPC error",
            ),
        ):
            with self.subTest(expected=expected), response, self.assertRaisesRegex(
                probe.ValidationError, expected
            ):
                probe.read_result(response, 1)

    @patch.object(probe, "build_opener")
    def test_http_errors_fail_with_stage_and_status(self, build_opener):
        build_opener.return_value.open.side_effect = HTTPError(
            ENDPOINT, 401, "Unauthorized", Message(), None
        )
        with self.assertRaisesRegex(probe.ValidationError, "initialize: HTTP 401"):
            probe.MCPClient(ENDPOINT, "test-token").send("initialize", {}, 1)

    @patch.dict(
        os.environ,
        {
            "SNOWFLAKE_MCP_REFRESH_TOKEN": "test-refresh+&=",
            "SNOWFLAKE_OAUTH_CLIENT_ID": "test-client+&=",
            "SNOWFLAKE_OAUTH_CLIENT_SECRET": "test-secret+&=",
        },
    )
    @patch.object(probe, "build_opener")
    def test_refresh_uses_form_encoding_and_does_not_send_basic_auth(self, build_opener):
        build_opener.return_value.open.return_value = Response(
            b'{"access_token":"new-test-token","token_type":"Bearer"}'
        )
        self.assertEqual(probe.refresh_access_token(ENDPOINT), "new-test-token")
        request = build_opener.return_value.open.call_args.args[0]
        self.assertEqual(
            request.full_url, "https://myorg-myaccount.snowflakecomputing.com/oauth/token-request"
        )
        self.assertIsNone(request.get_header("Authorization"))
        self.assertEqual(request.get_header("Content-type"), "application/x-www-form-urlencoded")
        self.assertEqual(
            parse_qs(request.data.decode()),
            {
                "grant_type": ["refresh_token"],
                "refresh_token": ["test-refresh+&="],
                "client_id": ["test-client+&="],
                "client_secret": ["test-secret+&="],
            },
        )

    @patch.dict(os.environ, {}, clear=True)
    @patch.object(probe, "build_opener")
    def test_missing_token_exits_without_network_or_success(self, build_opener):
        output = io.StringIO()
        with patch("sys.argv", ["validate_connection.py", "--url", ENDPOINT]):
            with redirect_stderr(output):
                self.assertEqual(probe.main(), 1)
        self.assertIn("SNOWFLAKE_MCP_ACCESS_TOKEN", output.getvalue())
        build_opener.assert_not_called()


class DeploymentTests(unittest.TestCase):
    @patch.object(deployment.shutil, "which", return_value="paconn")
    @patch.object(deployment.subprocess, "run")
    def test_create_and_update_deploy_both_artifacts_and_clean_staging(self, run, which):
        for connector_id in (None, "existing-connector"):
            with self.subTest(connector_id=connector_id):
                paths = []

                def inspect_staged_properties(command, check):
                    self.assertTrue(check)
                    self.assertEqual(command[1], "update" if connector_id else "create")
                    self.assertEqual(command[command.index("--env") + 1], "test-environment")
                    self.assertTrue(Path(command[command.index("--api-def") + 1]).is_file())
                    path = Path(command[command.index("--api-prop") + 1])
                    paths.append(path)
                    staged = json.loads(path.read_text(encoding="utf-8"))["properties"]
                    self.assertEqual(staged["publisher"], "Authorized publisher")
                    self.assertNotIn("stackOwner", staged)
                    original = json.loads(
                        (deployment.CONNECTOR / "apiProperties.json").read_text(encoding="utf-8")
                    )["properties"]
                    self.assertEqual(staged["connectionParameters"], original["connectionParameters"])
                    self.assertEqual(staged["policyTemplateInstances"], original["policyTemplateInstances"])
                    if connector_id:
                        self.assertEqual(command[command.index("--cid") + 1], connector_id)
                    else:
                        self.assertNotIn("--cid", command)

                run.side_effect = inspect_staged_properties
                deployment.deploy("test-environment", "Authorized publisher", connector_id)
                self.assertEqual(len(paths), 1)
                self.assertFalse(paths[0].exists())

    @patch.object(deployment.shutil, "which", return_value="paconn")
    @patch.object(deployment.subprocess, "run")
    def test_failed_deployment_is_not_reported_as_success_and_cleans_staging(self, run, which):
        paths = []

        def fail(command, check):
            paths.append(Path(command[command.index("--api-prop") + 1]))
            raise subprocess.CalledProcessError(1, command)

        run.side_effect = fail
        with self.assertRaises(subprocess.CalledProcessError):
            deployment.deploy("test-environment", "Authorized publisher", "existing-connector")
        self.assertEqual(len(paths), 1)
        self.assertFalse(paths[0].exists())

    @patch.object(deployment.shutil, "which", return_value=None)
    def test_missing_cli_has_an_explicit_actionable_error(self, which):
        with self.assertRaisesRegex(FileNotFoundError, "pip install paconn"):
            deployment.deploy("test-environment", "Authorized publisher")


if __name__ == "__main__":
    unittest.main()
