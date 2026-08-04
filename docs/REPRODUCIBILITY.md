# Reproducibility guide

## Validate the published files without running a browser

```bash
python -m pip install -r requirements.lock.txt
python scripts/verify_results.py
python scripts/verify_checksums.py
python -m unittest discover -s tests -v
```

This confirms that:

- all 60 raw rows are present;
- each variant has 15 rows;
- processed medians, P75, minimums, maximums, and comparisons recalculate from the raw data;
- the CSV medians agree with the JSON summary;
- JSON files satisfy the repository schemas;
- frozen-file checksums match.

## Run a smoke benchmark

```bash
python -m playwright install chromium
python src/run_benchmark.py --runs-per-variant 1 --output-dir artifacts/smoke
```

A smoke run verifies that the local server, browser automation, timing observers, request capture, and output generation work. It is not expected to numerically match a 15-run median.

## Run the full profile

```bash
python src/run_benchmark.py --output-dir artifacts/full-run
```

The runner writes raw data, summary JSON, medians CSV, runtime environment, and a run manifest.

## Compare runs responsibly

Compare architecture direction before comparing exact milliseconds. Browser engines, virtualized CPU scheduling, host load, Playwright versions, and network emulation implementation can change absolute values.

A rerun should be published as a new release when any of these change:

- browser or Playwright version;
- fixture or synthetic payload;
- CPU/network profile;
- run count or randomization;
- metric collection or summarization;
- variant definitions.

## Docker baseline

The Dockerfile provides a pinned Playwright image tag for future reruns. For archival-grade reproducibility, record the image digest in the new release manifest because tags can be republished or removed upstream.

## Frozen v1.0.0 provenance

The unmodified original runner is retained in `docs/original-runner-v1.0.0.py`. The maintained runner changes execution portability and metadata capture, not the conceptual four-variant design. The frozen raw data remains separate and is never regenerated in place.
