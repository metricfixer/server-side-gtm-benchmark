# GitHub repository setup

## Repository identity

- Organization: `metricfixer`
- Repository: `server-side-gtm-benchmark`
- Visibility: public
- Default branch: `main`
- Description: `Reproducible web GTM vs server-side GTM benchmark with raw data, a Playwright runner, performance metrics, methodology, and documented limitations.`
- Website: `https://metricfixer.com/publications/analytics-conversion-tracking/server-side-gtm-real-gains-marketing-myths-benchmark`

## Topics

`server-side-gtm`, `sgtm`, `google-tag-manager`, `web-gtm`, `server-side-tagging`, `web-analytics`, `conversion-tracking`, `web-performance`, `core-web-vitals`, `playwright`, `benchmark`, `consent-mode`

## First publication sequence

```bash
git init
git branch -M main
git add .
git commit -m "Publish Metricfixer web GTM vs sGTM benchmark v1.0.0"
git remote add origin https://github.com/metricfixerSupportServices/server-side-gtm-benchmark.git
git push -u origin main
```

Then create an annotated or signed tag:

```bash
git tag -a v1.0.0 -m "Metricfixer web GTM vs sGTM benchmark v1.0.0"
git push origin v1.0.0
```

The included release workflow can build assets when the tag is pushed. Review the draft/release output before linking it from the article.

## Recommended settings

- Enable issues and private vulnerability reporting.
- Disable wiki and projects unless they will be maintained.
- Protect `main`: require pull requests, status checks, resolved conversations, and block force pushes/deletion.
- Require the `Validate baseline data` check. Require `Smoke benchmark` only after confirming the workflow cost and stability are acceptable.
- Enable Dependabot for Python and GitHub Actions.
- Enable immutable releases after the first asset set is verified.
- Create a `maintainers` team before activating `.github/CODEOWNERS.example`.

## About section

Use the description, website, and topics above. Upload `assets/social-preview.png` as the repository social preview.

## Release assets

Attach:

- `server-side-gtm-benchmark-v1.0.0.zip`;
- `server-side-gtm-benchmark-data-v1.0.0.zip`;
- `SHA256SUMS.txt`.

Link the article to the release tag, not to a mutable `main.zip` archive.
