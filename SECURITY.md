# Security policy

## Supported versions

Only the latest repository release receives security-related maintenance. The frozen benchmark data remains available for provenance, but executable tooling may be updated in a new patch release.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting feature for this repository. Do not open a public issue for a vulnerability that could expose secrets, enable arbitrary code execution, or compromise a benchmark runner.

## Repository safety rules

- The benchmark must bind only to `127.0.0.1` by default.
- No production analytics, advertising, CRM, payment, or customer endpoints are called.
- No real identifiers, cookies, credentials, service-account files, API keys, or personal data belong in this repository.
- Pull requests that add network calls must document every destination and remain disabled by default.
- Release assets must be accompanied by SHA-256 checksums.
