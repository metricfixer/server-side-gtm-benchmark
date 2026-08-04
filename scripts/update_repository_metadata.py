#!/usr/bin/env python3
"""Replace repository and article URLs across text metadata files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/repository.json"
TEXT_SUFFIXES = {".md", ".json", ".yml", ".yaml", ".html", ".cff", ".toml", ".txt"}
EXCLUDED_DIRS = {".git", ".venv", "dist", "artifacts", "__pycache__"}


def parse_args() -> argparse.Namespace:
    parser=argparse.ArgumentParser()
    parser.add_argument("--article-url", required=True)
    parser.add_argument("--repository-url", required=True)
    return parser.parse_args()


def main() -> None:
    args=parse_args()
    config=json.loads(CONFIG.read_text(encoding="utf-8"))
    old_article=config["article_url"]
    old_repo=config["repository_url"]
    old_release=config["release_url"]
    new_release=args.repository_url.rstrip("/") + "/releases/tag/" + config["release"]

    changed=[]
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        relative=path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        text=path.read_text(encoding="utf-8")
        updated=text.replace(old_release,new_release).replace(old_article,args.article_url).replace(old_repo,args.repository_url)
        if updated != text:
            path.write_text(updated,encoding="utf-8")
            changed.append(relative.as_posix())

    config=json.loads(CONFIG.read_text(encoding="utf-8"))
    config["article_url"]=args.article_url
    config["repository_url"]=args.repository_url
    config["release_url"]=new_release
    CONFIG.write_text(json.dumps(config,indent=2)+"\n",encoding="utf-8")
    print("Updated:")
    for relative in changed:
        print(f"- {relative}")
    print("Regenerate checksums before release.")


if __name__ == "__main__":
    main()
