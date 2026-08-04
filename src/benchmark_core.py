"""Shared summary and file helpers for the Metricfixer sGTM benchmark."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any, Mapping, Sequence

VARIANTS = ["control", "web_gtm", "sgtm_proxy_only", "sgtm_consolidated"]
NUMERIC_FIELDS = [
    "dcl",
    "load",
    "responseEnd",
    "lcp",
    "cls",
    "longTaskCount",
    "longTaskDuration",
    "tbt",
    "interactionDelay",
    "wall_ms",
    "request_count",
    "transfer_bytes",
    "js_request_count",
    "js_transfer_bytes",
    "server_browser_event_requests",
    "logical_destination_deliveries",
]
CSV_METRICS = [
    ("Browser requests", "", "request_count"),
    ("Total transfer", "bytes", "transfer_bytes"),
    ("JavaScript requests", "", "js_request_count"),
    ("JavaScript transfer", "bytes", "js_transfer_bytes"),
    ("Largest Contentful Paint", "ms", "lcp"),
    ("Load event", "ms", "load"),
    ("Long tasks", "", "longTaskCount"),
    ("Long-task duration", "ms", "longTaskDuration"),
    ("Total Blocking Time", "ms", "tbt"),
    ("Browser event requests", "", "server_browser_event_requests"),
    ("Logical destination deliveries", "", "logical_destination_deliveries"),
]


def percentile(values: Sequence[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[int(position)]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def summarize(results: Sequence[Mapping[str, Any]], runs_per_variant: int | None = None) -> dict[str, Any]:
    if runs_per_variant is None:
        counts = [sum(1 for row in results if row.get("variant") == variant) for variant in VARIANTS]
        runs_per_variant = min(counts) if counts else 0

    output: dict[str, Any] = {"runs_per_variant": int(runs_per_variant), "variants": {}}
    for variant in VARIANTS:
        rows = [row for row in results if row.get("variant") == variant]
        variant_summary: dict[str, Any] = {"n": len(rows)}
        for field in NUMERIC_FIELDS:
            values = [float(row[field]) for row in rows if row.get(field) is not None]
            variant_summary[field] = {
                "median": statistics.median(values) if values else None,
                "p75": percentile(values, 0.75) if values else None,
                "min": min(values) if values else None,
                "max": max(values) if values else None,
            }
        variant_summary["errors"] = sum(len(row.get("errors", [])) for row in rows)
        variant_summary["failed_requests"] = sum(int(row.get("failed_request_count", 0)) for row in rows)
        output["variants"][variant] = variant_summary

    base = output["variants"]["web_gtm"]
    consolidated = output["variants"]["sgtm_consolidated"]
    proxy = output["variants"]["sgtm_proxy_only"]
    comparisons: dict[str, Any] = {}
    for field in ["request_count", "js_transfer_bytes", "lcp", "load", "longTaskDuration", "tbt"]:
        base_value = base[field]["median"]
        consolidated_value = consolidated[field]["median"]
        proxy_value = proxy[field]["median"]
        comparisons[field] = {
            "consolidated_vs_web_pct": (
                (consolidated_value - base_value) / base_value * 100 if base_value else None
            ),
            "proxy_vs_web_pct": (proxy_value - base_value) / base_value * 100 if base_value else None,
        }
    output["comparisons"] = comparisons
    return output


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_medians_csv(path: Path, summary: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["metric", "unit", *VARIANTS])
        for label, unit, field in CSV_METRICS:
            writer.writerow(
                [label, unit, *[summary["variants"][variant][field]["median"] for variant in VARIANTS]]
            )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
