# Results

## Frozen median table

| Metric | Control | Web GTM-style | sGTM proxy-only | sGTM consolidated |
|---|---:|---:|---:|---:|
| Browser requests | 2 | 11 | 11 | 4 |
| Total transfer | 230,292 B | 374,533 B | 374,603 B | 247,280 B |
| JavaScript requests | 0 | 5 | 5 | 1 |
| JavaScript transfer | 0 B | 143,648 B | 143,703 B | 16,769 B |
| LCP | 1,480 ms | 2,232 ms | 2,236 ms | 1,576 ms |
| Load event | 1,470.5 ms | 2,222.4 ms | 2,222.5 ms | 1,567.2 ms |
| Long tasks | 0 | 4 | 4 | 0 |
| Long-task duration | 0 ms | 453 ms | 465 ms | 0 ms |
| TBT | 0 ms | 253 ms | 265 ms | 0 ms |
| Browser event requests | 0 | 4 | 4 | 1 |
| Logical destination deliveries | 0 | 4 | 4 | 4 |

## Proxy-only comparison

Relative to the web GTM-style median:

- browser request count: `0.0%` change;
- JavaScript transfer: `+0.038%`;
- LCP: `+0.179%`;
- load event: `+0.0045%`;
- long-task duration: `+2.65%`;
- TBT: `+4.74%`.

The small timing differences are ordinary run-to-run variation in this fixture. The architecture retained the same five JavaScript resources and four browser event requests, so no browser-side performance mechanism was removed.

## Consolidated comparison

Relative to the web GTM-style median:

- browser request count: `-63.64%`;
- JavaScript transfer: `-88.33%`;
- LCP: `-29.39%`;
- load event: `-29.48%`;
- long-task duration: `-100%`;
- TBT: `-100%`.

The consolidated variant retained four logical destination deliveries with one browser event request. The transferable conclusion is that performance improved when browser code and requests were removed, not merely when the endpoint changed.

## Interpretation boundary

These results do not forecast a 29.4% LCP improvement for an arbitrary production site. Real sites differ in vendor code, tag order, cache state, consent state, device mix, page composition, network conditions, and browser behavior.
