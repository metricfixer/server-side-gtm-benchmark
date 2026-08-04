# Recommended future experiments

The following studies would extend the evidence without pretending that the synthetic browser benchmark already measured them.

## Blocker matrix

Test named browser/extension/filter-list versions against:

- vendor-hosted collection;
- first-party subdomain;
- same-origin path;
- recognizable and randomized paths;
- dependency serving enabled/disabled.

Retain exact extension versions, enabled lists, list commit hashes, request logs, and user-agent/browser versions.

## Safari and storage matrix

Test JavaScript-set cookies, HTTP response cookies, same-origin paths, first-party subdomains, CNAME-cloaked services, link decoration, private browsing, and storage deletion across named Safari/WebKit versions. Avoid claiming permanent cookie life.

## Consent and opt-out matrix

Use a real CMP and document default consent, update timing, region rules, Basic/Advanced Consent Mode, server-container enforcement, destination behavior, and Google Analytics opt-out. Confirm that denied states do not get routed around.

## Conversion-reconciliation study

For a consenting test environment, reconcile browser events, backend orders, sGTM receives, destination accepts, and destination reports. Measure missing, duplicate, malformed, unattributed, and delayed events by browser and acquisition source.

## Infrastructure cost benchmark

Measure requests, CPU, memory, cold starts, concurrency, egress, logs, observability, and operator time at defined traffic volumes. Publish cost per million accepted events and cost per reconciled incremental business event.
