# Release checklist

## Data and code

- [ ] Raw row count and per-variant counts are correct.
- [ ] Summary JSON recalculates from raw JSON.
- [ ] CSV medians match summary JSON.
- [ ] Schemas validate all machine-readable files.
- [ ] Unit tests pass.
- [ ] A smoke browser run succeeds.
- [ ] Frozen data has not been silently replaced.

## Provenance

- [ ] Benchmark date, package date, release version, and article URL are correct.
- [ ] Exact runtime and browser versions are recorded for new runs.
- [ ] Fixture and output hashes are recorded.
- [ ] Filter-list audits include source URL, date, and exact commit/hash or an explicit limitation.
- [ ] No real IDs, secrets, user data, production endpoints, or customer hostnames are present.

## Documentation

- [ ] README result table matches the processed dataset.
- [ ] Evidence matrix separates measured, documented, audited, inferred, and untested claims.
- [ ] Limitations are prominent.
- [ ] Citation and licenses are correct.
- [ ] Article and repository link to each other.

## GitHub

- [ ] CI passes on `main`.
- [ ] Tag is annotated or signed.
- [ ] Release assets and checksums are attached.
- [ ] Release is made immutable only after assets are verified.
- [ ] Article links to the exact release tag.
