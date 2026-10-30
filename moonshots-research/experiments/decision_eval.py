#!/usr/bin/env python3
"""Compare pre-generated classification outputs; zero API calls and zero transcript access.

The synthetic fixtures are for smoke testing the evaluator, NOT evidence
that any product or model reaches a particular performance level.
"""
import argparse
import json
import statistics
from pathlib import Path


def read_rows(path):
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("Expected a JSON array")
    return rows


def evaluate(gold, outputs, confidence_threshold=0.8):
    if not 0 <= confidence_threshold <= 1:
        raise ValueError("confidence threshold must be within [0, 1]")
    ids = [row["id"] for row in gold]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate reference IDs")
    pred_ids = [row["id"] for row in outputs]
    if len(pred_ids) != len(set(pred_ids)):
        raise ValueError("duplicate prediction IDs")
    if set(pred_ids) != set(ids):
        raise ValueError("Predictions and reference data must contain exactly the same IDs")
    by_id = {row["id"]: row for row in outputs}
    labels = {row["label"] for row in gold}
    attempted = 0
    correct = 0
    costs = []
    latency = []
    conf_abstain = 0
    explicit_abstain = 0
    failures = []
    for item in gold:
        p = by_id[item["id"]]
        score = float(p.get("confidence", 0.0))
        if not 0 <= score <= 1:
            raise ValueError("invalid confidence for " + str(item["id"]))
        cost = float(p.get("cost_usd", 0))
        ms = float(p.get("latency_ms", 0))
        if cost < 0 or ms < 0:
            raise ValueError("cost and latency cannot be negative")
        costs.append(cost)
        latency.append(ms)
        result = p.get("prediction")
        if result is None or result == "abstain":
            explicit_abstain += 1
            continue
        if result not in labels:
            raise ValueError("unknown output label " + str(result))
        if score < confidence_threshold:
            conf_abstain += 1
            continue
        attempted += 1
        if result == item["label"]:
            correct += 1
        else:
            failures.append({"id": item["id"], "expected": item["label"], "predicted": result})
    total = len(gold)
    if not total:
        raise ValueError("empty reference dataset")
    return {
        "dataset": "external labels required; synthetic fixture is NOT a model benchmark",
        "n": total,
        "threshold": confidence_threshold,
        "automated_decisions": attempted,
        "coverage": round(attempted / total, 4),
        "selective_accuracy": round(correct / attempted, 4) if attempted else None,
        "end_to_end_correct_rate": round(correct / total, 4),
        "errors": attempted - correct,
        "confidence_deferrals": conf_abstain,
        "explicit_deferrals": explicit_abstain,
        "total_cost_usd": round(sum(costs), 6),
        "mean_latency_ms": round(statistics.mean(latency), 3),
        "wrong_automated_decisions": failures,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--confidence-threshold", type=float, default=0.8)
    args = parser.parse_args(argv)
    print(json.dumps(evaluate(read_rows(args.gold), read_rows(args.predictions),
                              args.confidence_threshold), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
