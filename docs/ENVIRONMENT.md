# Environment

## Environment known from the original source package

The preserved runner and README establish the following profile for the 31 July 2026 dataset:

- headless Chromium launched from `/usr/bin/chromium`;
- 1365 × 900 viewport;
- cache disabled;
- 150 ms network latency;
- 1.6 Mbps download and 750 Kbps upload;
- 4× CPU slowdown;
- 15 randomized runs per variant.

## Environment not captured in the original dataset

The original package did not embed:

- exact operating-system image or kernel;
- exact machine or virtual-machine type;
- exact Python version;
- exact Playwright version;
- exact Chromium build;
- exact `aiohttp` and Pillow versions.

Those values must therefore be treated as unknown for the frozen `v1.0.0` run. The repository does not infer them from a later validation environment.

## Package-validation environment

`data/manifest/package-validation-environment.json` records the environment in which this repository package was assembled and validated on 4 August 2026. It is included for maintenance transparency and is **not** presented as proof of the original benchmark environment.

## Future runs

The maintained runner writes:

- `run_environment.json` with runtime, platform, dependency, and browser versions;
- `run_manifest.json` with the command profile, fixture hash, timestamps, and output hashes.

A future official release should also identify the hardware or CI runner type and, where feasible, preserve a container digest rather than only an image tag.
