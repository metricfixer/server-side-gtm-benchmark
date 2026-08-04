#!/usr/bin/env python3
"""Check external HTTP links in repository text files."""

from __future__ import annotations

import argparse
import re
import ssl
import urllib.error
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
URL_RE=re.compile(r"https://[^\s<>)\]\"']+")
TEXT_SUFFIXES={".md",".html",".json",".yml",".yaml",".cff",".toml",".txt"}
EXCLUDED={".git",".venv","dist","artifacts","__pycache__"}


def parse_args():
    parser=argparse.ArgumentParser()
    parser.add_argument("--soft-fail",action="store_true")
    parser.add_argument("--output",type=Path)
    parser.add_argument("--timeout",type=float,default=15.0)
    return parser.parse_args()


def collect_urls():
    urls=set()
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        relative=path.relative_to(ROOT)
        if any(part in EXCLUDED for part in relative.parts):
            continue
        for match in URL_RE.findall(path.read_text(encoding="utf-8",errors="ignore")):
            urls.add(match.rstrip(".,;:"))
    return sorted(urls)


def check(url,timeout):
    request=urllib.request.Request(url,headers={"User-Agent":"MetricfixerBenchmarkLinkCheck/1.0"},method="GET")
    try:
        with urllib.request.urlopen(request,timeout=timeout,context=ssl.create_default_context()) as response:
            return response.status, response.geturl(), None
    except urllib.error.HTTPError as exc:
        return exc.code, url, str(exc)
    except Exception as exc:
        return None, url, str(exc)


def main():
    args=parse_args()
    lines=[]; failures=[]
    for url in collect_urls():
        status,final,error=check(url,args.timeout)
        ok=status is not None and status < 400
        line=f"{'OK' if ok else 'FAIL'}\t{status or '-'}\t{url}\t{final}\t{error or ''}"
        lines.append(line)
        print(line)
        if not ok: failures.append(line)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text("\n".join(lines)+"\n",encoding="utf-8")
    if failures and not args.soft_fail:
        raise SystemExit(f"{len(failures)} link checks failed")


if __name__ == "__main__":
    main()
