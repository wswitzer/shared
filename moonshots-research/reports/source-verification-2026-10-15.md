# Source verification and review-depth checkpoint — October 15, 2026

**Baseline evidence cutoff:** 2026-10-14. **Work performed:** 2026-10-15. This report updates editorial conclusions without changing the original nine forecast conditions.

## Current state

- **24/24** podcast episodes/specials have at least one cited public-transcript window. **0/24** completed full transcript or original audio audits.
- **74** unique claim/interpretation ledger records; **41** have explicit second-pass source-audit records and **33** still await deeper verification. Review `data/evidence_audits.json` and run `python3 quality.py backlog` for the dynamically prioritized list.
- **Nine** preregistered open analyst forecasts. The new `forecast_review.py` flags due/overdue horizons without resolving claims or rewriting the original criteria.
- As of this pass, first-order claim labels in the ledger are **25 primary-source corroborated, 8 independently supported, 36 podcast-only/interpretive, and 5 contested**. Labels capture evidence for a *bounded statement*, not epistemic certainty about the podcast as a whole.
- A new `coverage.py` exposes citation-window minutes without claiming that those minutes were fully heard, read, or exhaustive. **Do not report a transcript-completion percentage.**

## Important corrected and clarified items

| Claim IDs | Primary finding | Evidentiary boundary |
| --- | --- | --- |
| `ms-297-001` | [Nature's May 2026 Robin paper](https://www.nature.com/articles/s41586-026-10652-y) demonstrates a human-in-the-loop experimental biology workflow. | A prospective claim about the *next 3–5 years* is not independently verified by a paper predating the prediction. Claim downgraded to **podcast_only** and retained peer-reviewed background references. |
| `ms-286-001` | [ARC Prize](https://arcprize.org/results/openai-gpt-6) lists Astra Max at **62.7% Standard vs 98.6% Provider Adapter**, and Astra High at **54.8% Standard vs 99.9% Provider Adapter** on ARC-AGI-3. | Same model family, different harness/effort. The very high score is not fabricated solely because another harness reports lower results. Neither predicts a customer's task-level reliability without matched evaluation. |
| `ms-280-001` | [Duke's flexible-load study](https://scholars.duke.edu/publication/1665550) analyzes modeled grid opportunities. | Simulated grid accommodation is **not** real installed or commissioned generation/capacity. |
| `ms-280-002` | [IEA 2026](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries) shows sodium-ion batteries in early scale-up amid mature LFP supply. | Technology potential is not an industry-wide proven **10× cost saving** or imminent capacity parity. |
| `ms-298-001` | [White House Accord text, Sep 29 2026](https://www.presidency.ucsb.edu/documents/white-house-accord-super-intelligence) requests audits, controls and external evaluators and says later regulation *may* codify them. | Voluntary commitments and enforceable law are separate categories. |
| `ms-291-002` | [Anthropic, Sep 18](https://www.anthropic.com/news/accenture-embedded-evaluation), announces Accenture collaboration and admits unsettled independent evaluator access/funding standards. | Promise of embedded evaluation is **not** an already-published substantive independent assessment. |
| `ms-284-001` | [NVIDIA earnings release](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2027/) reports $96.221B revenue and +106% year-on-year growth in fiscal Q2 2027. | This is a primary issuer financial release, not a prediction of future sustained growth. |
| `ms-292-002/003` | [Robinhood issuer filing](https://www.sec.gov/Archives/edgar/data/1783879/000178387926000114/hood-20260630.htm) and [SEC investor guidance](https://www.investor.gov/introduction-investing/investing-basics/investment-products/tokenized-securities) distinguish economic exposure from underlying shareholder rights. | Securities offered by different providers can have materially different legal structures; SEC archival hosting does not mean endorsement. |
| `ms-296-003` | [Waymo](https://www.waymo.com/safety/impact/) reports **271.3M driverless passenger miles through June 2026**, and fewer crashes with injuries than matched city human benchmarks. | Operator data are transparent but conditional on cities/routes/time; no Tesla-specific inference or universal safety guarantee. |
| `ms-290-001/003` | [United Therapeutics' SEC filing](https://www.sec.gov/Archives/edgar/data/1082554/000108255426000006/uthr-20251231.htm) documents investigational xenotransplantation programs. | IND trial authorization does **not** imply a licensed unlimited organ supply; a medical decision requires qualified professionals. |
| `ms-299-001` | [AIDE2](https://arxiv.org/abs/2609.26457) reports seven successive research-agent improvements in eight days; [AI4AI-Bench](https://arxiv.org/abs/2608.20318) finds modest progress on hidden algorithm-design benchmarks. | Both are bounded research preprints and require independent replication; neither proves a hard cap on AI capabilities or inevitable open-ended takeoff. |
| `ms-special-builders-001/003` | [XPRIZE organizer report](https://www.xprize.org/news/polyfork-wins-the-build-with-gemini-xprize) confirms competition categories and Mexico-based second-place Tician Cierre. | Prize selection is highly selective; organizer statements are not a typical startup survival-rate study. |

## Remaining work, in order

1. **33 claims need second-pass source assessments.** The priority CLI ranks forecast-linked claims and safety/financial/clinical topics first. Many are explicitly untestable *opinions or future forecasts*, so a high-quality audit may conclude `not_independently_verified` rather than force a binary true/false.
2. **Full text and audio verification** is incomplete for every episode. For each candidate, obtain transcript/audio with appropriate permissions, identify speaker switches and quoted promotional messages, check the entire episode rather than only cited segments, and reconcile discrepancies with original audio.
3. **Actual experimental evidence** is needed before recommending a specialized decision model as a commercial offer. `experiments/decision_eval.py` currently has only synthetic fixtures and no genuine inference/billing measurements.
4. **Forecast resolution** is future-dependent; the read-only planner provides a manual review schedule. Add date-stamped assessments and archived external sources at the horizon; never rewrite the frozen prediction after seeing the outcome.
5. **No automatic source monitoring or paid transcript jobs** have been authorized/created. CI performs code tests and an RSS metadata smoke check on commits only.

## Reproduce audit and schedule checks

```bash
cd moonshots-research
python3 collector.py validate
python3 quality.py validate
python3 quality.py summary
python3 quality.py backlog --limit 20
python3 coverage.py
python3 forecast_review.py --as-of 2026-10-15 --warning-days 60
python3 -m unittest discover -s tests -v
```

This is a **source-supported exploratory study**, not complete listening of 24 episodes, a financial/medical recommendation, or a claim that 41 records have all been independently replicated.
