# A no-API baseline for structured decision models

Motivation: episode #299 discusses TypeSafe's **Jev** and fast typed decisions. Independent public [benchmark research](https://arxiv.org/abs/2609.37647) finds substantial task-specific results and calibration challenges. This experiment does **not** install Jev or call any provider.

## Run

```bash
python3 moonshots-research/experiments/decision_eval.py \
  --gold moonshots-research/experiments/fixtures/synthetic_gold.json \
  --predictions moonshots-research/experiments/fixtures/synthetic_predictions.json \
  --confidence-threshold 0.8
```

The fixtures are entirely **fabricated demonstration tickets and fabricated prediction values**, including their 10 ms latency and $0.001 per-item costs. **No model actually produced these predictions.** Do not quote this fixture's accuracy, cost or latency as any vendor's performance.

## Actual evaluation protocol

1. Obtain authorization and create a private test file of 100–200 **anonymized** representative messages with independently human-verified labels. Do not commit personal/customer data to this public repository.
2. Choose a small label taxonomy that fits the business. Hold examples aside before prompt and threshold tuning; freeze the gold labels.
3. Run at least three approaches on **the same** held-out cases: low-cost deterministic rules, a decision/classification model, and a general-purpose LLM. Collect each output, confidence, measured latency and actual total billed cost. Predictions can be written as the JSON shape in the synthetic fixture.
4. Compute coverage and accuracy among **automatically accepted** decisions using a chosen confidence threshold, plus the absolute number of wrong automated decisions. Lowering coverage can raise selective accuracy; do not claim improved accuracy without disclosing coverage.
5. Count errors by business impact. For security incidents, client charges, regulated claims or irreversible tasks, use human approval rather than automated dispatch unless risk has been professionally assessed.
6. Review failure cases, set a stop criterion and present performance with sample sizes; only recommend a model when it changes an operational decision. Watch for Spanish/English and ambiguous messages.

No API secrets, audio, transcript copies, live payments, data collection or externally scheduled calls are used.

## Current status

A working **evaluation harness** and synthetic fixtures exist. **No genuine model comparison has been performed**, and no actual customer performance has been measured. The empirical experiment depends on a permitted labeled dataset and real model outputs.
