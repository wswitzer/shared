# Publisher RSS reconciliation — 2026-10-14 research cutoff

The initial inventory of 24 entries came from Spoken.md's public podcast catalog. On 2026-10-15 UTC (still October 14 in Mexico City), GitHub Actions ran `python3 collector.py sync` against the verified publisher feed `https://feeds.megaphone.fm/DVVTS2890392624`.

**Result:** 24 RSS items in study window; **0 new rows**, 58 metadata fields updated. All progress metadata, seven selectively reviewed transcript segments and research annotations were retained. All eight offline unit tests and validation passed.

Provider catalog date discrepancies resolved in favor of the publisher RSS:

| Episode | Provider date | Publisher RSS date |
| --- | --- | --- |
| #294 | 2026-09-27 | 2026-09-28 |
| #291 | 2026-09-17 | 2026-09-19 |
| #288 | 2026-09-11 | 2026-09-28 |
| #282 | 2026-08-21 | 2026-08-29 |

Other title and GUID adjustments were applied as published by the RSS feed. No full podcast transcripts were read by the synchronization step; it deals with metadata only. Source catalogs may retain different display dates, and a feed re-publication does not necessarily prove the underlying audio was first released on that date.

Check: [GitHub Actions RSS reconciliation](https://github.com/wswitzer/shared/actions/runs/38690351105). The checked-in `data/episodes.json` is now the reconciled inventory.
