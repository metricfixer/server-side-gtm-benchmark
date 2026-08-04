#!/usr/bin/env python3
"""Build deterministic full and data-only release ZIP files."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DIST = ROOT / "dist"
FIXED_TIME = (2026, 8, 4, 0, 0, 0)
EXCLUDED_PARTS = {".git", ".venv", "artifacts", "dist", "__pycache__", ".pytest_cache"}

DATA_PREFIXES = (
    "data/",
    "audits/",
    "fixtures/",
)
DATA_FILES = {
    "README.md",
    "ARTICLE_REFERENCE.md",
    "article-reference.json",
    "CITATION.cff",
    "DATA_STATEMENT.md",
    "LICENSE-DATA.md",
    "docs/METHODOLOGY.md",
    "docs/ENVIRONMENT.md",
    "docs/METRICS.md",
    "docs/RESULTS.md",
    "docs/EVIDENCE_MATRIX.md",
    "docs/LIMITATIONS.md",
    "docs/REPRODUCIBILITY.md",
    "docs/DATA_DICTIONARY.md",
    "docs/REFERENCES.md",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest


def iter_full_files() -> list[Path]:
    files=[]
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative=path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        files.append(path)
    return sorted(files)


def iter_data_files() -> list[Path]:
    selected=[]
    for path in iter_full_files():
        relative=path.relative_to(ROOT).as_posix()
        if relative == "data/checksums/SHA256SUMS.txt":
            continue
        if relative in DATA_FILES or relative.startswith(DATA_PREFIXES):
            selected.append(path)
    return selected


def write_zip(path: Path, files: list[Path], folder_name: str, include_internal_checksums: bool = False) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in files:
            relative=source.relative_to(ROOT).as_posix()
            info=zipfile.ZipInfo(f"{folder_name}/{relative}", date_time=FIXED_TIME)
            info.compress_type=zipfile.ZIP_DEFLATED
            mode=0o755 if source.suffix in {".sh"} or source.name.endswith(".py") else 0o644
            info.external_attr=(mode & 0xFFFF) << 16
            archive.writestr(info, source.read_bytes())
        if include_internal_checksums:
            checksum_lines = [
                f"{sha256(source)}  {source.relative_to(ROOT).as_posix()}"
                for source in files
            ]
            info=zipfile.ZipInfo(f"{folder_name}/SHA256SUMS.txt", date_time=FIXED_TIME)
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o644 & 0xFFFF) << 16
            archive.writestr(info, ("\n".join(checksum_lines) + "\n").encode("utf-8"))


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts/generate_checksums.py")], check=True)
    DIST.mkdir(parents=True, exist_ok=True)
    full_path=DIST / f"server-side-gtm-benchmark-v{VERSION}.zip"
    data_path=DIST / f"server-side-gtm-benchmark-data-v{VERSION}.zip"
    write_zip(full_path, iter_full_files(), f"server-side-gtm-benchmark-{VERSION}")
    write_zip(data_path, iter_data_files(), f"server-side-gtm-benchmark-data-{VERSION}", include_internal_checksums=True)
    sums=DIST / "SHA256SUMS.txt"
    sums.write_text(
        f"{sha256(full_path)}  {full_path.name}\n{sha256(data_path)}  {data_path.name}\n",
        encoding="utf-8",
    )
    print(f"Built {full_path.name}")
    print(f"Built {data_path.name}")
    print(f"Wrote {sums.name}")


if __name__ == "__main__":
    main()
