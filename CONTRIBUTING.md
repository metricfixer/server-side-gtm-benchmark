# Contributing

Contributions that improve reproducibility, correct documentation, add independently verifiable experiments, or make the runner more portable are welcome.

## Before opening a pull request

1. Open an issue describing the proposed change and whether it affects code, methodology, data, or interpretation.
2. Do not replace or edit the frozen `v1.0.0` raw dataset to make a new run appear identical to the published release.
3. Put new experimental output under a new versioned directory or release.
4. Record the browser, runtime, operating system, hardware or runner type, network profile, CPU throttling, and exact command used.
5. Explain whether the contribution is a synthetic benchmark, live-vendor test, browser-policy review, filter-list audit, or inference.

## Development checks

```bash
python scripts/verify_results.py
python scripts/verify_checksums.py
python -m unittest discover -s tests -v
python -m py_compile src/run_benchmark.py src/benchmark_core.py scripts/*.py
```

For runner changes, also run a smoke benchmark:

```bash
python src/run_benchmark.py --runs-per-variant 1 --output-dir artifacts/smoke
```

## Data contributions

A new dataset must include raw results, a machine-readable environment file, a run manifest, a methodology note, and checksums. Do not submit real user identifiers, cookies, advertising IDs, account IDs, API keys, customer endpoints, or production payloads.

## Editorial standard

Use precise language. Separate direct measurement from platform documentation, inference, and recommendations. Avoid claims such as "sGTM bypasses AdBlock" or "sGTM fixes attribution" unless the exact tested conditions and limits are stated.
