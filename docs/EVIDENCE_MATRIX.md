# Evidence matrix

This matrix prevents the repository from presenting every article conclusion as if it were directly measured by the same experiment.

| Claim or question | Evidence type in v1.0.0 | Directly reproducible here? | Primary artifact | Boundary |
|---|---|---:|---|---|
| A proxy-only sGTM migration does not remove browser work | Synthetic architecture benchmark | Yes | Raw runs, runner, summary | Applies to the tested architecture, not every possible implementation |
| Consolidating browser libraries and requests can reduce transfer and main-thread work | Synthetic architecture benchmark | Yes | Raw runs, processed results | Exact percentages belong to this fixture |
| One browser event can be represented as four logical server-side deliveries | Synthetic local fan-out model | Yes | Runner and server logs | No live destination acceptance is tested |
| A first-party collection hostname is not automatically unblockable | Dated filter-list review plus architecture analysis | Partly | `audits/filter-list-audit-2026-07-31.md` | Exact filter snapshots/commits were not recorded in the original package |
| sGTM cannot recover an event that neither browser nor backend generated | System-architecture conclusion | Conceptually, not as a numeric lab test | Methodology and article | A backend can independently generate server-known business events |
| Same-origin server-set cookies can avoid the specific WebKit cap on JavaScript-set cookies | Browser documentation review | No browser-policy lab in v1.0.0 | References | Does not mean cookies are permanent or consent-exempt |
| CNAME-cloaked endpoints can still face browser defenses | Browser documentation review | No | References | Depends on deployment and browser version |
| sGTM does not override denied consent or an explicit analytics opt-out | Platform-policy and architecture review | No live CMP/opt-out experiment | References and limitations | Requires a separate consent test matrix |
| sGTM can improve attribution when identifiers and transaction links are preserved | Architecture inference | No universal attribution experiment | Article and future-experiment plan | Migration errors can worsen attribution |
| sGTM infrastructure has non-zero cost | Platform pricing and operations review | No production-load cost test | References | Cost varies by region, logging, traffic, provider, and scaling model |
| Safari, blockers, CMPs, and vendor endpoints behave identically to the synthetic fixture | Not supported | No | Limitations | Must not be claimed |

## Evidence labels for future contributions

Use one of these labels in new documentation:

- **Measured:** produced by a defined experiment with retained raw output.
- **Audited:** observed in a dated external artifact such as a filter list.
- **Documented:** stated in a cited primary platform or browser source.
- **Inferred:** a reasoned architecture conclusion supported by measured or documented premises.
- **Not tested:** plausible or important, but not evaluated by the release.
