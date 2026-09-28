from __future__ import annotations

import hashlib
import json
import struct
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONNECTOR = ROOT / "connector"
PACKAGE = ROOT / "dist" / "mongodb-copilot-studio-connector-source.zip"


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
            "assets/mongodb.svg",
            "docs/certification-research.md",
            "THIRD-PARTY-NOTICES.md",
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

    def test_mcp_operation_uses_fixed_streamable_http_endpoint(self) -> None:
        self.assertEqual(self.definition["host"], "mcp.mongodb.com")
        self.assertEqual(self.definition["basePath"], "/")
        self.assertEqual(set(self.definition["paths"]), {"/"})
        operation = self.definition["paths"]["/"]["post"]
        self.assertEqual(operation["operationId"], "InvokeMCP")
        self.assertEqual(operation["x-ms-agentic-protocol"], "mcp-streamable-1.0")
        self.assertIn("application/json", operation["consumes"])
        self.assertLessEqual(len(operation["summary"]), 80)
        for status in ("200", "401", "403", "429"):
            self.assertIn(status, operation["responses"])
        self.assertEqual(
            self.properties["properties"]["policyTemplateInstances"], []
        )

    def test_oauth_settings_match_fixed_mongodb_metadata(self) -> None:
        security = self.definition["securityDefinitions"]["oauth2-auth"]
        oauth = self.properties["properties"]["connectionParameters"]["token"][
            "oAuthSettings"
        ]
        self.assertEqual(security["type"], "oauth2")
        self.assertEqual(security["flow"], "accessCode")
        self.assertEqual(
            security["authorizationUrl"], "https://cloud.mongodb.com/oauth/authorize"
        )
        self.assertEqual(
            security["tokenUrl"], "https://authorize.mongodb.com/tokens"
        )
        self.assertEqual(security["scopes"], {})
        self.assertEqual(oauth["identityProvider"], "oauth2")
        self.assertEqual(oauth["scopes"], [])
        templates = oauth["customParameters"]
        self.assertEqual(
            templates["authorizationUrl"]["value"],
            "https://cloud.mongodb.com/oauth/authorize",
        )
        self.assertEqual(
            templates["tokenUrl"]["value"], "https://authorize.mongodb.com/tokens"
        )
        self.assertEqual(
            templates["refreshUrl"]["value"],
            "https://authorize.mongodb.com/tokens",
        )

    def test_oauth_credentials_are_present_and_empty(self) -> None:
        oauth = self.properties["properties"]["connectionParameters"]["token"][
            "oAuthSettings"
        ]
        self.assertIn("clientId", oauth)
        self.assertIn("clientSecret", oauth)
        self.assertEqual(oauth["clientId"], "")
        self.assertEqual(oauth["clientSecret"], "")

    def test_template_marks_publisher_owned_values(self) -> None:
        combined = json.dumps(self.definition) + json.dumps(self.properties)
        self.assertIn("REPLACE_WITH_REDIRECT_URL", combined)
        self.assertIn("REPLACE_WITH_AUTHORIZED_PUBLISHER", combined)
        self.assertNotIn("REPLACE_WITH_MCP_SERVER", combined)

    def test_icon_is_128_pixel_rgba_png(self) -> None:
        data = (CONNECTOR / "icon.png").read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        width, height, bit_depth, color_type = struct.unpack(">IIBB", data[16:26])
        self.assertEqual((width, height), (128, 128))
        self.assertEqual(bit_depth, 8)
        self.assertEqual(color_type, 6)

    def test_icon_uses_azure_mcp_mongodb_asset(self) -> None:
        svg = (ROOT / "assets" / "mongodb.svg").read_bytes()
        self.assertEqual(
            hashlib.sha256(svg).hexdigest(),
            "a143cb59fdba7c1e01e8f67b8086a22b96806db2f5aa811f95f6515490c07416",
        )
        self.assertIn(b'viewBox="0 0 120 258"', svg)
        self.assertIn(b"#00684A", svg)
        self.assertEqual(
            self.properties["properties"]["iconBrandColor"].lower(), "#00684a"
        )

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
                    "mongodb/README.md",
                    "mongodb/intro.md",
                    "mongodb/THIRD-PARTY-NOTICES.md",
                    "mongodb/connector/apiDefinition.swagger.json",
                    "mongodb/connector/apiProperties.json",
                    "mongodb/connector/icon.png",
                },
            )
            self.assertIsNone(archive.testzip())


if __name__ == "__main__":
    unittest.main()
