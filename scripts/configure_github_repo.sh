#!/usr/bin/env bash
set -euo pipefail

ORG="${1:-metricfixer}"
REPO="${2:-server-side-gtm-benchmark}"
ARTICLE_URL="${3:-https://metricfixer.com/publications/analytics-conversion-tracking/server-side-gtm-real-gains-marketing-myths-benchmark}"
TARGET="$ORG/$REPO"
DESCRIPTION="Reproducible web GTM vs server-side GTM benchmark with raw data, a Playwright runner, performance metrics, methodology, and documented limitations."

gh repo edit "$TARGET" \
  --description "$DESCRIPTION" \
  --homepage "$ARTICLE_URL" \
  --enable-issues \
  --enable-wiki=false \
  --enable-projects=false

for topic in \
  server-side-gtm sgtm google-tag-manager web-gtm server-side-tagging \
  web-analytics conversion-tracking web-performance core-web-vitals \
  playwright benchmark consent-mode
do
  gh repo edit "$TARGET" --add-topic "$topic"
done

echo "Configured $TARGET. Apply branch protection and release immutability in repository settings."
