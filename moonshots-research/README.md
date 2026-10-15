# Moonshots Research Radar

Research window: **2026-08-14 through 2026-10-14, inclusive**. Show: **Moonshots with Peter Diamandis** (Apple podcast ID `1648228034`). This is a **public, reproducible research foundation plus a first evidence-backed pass**: seven episodes selectively reviewed, NOT 24 complete episode analyses.

## Status and scope

- `data/episodes.json`: 24 entries inventoried from the public spoken.md catalog as of 2026-10-14 (22 numbered episodes #280–#301 and 2 unnumbered specials). Dates are the provider's dates until RSS reconciliation.
- `data/claims.json`: 20 source-attributed claim and analytical-caveat records across seven partially reviewed episodes; distinguish independent checks, primary-source corroboration, podcast-only forecasts, and contested headlines.
- `data/research_queue.json`: seven prioritized deeper research questions; these are NOT verified facts.
- `reports/initial-brief.md`: first pilot, maintained as a historical snapshot.
- `reports/opportunity-radar-2026-10-14.md`: substantive cross-episode synthesis, evidence check, and prioritized action hypotheses.
- `data/forecasts.json`: five preregistered dated analyst forecasts with resolution criteria and source links.
- `collector.py`: update episode metadata from the publisher's RSS; import locally supplied transcripts; report coverage; validate provenance; create a status report. Python standard library only.

## Quick start

```bash
cd moonshots-research
python3 collector.py status
python3 collector.py validate
python3 -m unittest discover -s tests -v
python3 collector.py sync                          # refresh from official feed; needs internet
python3 collector.py report --output reports/coverage.md
# When you have legitimately obtained a full transcript:
python3 collector.py import-transcript --episode ep-300 --file /path/to/transcript.md
```

`sync` is idempotent, never erases transcript/analysis progress, and keeps the study window fixed. Use `--rss-file sample.xml` to replay an RSS snapshot offline. An RSS feed can omit older episodes; missing items never cause deletion. New releases after 2026-10-14 are outside this frozen cohort and require a distinct study.

Official/publisher RSS: https://feeds.megaphone.fm/DVVTS2890392624  
Official episode archive: https://www.diamandis.com/podcast/all  
Transcripts catalog: https://spoken.md/podcast/moonshots-with-peter-diamandis-1648228034  
Spoken API docs: https://spoken.md/podcast/moonshots-with-peter-diamandis-1648228034 (authenticated API; not used by this repo)

## Provenance and analysis gates

1. **Discovery**: capture title, publication date, publisher URL, GUID, source and retrieval date; preserve source conflicts.
2. **Transcripts**: acquire full content from a licensed or permitted source, or import a transcript you possess. Keep raw transcripts local at `.private/transcripts/`; they are ignored by Git. Never place podcast audio, whole transcripts, private keys or access tokens in this public repo.
3. **Extraction**: attribute each claim to episode, speaker, and timestamp; attach precise original-source citation. Explicitly distinguish factual claim, forecast, opinion, framework, speculation, and paid promotion.
4. **Research**: search original studies, official records, product documentation, and skeptical evidence. A speaker's company corroborating its own claim is *primary-source corroboration*, not independent validation. Date every check; avoid turning episode titles into verified facts.
5. **Forecasts**: write falsifiable conditions, horizon, probability/range, baseline, counterarguments, last-checked date, and resolution criteria. Do not assign confidence as arbitrary precision.
6. **Recommendations**: separate user-specific opportunities from broadly applicable advice. Identify effort, capital required, reversibility and first cheap experiment.
7. **Review**: do not publish full corpus-derived conclusions until transcript coverage and per-claim verification are reported.

## Inputs and costs

The main RSS feed provides **metadata**, not full transcript text. Spoken.md advertises transcript access via its paid API; an API key is not provided here. This project deliberately performs **no automatic purchase, audio download, model API call, or recurring paid job**. A coding agent or ChatGPT Work can independently review each item and write sourced notes or extend the pipeline once inputs/permissions are available.

## Next milestone

Complete the 17 remaining episode reviews, expand and deduplicate the 20-record initial claim ledger, secure full transcripts privately where needed, improve independent evaluations, and track the five forecasts against their dated resolution criteria. The first opportunity report is already available. Track coverage by episode and claim, not merely by count of summaries.
### Current coverage (October 14 cutoff)

- 24 episodes/specials inventoried from the provider catalog, subject to RSS-date reconciliation.
- 7 time-coded partial reviews (#280, #286, #292, #297, #298, #299, #300); 17 episodes not yet source-reviewed.
- 20 attributed claim/interpretation records; 5 preregistered analyst forecasts; 7 research queue items.
- 0 complete transcripts acquired in local private storage; 0 episodes declared fully analyzed. Public timestamped transcripts exist at Podscripts but are **not republished** here.
- Offline validation and GitHub Actions tests; no scheduled crawl or AI inference budget.
