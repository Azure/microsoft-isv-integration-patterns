"""Deploy both Snowflake connector artifacts with paconn; never collect OAuth secrets."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CONNECTOR = Path(__file__).resolve().parents[1] / "connector"


def deploy(environment: str, publisher: str, connector_id: str | None = None) -> None:
    if not environment.strip() or not publisher.strip():
        raise ValueError("Environment and publisher must not be empty.")
    if publisher == "REPLACE_WITH_AUTHORIZED_PUBLISHER":
        raise ValueError("Supply the authorized publisher name, not the template token.")
    if connector_id is not None and not connector_id.strip():
        raise ValueError("Connector ID must not be empty when updating a connector.")
    executable = shutil.which("paconn")
    if executable is None:
        raise FileNotFoundError("paconn is not installed. Run: python -m pip install paconn")

    properties = json.loads((CONNECTOR / "apiProperties.json").read_text(encoding="utf-8"))
    properties["properties"]["publisher"] = publisher
    # paconn cannot update local custom connectors containing certification stackOwner.
    properties["properties"].pop("stackOwner", None)
    with tempfile.TemporaryDirectory(prefix="snowflake-connector-") as directory:
        local_properties = Path(directory) / "apiProperties.json"
        local_properties.write_text(json.dumps(properties, indent=2), encoding="utf-8")
        command = [
            executable,
            "update" if connector_id is not None else "create",
            "--env",
            environment,
            "--api-def",
            str(CONNECTOR / "apiDefinition.swagger.json"),
            "--api-prop",
            str(local_properties),
            "--icon",
            str(CONNECTOR / "icon.png"),
        ]
        if connector_id is not None:
            command.extend(["--cid", connector_id])
        subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", required=True, help="Power Platform environment ID")
    parser.add_argument("--publisher", required=True, help="Authorized publisher name")
    parser.add_argument("--connector-id", help="Update this existing connector; omit to create")
    args = parser.parse_args()
    try:
        deploy(args.environment, args.publisher, args.connector_id)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Connector deployment failed: {error}", file=sys.stderr)
        return 1
    print("Connector artifacts deployed. Register its callback, then create a new connection.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
