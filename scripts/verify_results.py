#!/usr/bin/env python3
"""Validate the frozen benchmark dataset against source data and schemas."""

from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from benchmark_core import VARIANTS, sha256_file, summarize  # noqa: E402


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def compare(actual: Any, expected: Any, path: str = "root") -> None:
    if isinstance(actual, dict) and isinstance(expected, dict):
        if set(actual) != set(expected):
            raise AssertionError(f"{path}: key mismatch: {set(actual) ^ set(expected)}")
        for key in actual:
            compare(actual[key], expected[key], f"{path}.{key}")
        return
    if isinstance(actual, list) and isinstance(expected, list):
        if len(actual) != len(expected):
            raise AssertionError(f"{path}: length {len(actual)} != {len(expected)}")
        for index, (left, right) in enumerate(zip(actual, expected)):
            compare(left, right, f"{path}[{index}]")
        return
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        if not math.isclose(float(actual), float(expected), rel_tol=1e-12, abs_tol=1e-9):
            raise AssertionError(f"{path}: {actual!r} != {expected!r}")
        return
    if actual != expected:
        raise AssertionError(f"{path}: {actual!r} != {expected!r}")


def validate_schemas(raw: Any, summary: Any, manifest: Any, article_reference: Any) -> None:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError as exc:
        raise SystemExit("jsonschema is required; install requirements.lock.txt") from exc

    checks = [
        (raw, ROOT / "data/schema/benchmark-raw.schema.json"),
        (summary, ROOT / "data/schema/benchmark-summary.schema.json"),
        (manifest, ROOT / "data/schema/benchmark-manifest.schema.json"),
        (article_reference, ROOT / "data/schema/article-reference.schema.json"),
    ]
    for instance, schema_path in checks:
        schema = load_json(schema_path)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
        if errors:
            detail = "\n".join(f"- {list(error.path)}: {error.message}" for error in errors)
            raise AssertionError(f"Schema validation failed for {schema_path}:\n{detail}")


def validate_csv(summary: dict[str, Any]) -> None:
    path = ROOT / "data/processed/benchmark_medians.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    fields = {
        "Browser requests": "request_count",
        "Total transfer": "transfer_bytes",
        "JavaScript requests": "js_request_count",
        "JavaScript transfer": "js_transfer_bytes",
        "Largest Contentful Paint": "lcp",
        "Load event": "load",
        "Long tasks": "longTaskCount",
        "Long-task duration": "longTaskDuration",
        "Total Blocking Time": "tbt",
        "Browser event requests": "server_browser_event_requests",
        "Logical destination deliveries": "logical_destination_deliveries",
    }
    if len(rows) != len(fields):
        raise AssertionError(f"CSV row count {len(rows)} != {len(fields)}")
    for row in rows:
        field = fields[row["metric"]]
        for variant in VARIANTS:
            expected = float(summary["variants"][variant][field]["median"])
            actual = float(row[variant])
            if not math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-9):
                raise AssertionError(f"CSV mismatch for {row['metric']} / {variant}: {actual} != {expected}")


def main() -> None:
    raw_path = ROOT / "data/raw/benchmark_raw.json"
    summary_path = ROOT / "data/processed/benchmark_summary.json"
    manifest_path = ROOT / "data/manifest/benchmark-manifest.json"
    article_path = ROOT / "article-reference.json"

    raw = load_json(raw_path)
    summary = load_json(summary_path)
    manifest = load_json(manifest_path)
    article_reference = load_json(article_path)

    if len(raw) != 60:
        raise AssertionError(f"Expected 60 raw runs, found {len(raw)}")
    counts = Counter(row["variant"] for row in raw)
    if counts != Counter({variant: 15 for variant in VARIANTS}):
        raise AssertionError(f"Unexpected variant counts: {counts}")
    for variant in VARIANTS:
        iterations = sorted(row["iteration"] for row in raw if row["variant"] == variant)
        if iterations != list(range(1, 16)):
            raise AssertionError(f"Unexpected iterations for {variant}: {iterations}")
    if any(row.get("errors") for row in raw):
        raise AssertionError("At least one raw run contains a browser error")
    if any(row.get("failed_request_count", 0) for row in raw):
        raise AssertionError("At least one raw run contains a failed local request")

    recalculated = summarize(raw, runs_per_variant=15)
    compare(recalculated, summary, "summary")
    validate_csv(summary)
    validate_schemas(raw, summary, manifest, article_reference)

    for relative, expected_hash in manifest["frozen_files"].items():
        actual_hash = sha256_file(ROOT / relative)
        if actual_hash != expected_hash:
            raise AssertionError(f"Frozen file hash mismatch for {relative}: {actual_hash} != {expected_hash}")
    fixture = manifest["fixture"]
    if sha256_file(ROOT / fixture["path"]) != fixture["sha256"]:
        raise AssertionError("Fixture hash does not match manifest")

    article_url = article_reference["canonical_url"]
    for relative in ["README.md", "ARTICLE_REFERENCE.md", "CITATION.cff"]:
        if article_url not in (ROOT / relative).read_text(encoding="utf-8"):
            raise AssertionError(f"Canonical article URL missing from {relative}")

    print("Validated 60 raw runs, processed summaries, CSV medians, schemas, provenance hashes, and article references.")


if __name__ == "__main__":
    main()
