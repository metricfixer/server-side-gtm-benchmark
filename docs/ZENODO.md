# Optional Zenodo archiving

After the GitHub repository and `v1.0.0` release are public, Metricfixer can connect the repository to Zenodo and archive the release to obtain a DOI.

Before enabling the integration:

1. Confirm that the GitHub release assets and SHA-256 checksums are final.
2. Review `.zenodo.json` and `CITATION.cff`.
3. Confirm the companion article URL.
4. Verify the code/data license split and third-party exclusions.
5. Publish the GitHub release before triggering Zenodo archival.

A DOI is useful for stable citation and preservation. It should not be described as proof that every article claim was experimentally measured; the evidence matrix and limitations still apply.
