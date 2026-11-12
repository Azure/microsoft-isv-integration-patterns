"""Check a Snowflake MCP endpoint directly, not the deployed Power Platform connector."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

PROTOCOL_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26")


class ValidationError(Exception):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValidationError("Redirect refused. Use the canonical public Snowflake endpoint.")


def validate_url(url: str) -> str:
    parts = urlsplit(url)
    if (
        parts.scheme != "https"
        or not re.fullmatch(
            r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.snowflakecomputing\.com",
            parts.hostname or "",
        )
        or parts.port not in (None, 443)
        or parts.username is not None
        or parts.password is not None
        or parts.query
        or parts.fragment
        or not re.fullmatch(
            r"/api/v2/databases/[^/]+/schemas/[^/]+/mcp-servers/[^/]+", parts.path
        )
    ):
        raise ValidationError(
            "Use an HTTPS public Snowflake-managed MCP URL with database, schema, and "
            "server path; no credentials, query, fragment, or underscore in the hostname."
        )
    return url


def build_url(account: str, database: str, schema: str, server: str) -> str:
    for label, value in (("database", database), ("schema", schema), ("MCP server", server)):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_$]*", value):
            raise ValidationError(
                f"The {label} must be a single unquoted identifier, not a qualified name "
                "or path. Use --url for an existing URL with encoded identifiers."
            )
    return validate_url(
        f"https://{account}.snowflakecomputing.com/api/v2/databases/{database}"
        f"/schemas/{schema}/mcp-servers/{server}"
    )


def required_environment(name: str) -> str:
    value = os.environ.get(name)
    if not value or not value.strip():
        raise ValidationError(f"Set {name} securely in the process environment.")
    return value


def rpc_result(message, request_id: int) -> dict:
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
        raise ValidationError("Response is not a JSON-RPC 2.0 object.")
    if message.get("id") != request_id:
        raise ValidationError("JSON-RPC response ID does not match the request.")
    if "error" in message:
        raise ValidationError("Server returned a JSON-RPC error; inspect Snowflake audit logs.")
    if not isinstance(message.get("result"), dict):
        raise ValidationError("JSON-RPC response has no object result.")
    return message["result"]


def read_result(response, request_id: int) -> dict:
    content_type = response.headers.get_content_type()
    if content_type == "application/json":
        return rpc_result(json.load(response), request_id)
    if content_type != "text/event-stream":
        raise ValidationError("Expected application/json or text/event-stream response.")
    data = []
    for raw_line in response:
        line = raw_line.decode("utf-8").rstrip("\r\n")
        if line.startswith("data:"):
            data.append(line[5:].removeprefix(" "))
        elif not line and data:
            event = "\n".join(data)
            data = []
            if event == "[DONE]":
                break
            message = json.loads(event)
            if isinstance(message, dict) and message.get("id") == request_id:
                return rpc_result(message, request_id)
    raise ValidationError("SSE stream ended without the matching JSON-RPC response.")


class MCPClient:
    def __init__(self, endpoint: str, access_token: str):
        self.endpoint = endpoint
        self.opener = build_opener(NoRedirect())
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }

    def send(self, method: str, params: dict | None = None, request_id: int | None = None):
        message = {"jsonrpc": "2.0", "method": method}
        if request_id is not None:
            message["id"] = request_id
        if params is not None:
            message["params"] = params
        request = Request(
            self.endpoint, json.dumps(message).encode("utf-8"), self.headers, method="POST"
        )
        try:
            with self.opener.open(request, timeout=60) as response:
                if request_id is None:
                    if response.status != 202:
                        raise ValidationError(f"{method}: expected HTTP 202 for notification.")
                    return None
                if response.status != 200:
                    raise ValidationError(f"{method}: expected HTTP 200.")
                result = read_result(response, request_id)
                if method == "initialize":
                    version = result.get("protocolVersion")
                    if version not in PROTOCOL_VERSIONS:
                        raise ValidationError("Server negotiated an unsupported MCP version.")
                    self.headers["MCP-Protocol-Version"] = version
                    session = response.headers.get("MCP-Session-Id")
                    if session:
                        self.headers["MCP-Session-Id"] = session
                return result
        except HTTPError as error:
            raise ValidationError(
                f"{method}: HTTP {error.code}. Check endpoint, OAuth, grants, and network policy."
            ) from error


def refresh_access_token(endpoint: str) -> str:
    body = urlencode(
        {
            "grant_type": "refresh_token",
            "refresh_token": required_environment("SNOWFLAKE_MCP_REFRESH_TOKEN"),
            "client_id": required_environment("SNOWFLAKE_OAUTH_CLIENT_ID"),
            "client_secret": required_environment("SNOWFLAKE_OAUTH_CLIENT_SECRET"),
        }
    ).encode("utf-8")
    parts = urlsplit(endpoint)
    request = Request(
        f"https://{parts.netloc}/oauth/token-request",
        body,
        {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        method="POST",
    )
    with build_opener(NoRedirect()).open(request, timeout=60) as response:
        token = json.load(response)
    if (
        not isinstance(token, dict)
        or not isinstance(token.get("access_token"), str)
        or not token["access_token"].strip()
        or not isinstance(token.get("token_type"), str)
        or token.get("token_type", "").lower() != "bearer"
    ):
        raise ValidationError("Refresh did not return a Bearer access token.")
    return token["access_token"]


def validate_connection(endpoint: str, token: str, tool: str | None, arguments: dict) -> None:
    client = MCPClient(endpoint, token)
    initialized = client.send(
        "initialize",
        {
            "protocolVersion": PROTOCOL_VERSIONS[0],
            "capabilities": {},
            "clientInfo": {"name": "snowflake-connector-validation", "version": "1.1"},
        },
        1,
    )
    if not isinstance(initialized.get("capabilities"), dict) or not isinstance(
        initialized["capabilities"].get("tools"), dict
    ):
        raise ValidationError("Server does not advertise MCP tool capabilities.")
    client.send("notifications/initialized")
    print("MCP initialization passed.")
    names = set()
    cursors = set()
    params = {}
    request_id = 2
    while True:
        result = client.send("tools/list", params, request_id)
        tools = result.get("tools")
        if not isinstance(tools, list) or any(
            not isinstance(item, dict)
            or not isinstance(item.get("name"), str)
            or not item["name"].strip()
            or not isinstance(item.get("inputSchema"), dict)
            or item["inputSchema"].get("type") != "object"
            for item in tools
        ):
            raise ValidationError("tools/list did not return named tools with object input schemas.")
        names.update(item["name"] for item in tools)
        cursor = result.get("nextCursor")
        if cursor is None:
            break
        if not isinstance(cursor, str) or not cursor or cursor in cursors:
            raise ValidationError("tools/list returned an invalid or repeated cursor.")
        cursors.add(cursor)
        params = {"cursor": cursor}
        request_id += 1
    if not names:
        raise ValidationError("No visible tools. Check the effective role and object privileges.")
    print(f"Tool discovery passed ({len(names)} tools).")
    if tool is not None:
        if tool not in names:
            raise ValidationError("Requested tool was not returned by tools/list.")
        result = client.send("tools/call", {"name": tool, "arguments": arguments}, request_id + 1)
        if result.get("isError"):
            raise ValidationError("Tool execution returned isError; inspect Snowflake audit logs.")
        print("Tool execution passed.")
    else:
        print("Tool execution not checked. Supply --tool and approved --arguments to check it.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="Complete public Snowflake-managed MCP endpoint")
    parser.add_argument("--account", help="Organization-account hostname prefix")
    parser.add_argument("--database")
    parser.add_argument("--schema")
    parser.add_argument("--mcp-server")
    parser.add_argument("--tool", help="Only invoke an explicitly approved test tool")
    parser.add_argument("--arguments", help="Tool arguments as a JSON object")
    parser.add_argument("--check-refresh", action="store_true", help="Use a dedicated test refresh token")
    args = parser.parse_args()
    try:
        components = (args.account, args.database, args.schema, args.mcp_server)
        if args.url:
            if any(value is not None for value in components):
                raise ValidationError("Use --url OR all four endpoint components, not both.")
            endpoint = validate_url(args.url)
        else:
            if not all(components):
                raise ValidationError("Supply --url OR --account, --database, --schema, --mcp-server.")
            endpoint = build_url(*components)
        if args.arguments is not None and args.tool is None:
            raise ValidationError("--arguments requires --tool.")
        arguments = json.loads(args.arguments) if args.arguments is not None else {}
        if not isinstance(arguments, dict):
            raise ValidationError("--arguments must be a JSON object.")
        if args.check_refresh:
            token = refresh_access_token(endpoint)
            print("OAuth refresh passed (use a dedicated test connection if tokens rotate).")
        else:
            token = required_environment("SNOWFLAKE_MCP_ACCESS_TOKEN")
        validate_connection(endpoint, token, args.tool, arguments)
    except (ValidationError, ValueError, OSError, URLError) as error:
        # Never print token response bodies, tool arguments, or confidential tool results.
        if isinstance(error, HTTPError):
            message = f"HTTP {error.code}. Check OAuth configuration and network policy."
        elif isinstance(error, ValueError):
            message = "Invalid URL, JSON arguments, or server JSON response."
        else:
            message = str(error)
        print(f"Connection validation failed: {message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
