#!/usr/bin/env python3
"""Read-only forecast review planner with frozen baseline and due-date checks.

It never adjudicates or edits a forecast and never performs background monitoring.
"""
import argparse
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FORECASTS = ROOT / "data" / "forecasts.json"
CLAIMS = ROOT / "data" / "claims.json"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def plan(forecasts, as_of, warning_days=60):
    if warning_days < 0:
        raise ValueError("warning days cannot be negative")
    results = []
    for forecast in forecasts:
        end = date.fromisoformat(forecast["horizon"])
        delta = (end - as_of).days
        state = forecast.get("status")
        if state == "open":
            if delta < 0:
                recommendation = "overdue_for_manual_adjudication"
            elif delta <= warning_days:
                recommendation = "within_review_window"
            else:
                recommendation = "not_due"
        else:
            recommendation = "already_marked_" + str(state)
        results.append({
            "forecast_id": forecast["forecast_id"],
            "horizon": forecast["horizon"],
            "days_until_deadline": delta,
            "status": state,
            "review_action": recommendation,
            "resolution_test": forecast["resolution"],
            "source_count": len(forecast.get("sources", [])),
        })
    return sorted(results, key=lambda item: (item["horizon"], item["forecast_id"]))


def markdown(items, as_of):
    lines = [
        "# Moonshots forecast review schedule",
        "",
        f"Review as of **{as_of.isoformat()}**. Forecasts are **not adjudicated automatically**.",
        "",
        "| ID | Deadline | Days left | State | Review action |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for r in items:
        lines.append(
            f"| {r['forecast_id']} | {r['horizon']} | {r['days_until_deadline']} | "
            f"{r['status']} | {r['review_action']} |"
        )
    lines.extend([
        "", "Manual adjudication protocol:",
        "1. Find original dated outcome sources and independent counterevidence.",
        "2. Apply the preregistered resolution criterion *without changing it*.",
        "3. If a criterion cannot be evaluated, mark unresolved and explain why.",
        "4. Save dated references, adjudicator and rationale in a new review record;",
        "   do not rewrite source predictions or the frozen 2026-10-14 baseline.",
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--warning-days", type=int, default=60)
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    as_of = date.fromisoformat(args.as_of)
    entries = plan(load(FORECASTS), as_of, args.warning_days)
    output = markdown(entries, as_of) if args.format == "markdown" else json.dumps({
        "as_of": as_of.isoformat(), "forecast_count": len(entries), "items": entries,
        "note": "No claims were resolved. This is a read-only review planner.",
    }, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
