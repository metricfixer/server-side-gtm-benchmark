# Limitations

## Synthetic vendor code

The browser bundles are deterministic synthetic payloads. They do not reproduce the exact bundle size, execution model, cookies, storage, network endpoints, consent behavior, retries, or feature set of any production analytics or advertising SDK.

## Single fixture and profile

The benchmark uses one landing page, one viewport, one CPU throttle, one network profile, cold cache, and headless Chromium. Absolute timings and relative effects can change on another page, browser, machine, network, or cache state.

## No field Core Web Vitals

Laboratory LCP and synthetic TBT are useful for detecting architecture differences. They are not a substitute for Real User Monitoring segmented by device, browser, geography, consent state, page template, and user behavior.

## No live destination acceptance

“Logical destination deliveries” are local counters. The benchmark does not prove that a production vendor would accept, deduplicate, attribute, model, or report the event.

## No production conversion-recovery test

The release does not estimate how many real conversions sGTM recovers. Recovery depends on the original loss point, event source, blockers, consent, backend data, identity, retries, destination rules, and reconciliation.

## No Safari/ITP lab matrix

Cookie and Safari sections in the companion article rely on browser documentation and architecture analysis. The release does not contain a multi-version Safari experiment.

## No CMP or Consent Mode experiment

The release does not run a real CMP, regional consent policy, Basic/Advanced Consent Mode matrix, or destination-level enforcement audit.

## Filter-list snapshot provenance

The original audit recorded the source URLs, date, counts, and interpretation, but not the exact upstream commit hashes or archived list files. The audit is useful as dated evidence that first-party and sGTM-specific blocking rules existed; it is not a bit-for-bit reproducible filter snapshot.

## Original environment gap

Exact runtime and browser versions for the frozen 31 July 2026 dataset were not embedded in the original raw files. Future runner output corrects this, but later environment metadata cannot be retroactively assigned to the original run.

## Infrastructure cost

No production load, autoscaling, egress, logging, observability, managed-provider, or staffing cost benchmark is included.
