"""Generate the connector icon without third-party dependencies."""

from __future__ import annotations

import binascii
import math
import struct
import zlib
from pathlib import Path

SIZE = 128
BACKGROUND = (17, 86, 127, 255)
FOREGROUND = (255, 255, 255, 255)


def distance_to_segment(
    x: float, y: float, x1: float, y1: float, x2: float, y2: float
) -> float:
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(x - x1, y - y1)
    position = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - (x1 + position * dx), y - (y1 + position * dy))


def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    payload = chunk_type + data
    return struct.pack(">I", len(data)) + payload + struct.pack(">I", binascii.crc32(payload))


def generate_icon(path: Path) -> None:
    center = SIZE / 2
    segments: list[tuple[float, float, float, float]] = []
    for angle_degrees in (0, 60, 120):
        angle = math.radians(angle_degrees)
        dx, dy = math.cos(angle) * 43, math.sin(angle) * 43
        segments.append((center - dx, center - dy, center + dx, center + dy))

    rows = bytearray()
    for y in range(SIZE):
        rows.append(0)
        for x in range(SIZE):
            color = FOREGROUND if any(
                distance_to_segment(x + 0.5, y + 0.5, *segment) <= 4.0
                for segment in segments
            ) else BACKGROUND
            rows.extend(color)

    header = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", header)
        + png_chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + png_chunk(b"IEND", b"")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


if __name__ == "__main__":
    generate_icon(Path(__file__).resolve().parents[1] / "connector" / "icon.png")
