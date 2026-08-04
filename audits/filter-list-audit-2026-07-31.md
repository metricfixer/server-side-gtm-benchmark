# Filter-list audit — 31 July 2026

## AdGuard first-party tracking-server list

Source:  
https://github.com/AdguardTeam/AdguardFilters/blob/master/SpywareFilter/sections/tracking_servers_firstparty.txt

Observed snapshot counts recorded in the original benchmark package:

- total lines: 3,594;
- active non-comment blocking rules: 3,550;
- exact hostname-label prefixes:
  - `sgtm.`: 43;
  - `gtm.`: 41;
  - `metrics.`: 50;
  - `analytics.`: 232;
  - `collect.`: 14;
  - `tracking.`: 80;
  - `tagging.`: 56.

## EasyPrivacy review

Source:  
https://github.com/easylist/easylist/blob/master/easyprivacy/easyprivacy_general.txt

The reviewed snapshot contained an explicit “Server-side GTM” section with 22 active rules targeting recognizable scripts, container IDs, paths, query parameters, and common hosted implementations.

## Interpretation

The audit demonstrates that first-party and sGTM-specific blocking rules existed in the reviewed lists. It does not estimate blocker adoption, affected-user share, or a universal event-recovery percentage.

## Reproducibility limitation

The original package did not record the exact upstream commit hashes and did not bundle the complete source snapshots. The counts are therefore preserved as a dated audit record, not as a bit-for-bit reproducible filter-list dataset. Future audits should record repository commit hashes and file SHA-256 values.
