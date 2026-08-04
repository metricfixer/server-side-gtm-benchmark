# Linking the Metricfixer article and repository

## From the article to GitHub

Place the block after the benchmark result table or at the end of the methodology section:

```html
<div class="article-context-note">
<p><strong>Reproducibility package:</strong> the benchmark source code, raw data, processed results, environment notes, and interpretation limits are available in the public Metricfixer repository.</p>
<p><a href="https://github.com/metricfixerSupportServices/server-side-gtm-benchmark" rel="nofollow noopener" target="_blank">Review the benchmark methodology and source code on GitHub</a>.</p>
<p><a href="https://github.com/metricfixerSupportServices/server-side-gtm-benchmark/releases/tag/v1.0.0" rel="nofollow noopener" target="_blank">Download the exact benchmark release used for this article</a>.</p>
</div>
```

The same block is available in `snippets/article-repository-block.html`.

## From GitHub to the article

The canonical article link appears near the top of `README.md`, in `ARTICLE_REFERENCE.md`, `article-reference.json`, `CITATION.cff`, and release notes. Do not copy the full article into the repository.

## URL changes

Run:

```bash
python scripts/update_repository_metadata.py \
  --article-url "https://metricfixer.com/final-path" \
  --repository-url "https://github.com/metricfixerSupportServices/server-side-gtm-benchmark"
```

Review the diff before committing.
