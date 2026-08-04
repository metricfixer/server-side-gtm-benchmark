# Methodology

## Research question

The benchmark asks a narrow architecture question: what browser-side changes occur when a conventional browser-heavy measurement setup is replaced by either a proxy-only server-side endpoint or a genuinely consolidated server-side event flow?

It does not attempt to reproduce the complete behavior of any specific analytics or advertising SDK.

## Fixture

Every run uses the same editorial-style landing page, CSS, hero image, content cards, and interaction target. The only changed variable is the synthetic measurement architecture.

The deterministic JPEG in `fixtures/benchmark_hero_fixture.jpg` is the page's primary LCP resource. It is not a publication hero image.

## Variants

| Variant | Browser behavior | Server behavior | Purpose |
|---|---|---|---|
| `control` | No measurement JavaScript | No event delivery | Establish page baseline |
| `web_gtm` | One container, four vendor bundles, four direct event requests | Four logical receives | Represent a browser-heavy multi-destination setup |
| `sgtm_proxy_only` | Same container, same four bundles, same four event requests, different first-hop path | Four forwarded receives | Test whether changing only the endpoint removes browser work |
| `sgtm_consolidated` | One small dispatcher and one first-party request | Four logical downstream deliveries | Test the architecture in which browser work is actually consolidated |

The JavaScript payloads are deterministic synthetic strings plus CPU loops. They represent relative architecture cost, not the exact size or behavior of Google, Meta, affiliate, CRM, or other vendor code.

## Test profile

- 15 cold loads per variant; 60 successful runs total.
- Variant order randomized within each round using seed `10000 + iteration`.
- Headless Chromium.
- Viewport: 1365 × 900 CSS pixels.
- Device scale factor: 1.
- Cache disabled through the Chrome DevTools Protocol.
- Network latency: 150 ms.
- Download throughput: 1.6 Mbps.
- Upload throughput: 750 Kbps.
- CPU slowdown: 4×.
- A 2.2-second post-load settling period before the interaction check.

## Metrics

The runner captures navigation timing, LCP, CLS, long tasks, synthetic TBT, interaction sanity-check delay, CDP request counts and encoded transfer, JavaScript request counts and transfer, browser event requests observed by the local server, and logical destination deliveries.

See `docs/METRICS.md` for definitions and caveats.

## Statistical reporting

The publication reports medians because a single fastest run is not representative. The processed JSON also preserves P75, minimum, and maximum. No hypothesis test or confidence interval is claimed in `v1.0.0`; the benchmark is a controlled architecture comparison, not a population estimate.

## Output provenance

The frozen raw output is in `data/raw/benchmark_raw.json`. Processed results are in `data/processed/`. The original unmodified runner from the source bundle is retained at `docs/original-runner-v1.0.0.py`. The maintained runner adds portability and environment recording for future runs.

## What the method can establish

It can establish that, in this fixture:

- the proxy-only variant retained the same browser libraries and event-request count as the web GTM-style variant;
- the consolidated variant removed browser requests, JavaScript transfer, and synthetic main-thread work while preserving four logical deliveries;
- architecture changes, rather than the label “server-side,” produced the measured browser effect.

## What the method cannot establish

It cannot establish a universal Core Web Vitals uplift, conversion recovery rate, blocker bypass rate, cookie lifetime, attribution improvement, consent compliance, vendor feature parity, or production infrastructure cost. Those require separate experiments and site-specific validation.
