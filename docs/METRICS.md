# Metric definitions

## Navigation and rendering

### `dcl`

`domContentLoadedEventEnd` from the navigation timing entry, in milliseconds from navigation start.

### `load`

`loadEventEnd` from the navigation timing entry, in milliseconds from navigation start.

### `responseEnd`

Time at which the final response byte for the main document was received.

### `lcp`

The last buffered `largest-contentful-paint` entry observed after the settling period. LCP is laboratory data for this fixture, not field Core Web Vitals data.

### `cls`

Sum of layout-shift values that did not have recent user input. The test fixture is deliberately stable and reported zero in the frozen data.

## Main-thread work

### `longTaskCount`

Number of PerformanceObserver `longtask` entries.

### `longTaskDuration`

Sum of all observed long-task durations.

### `tbt`

Synthetic Total Blocking Time calculated as the sum of `max(0, duration - 50 ms)` for each observed long task. This follows the conventional laboratory concept but is calculated directly by the fixture rather than imported from Lighthouse.

### `interactionDelay`

Delay from the button click timestamp to the next animation frame. It is a sanity check, not a field INP measurement.

## Network and delivery

### `request_count`

Number of local benchmark-server requests observed through CDP. A browser may occasionally request a favicon, which explains why some individual runs can contain one extra request while the median remains stable.

### `transfer_bytes`

Sum of CDP `encodedDataLength` for local benchmark requests. It includes response overhead reported by Chromium and should not be treated as pure payload bytes.

### `js_request_count`

Number of local JavaScript resource requests under `/assets/`.

### `js_transfer_bytes`

Sum of encoded transfer for those JavaScript resources.

### `browser_event_request_count_cdp`

Event-collection requests found in CDP for `/third-party/collect`, `/collect/proxy`, or `/collect/sgtm`.

### `server_browser_event_requests`

Event requests received by the local server. This is the first-hop delivery count used in the publication table.

### `logical_destination_deliveries`

Synthetic destination deliveries recorded by the local server. The consolidated endpoint counts one browser request as four logical fan-out deliveries; no live vendor APIs are called.

## Summary statistics

For each numeric metric, `benchmark_summary.json` stores `median`, `p75`, `min`, and `max`. Percentage comparisons use the web GTM-style median as the denominator.
