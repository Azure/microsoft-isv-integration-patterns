from __future__ import annotations

import json
import struct
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONNECTOR = ROOT / "connector"
PACKAGE = ROOT / "dist" / "snowflake-copilot-studio-connector-source.zip"


class ConnectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.definition = json.loads(
            (CONNECTOR / "apiDefinition.swagger.json").read_text(encoding="utf-8")
        )
        cls.properties = json.loads(
            (CONNECTOR / "apiProperties.json").read_text(encoding="utf-8")
        )

    def test_required_source_files_exist(self) -> None:
        for relative_path in (
            "README.md",
            "intro.md",
            "connector/apiDefinition.swagger.json",
            "connector/apiProperties.json",
            "connector/icon.png",
        ):
            with self.subTest(path=relative_path):
                self.assertTrue((ROOT / relative_path).is_file())

    def test_openapi_metadata_meets_connector_limits(self) -> None:
        info = self.definition["info"]
        self.assertEqual(self.definition["swagger"], "2.0")
        self.assertLessEqual(len(info["title"]), 30)
        self.assertNotIn("api", info["title"].lower())
        self.assertNotIn("connector", info["title"].lower())
        self.assertGreaterEqual(len(info["description"]), 30)
        self.assertLessEqual(len(info["description"]), 500)
        self.assertEqual(self.definition["schemes"], ["https"])

    def test_mcp_operation_uses_streamable_http(self) -> None:
        operations = [
            operation
            for path in self.definition["paths"].values()
            for method, operation in path.items()
            if method.lower() == "post"
        ]
        self.assertEqual(len(operations), 1)
        operation = operations[0]
        self.assertEqual(operation["operationId"], "InvokeMCP")
        self.assertEqual(operation["x-ms-agentic-protocol"], "mcp-streamable-1.0")
        self.assertIn("application/json", operation["consumes"])
        self.assertLessEqual(len(operation["summary"]), 80)
        self.assertIn("200", operation["responses"])
        self.assertIn("401", operation["responses"])
        self.assertIn("403", operation["responses"])
        self.assertIn("429", operation["responses"])

    def test_oauth_settings_match_definition(self) -> None:
        security = self.definition["securityDefinitions"]["oauth2-auth"]
        oauth = self.properties["properties"]["connectionParameters"]["token"][
            "oAuthSettings"
        ]
        self.assertEqual(security["type"], "oauth2")
        self.assertEqual(security["flow"], "accessCode")
        self.assertTrue(security["authorizationUrl"].startswith("https://"))
        self.assertTrue(security["tokenUrl"].startswith("https://"))
        self.assertIn("refresh_token", security["scopes"])
        self.assertEqual(oauth["scopes"], ["{Scope}"])
        self.assertEqual(oauth["identityProvider"], "oauth2generic")
        self.assertEqual(oauth["clientId"], "PLACEHOLDER_CLIENTID")
        self.assertNotIn("REPLACE_WITH_REDIRECT_URL", json.dumps(self.properties))

    def test_oauth_client_configuration_is_supplied_per_connection(self) -> None:
        parameters = self.properties["properties"]["connectionParameters"]
        self.assertEqual(parameters["token:ClientId"]["type"], "string")
        self.assertEqual(parameters["token:ClientSecret"]["type"], "securestring")
        self.assertEqual(parameters["token:Scope"]["type"], "string")
        for name in ("token:ClientId", "token:ClientSecret", "token:Scope"):
            self.assertEqual(
                parameters[name]["uiDefinition"]["constraints"]["required"], "true"
            )

        oauth = parameters["token"]["oAuthSettings"]
        self.assertEqual(oauth["scopes"], ["{Scope}"])
        templates = oauth["customParameters"]
        self.assertIn("{ClientId}", json.dumps(templates))
        self.assertIn("{ClientSecret}", json.dumps(templates))
        self.assertIn("{Scope}", json.dumps(templates))
        self.assertIn("{RedirectUrl}", json.dumps(templates))
        self.assertIn("{State}", json.dumps(templates))
        self.assertIn("{Code}", json.dumps(templates))
        self.assertIn("{RefreshToken}", json.dumps(templates))
        self.assertEqual(oauth["clientId"], "PLACEHOLDER_CLIENTID")

    def test_snowflake_endpoint_is_supplied_per_connection(self) -> None:
        properties = self.properties["properties"]
        parameters = properties["connectionParameters"]
        for name in ("token:accountIdentifier", "database", "schema", "mcpServer"):
            with self.subTest(parameter=name):
                self.assertIn(name, parameters)
                self.assertEqual(parameters[name]["type"], "string")
                self.assertEqual(
                    parameters[name]["uiDefinition"]["constraints"]["required"], "true"
                )

        policies = json.dumps(properties["policyTemplateInstances"])
        self.assertIn("@connectionParameters('token:accountIdentifier')", policies)
        self.assertIn(".snowflakecomputing.com", policies)
        self.assertNotIn("@connectionParameters('token:accountUrl')", policies)
        self.assertIn("@connectionParameters('database')", policies)
        self.assertIn("@connectionParameters('schema')", policies)
        self.assertIn("@connectionParameters('mcpServer')", policies)
        self.assertIn("dynamichosturl", policies)
        self.assertIn("routerequesttoendpoint", policies)

        oauth = parameters["token"]["oAuthSettings"]
        oauth_templates = json.dumps(oauth["customParameters"])
        self.assertEqual(oauth["identityProvider"], "oauth2generic")
        self.assertIn("{accountIdentifier}", oauth_templates)
        self.assertNotIn("REPLACE_WITH_ACCOUNT", oauth_templates)

        operation_ids = {
            operation["operationId"]
            for path in self.definition["paths"].values()
            for method, operation in path.items()
            if method.lower() in {"get", "post", "put", "patch", "delete"}
        }
        for policy in properties["policyTemplateInstances"]:
            configured_operations = policy["parameters"].get(
                "x-ms-apimTemplate-operationName", []
            )
            self.assertTrue(set(configured_operations).issubset(operation_ids))

    def test_openapi_contains_no_fixed_snowflake_endpoint(self) -> None:
        definition = json.dumps(self.definition)
        for token in (
            "REPLACE_WITH_ACCOUNT",
            "REPLACE_WITH_DATABASE",
            "REPLACE_WITH_SCHEMA",
            "REPLACE_WITH_MCP_SERVER",
        ):
            self.assertNotIn(token, definition)
        self.assertEqual(self.definition["basePath"], "/")
        self.assertEqual(set(self.definition["paths"]), {"/mcp"})

    def test_template_marks_all_publisher_owned_values(self) -> None:
        combined = json.dumps(self.definition) + json.dumps(self.properties)
        for token in (
            "REPLACE_WITH_AUTHORIZED_PUBLISHER",
        ):
            with self.subTest(token=token):
                self.assertIn(token, combined)

    def test_icon_is_128_pixel_rgba_png(self) -> None:
        data = (CONNECTOR / "icon.png").read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        width, height, bit_depth, color_type = struct.unpack(">IIBB", data[16:26])
        self.assertEqual((width, height), (128, 128))
        self.assertEqual(bit_depth, 8)
        self.assertEqual(color_type, 6)

    def test_intro_covers_submission_topics(self) -> None:
        intro = (ROOT / "intro.md").read_text(encoding="utf-8").lower()
        for topic in (
            "business purpose",
            "supported tools",
            "prerequisites",
            "authentication",
            "limitations",
            "privacy",
            "support",
        ):
            with self.subTest(topic=topic):
                self.assertIn(topic, intro)

    def test_source_package_has_expected_public_files(self) -> None:
        if not PACKAGE.is_file():
            self.skipTest("Run scripts/build_source_package.py to create the archive")
        with zipfile.ZipFile(PACKAGE) as archive:
            self.assertEqual(
                set(archive.namelist()),
                {
                    "snowflake/README.md",
                    "snowflake/intro.md",
                    "snowflake/connector/apiDefinition.swagger.json",
                    "snowflake/connector/apiProperties.json",
                    "snowflake/connector/icon.png",
                },
            )
            self.assertIsNone(archive.testzip())


if __name__ == "__main__":
    unittest.main()
