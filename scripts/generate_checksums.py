#!/usr/bin/env python3
"""Generate SHA-256 checksums for repository release-critical files."""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data/checksums/SHA256SUMS.txt"
EXCLUDED_DIRS = {".git", ".venv", "artifacts", "dist", "__pycache__", ".pytest_cache"}
EXCLUDED_FILES = {OUTPUT.resolve()}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def included(path: Path) -> bool:
    if path.resolve() in EXCLUDED_FILES:
        return False
    relative = path.relative_to(ROOT)
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return False
    return path.is_file()


def main() -> None:
    files = sorted(path for path in ROOT.rglob("*") if included(path))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}" for path in files]
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(lines)} checksums to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
