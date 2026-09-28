"""Build a deterministic archive of the public connector source artifacts."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist" / "mongodb-copilot-studio-connector-source.zip"
FILES = (
    ROOT / "README.md",
    ROOT / "intro.md",
    ROOT / "THIRD-PARTY-NOTICES.md",
    ROOT / "connector" / "apiDefinition.swagger.json",
    ROOT / "connector" / "apiProperties.json",
    ROOT / "connector" / "icon.png",
)


def build() -> Path:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing package files: {', '.join(missing)}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        OUTPUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path in FILES:
            info = zipfile.ZipInfo(
                f"mongodb/{path.relative_to(ROOT).as_posix()}",
                date_time=(2026, 1, 1, 0, 0, 0),
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return OUTPUT


if __name__ == "__main__":
    try:
        output = build()
    except (FileNotFoundError, OSError) as error:
        print(f"Package build failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    print(f"Built {output}")
