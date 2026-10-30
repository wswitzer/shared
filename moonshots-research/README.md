# Moonshots Research Radar

Research window: **2026-08-14 through 2026-10-14, inclusive**. Show: **Moonshots with Peter Diamandis** (Apple podcast ID `1648228034`). This is a **public, reproducible research foundation plus a first evidence-backed pass**: all 24 episodes selectively reviewed at specific timestamps, NOT 24 complete episode analyses.

## Status and scope

- `data/episodes.json`: 24 entries initially inventoried from the public spoken.md catalog, then updated using official RSS (22 numbered episodes #280–#301 and 2 unnumbered specials). Dates have been reconciled with the publisher's RSS feed.
- `data/claims.json`: 74 source-attributed claim and analytical-caveat records across 24 partially reviewed episodes; distinguish independent checks, primary-source corroboration, podcast-only forecasts, and contested headlines.
- `data/research_queue.json`: thirteen prioritized deeper research questions; these are NOT verified facts.
- `reports/initial-brief.md`: first pilot, maintained as a historical snapshot.
- `reports/opportunity-radar-2026-10-14.md`: first seven-episode research snapshot; maintained as a historical report.
- `reports/batch-02-agents-safety-robotics-biotech.md`: second six-episode pass, claims checked, and an agent-reliability pilot proposal.
- `data/forecasts.json`: nine preregistered dated analyst forecasts with resolution criteria and source links.
- `data/themes.json`: seven cross-episode evidence themes linking claim IDs and specific practical tests.
- `reports/batch-03-final-11-episodes.md`: third pass, covering previously unreviewed entries.
- `reports/integrated-decision-brief-2026-10-14.md`: **start here** for cross-episode recommendations, evidence hierarchy and forecast summary.
- `reports/deep-review-299-300.md`: expanded two-interview transcript audit, including explicit investment and sponsor claims, proposal-vs-law distinctions, and the decision-model opportunity.
- `reports/source-verification-2026-10-15.md`: latest source corrections, 41 manual audits, and an explicit account of unresolved questions.
- `forecast_review.py`: read-only due-date planner for nine forecasts (never auto-resolves them).
- `coverage.py`: per-episode timestamp citation-window audit; not listening-time proof or a percentage of total audio.
- `data/evidence_audits.json`: 41 separately documented second-pass source assessments; one entry can be critical or cautionary without declaring the claim false.
- `quality.py`: validate audit integrity, distinguish sponsor evidence, summarize support labels, and rank the **33 remaining claims without second-pass audit**.
- `experiments/decision_eval.py`: offline classifier comparison, with **synthetic** tickets and prediction scores, zero AI inference calls, and no customer data. See `experiments/README.md`.

- `collector.py`: update episode metadata from the publisher's RSS; import locally supplied transcripts; report coverage; validate claim, forecast and theme provenance; create a status report. Python standard library only.

## Quick start

```bash
cd moonshots-research
python3 collector.py status
python3 collector.py validate
python3 quality.py validate
python3 quality.py summary
python3 quality.py backlog --limit 15
python3 coverage.py
python3 forecast_review.py --as-of 2026-10-15
python3 experiments/decision_eval.py --gold experiments/fixtures/synthetic_gold.json --predictions experiments/fixtures/synthetic_predictions.json
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

## Research deliverables & reports

- `reports/comprehensive-research-synthesis-2026-10-18.md`: **Core research synthesis** across all 24 episodes, 10 technology domains, contradictions, second-order effects, and developer implications.
- `reports/technology-prediction-radar-2026-10-18.md`: **1-to-10-year capability radar** across 6 domains, evidentiary hierarchy, and status of the 9 preregistered forecasts.
- `reports/business-opportunity-assessment-2026-10-18.md`: **Commercial strategy for Switzer Systems**, evaluating 8 concrete offerings across 10 structured dimensions with a 90-day roadmap.
- `reports/research-limitations-and-uncertainties-2026-10-18.md`: **Methodological boundaries, biases, and open scientific questions**.
- `reports/source-verification-2026-10-18.md`: **Full 74-claim second-pass audit checkpoint**, clearing 100% of the backlog.
- `reports/deep-review-299-300.md`: Multi-segment transcript audit of Astro Teller (#300) and Richard Socher (#299).
- `reports/integrated-decision-brief-2026-10-14.md`: Foundational cross-episode brief and initial triage.

### Current verified coverage (Baseline cutoff October 14, 2026; research updated October 18, 2026)

- **24 episodes/specials** inventoried from provider catalog and reconciled with official publisher RSS.
- **24 complete episode transcripts** acquired and hashed locally in private storage (`.private/transcripts/`).
- **2 episodes fully analyzed end-to-end** (#299, #300); 22 episodes reviewed via complete timestamped transcript navigation windows.
- **0 episodes with complete audio audits** (truthfully disclosed; representative audio sampled and calibrated via local Whisper).
- **74 attributed claim/interpretation records** in `data/claims.json`.
- **74 second-pass evidence audits** in `data/evidence_audits.json` (**0 unreviewed claims remaining in backlog**).
- **9 open preregistered analyst forecasts** monitored via `forecast_review.py` with zero premature resolutions.
- **7 cross-episode research themes** linking verified claims, failure modes, and practical tests.
- Offline validation and GitHub Actions test suite (36 unit tests passing deterministically).

**Quality gate:** The claim ledger strictly distinguishes primary corporate disclosures from independent validation. Future predictions are never marked independently verified based on past evidence. Full textual coverage is never misrepresented as full human listening time.
