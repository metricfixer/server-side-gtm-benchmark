# v1.0.0 — Initial Metricfixer Web GTM vs sGTM benchmark

This release contains the frozen dataset and reproducibility materials used by the Metricfixer publication **Server-Side GTM Benchmarked: What It Really Improves—and What It Does Not**.

## Included

- 60 raw cold-load runs: 15 per architecture variant.
- Processed medians, P75, minimums, maximums, and comparisons.
- Portable Playwright runner for future reruns.
- Original runner retained for provenance.
- JSON Schemas, checksums, tests, Dockerfile, and CI workflows.
- Methodology, metrics, evidence matrix, limitations, data dictionary, and dated filter-list audit.

## Main measured result

The proxy-only design retained the same browser JavaScript and event-request count as the web GTM-style design. The consolidated design reduced browser requests and JavaScript transfer while preserving four logical downstream deliveries in the local synthetic model.

## Important limitation

The source package did not embed the exact runtime, browser, operating-system, or machine versions used on 31 July 2026. The frozen dataset is preserved as published; every future run records those values automatically.
