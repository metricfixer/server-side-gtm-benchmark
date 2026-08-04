# Data dictionary

## Raw dataset structure

`data/raw/benchmark_raw.json` is an array of 60 run objects.

| Field | Type | Meaning |
|---|---|---|
| `variant` | string | One of `control`, `web_gtm`, `sgtm_proxy_only`, `sgtm_consolidated` |
| `iteration` | integer | Round number from 1 to 15 within the variant |
| `rid` | string | Local technical run ID; not a user identifier |
| `wall_ms` | number | Wall-clock duration of navigation, settling, and interaction check |
| `dcl` | number/null | DOMContentLoaded end timing in ms |
| `load` | number/null | Load event end timing in ms |
| `responseEnd` | number/null | Main-document response end timing in ms |
| `lcp` | number/null | Observed LCP timing in ms |
| `cls` | number | Cumulative layout shift observed by the fixture |
| `longTaskCount` | integer | Number of long tasks |
| `longTaskDuration` | number | Sum of long-task durations in ms |
| `tbt` | number | Sum of blocking time over the 50 ms long-task threshold |
| `interactionDelay` | number/null | Click-to-next-frame sanity-check delay in ms |
| `errors` | array | Browser error strings captured by the fixture |
| `resourceEntries` | array | Browser resource timing entries retained for inspection |
| `request_count` | integer | Local CDP request count |
| `failed_request_count` | integer | Failed local requests |
| `transfer_bytes` | integer | Sum of encoded transfer length |
| `js_request_count` | integer | JavaScript resource request count |
| `js_transfer_bytes` | integer | JavaScript encoded transfer total |
| `browser_event_request_count_cdp` | integer | Event requests observed by CDP |
| `server_browser_event_requests` | integer | Event requests received by the local server |
| `logical_destination_deliveries` | integer | Synthetic downstream deliveries counted by the server |
| `server_event_paths` | array | Local event paths received for the run |

## Summary dataset

`data/processed/benchmark_summary.json` contains:

- `runs_per_variant`;
- one summary object per variant;
- `n` rows per variant;
- `median`, `p75`, `min`, and `max` for each numeric field;
- aggregated browser errors and failed requests;
- percentage comparisons of proxy-only and consolidated variants against `web_gtm`.

## CSV dataset

`data/processed/benchmark_medians.csv` is a compact publication-oriented table. Byte values remain bytes and timing values remain milliseconds; display formatting into KB is performed in documentation, not stored in the CSV.
