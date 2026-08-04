#!/usr/bin/env python3
"""Verify the repository checksum manifest."""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/checksums/SHA256SUMS.txt"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if not MANIFEST.is_file():
        raise SystemExit(f"Missing checksum manifest: {MANIFEST}")
    checked = 0
    failures: list[str] = []
    for line_number, raw_line in enumerate(MANIFEST.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            expected, relative = line.split("  ", 1)
        except ValueError:
            failures.append(f"Line {line_number}: invalid format")
            continue
        path = ROOT / relative
        if not path.is_file():
            failures.append(f"Missing: {relative}")
            continue
        actual = sha256(path)
        checked += 1
        if actual != expected:
            failures.append(f"Mismatch: {relative}: {actual} != {expected}")
    if failures:
        raise SystemExit("Checksum verification failed:\n" + "\n".join(f"- {item}" for item in failures))
    print(f"Verified {checked} repository file checksums.")


if __name__ == "__main__":
    main()
