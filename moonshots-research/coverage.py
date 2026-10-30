#!/usr/bin/env python3
"""Summarize citation-window coverage without implying full transcript/audio review."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EPISODES = ROOT / "data" / "episodes.json"
CLAIMS = ROOT / "data" / "claims.json"
AUDITS = ROOT / "data" / "evidence_audits.json"
TIME_RANGE = re.compile(r"^(\d{2}):(\d{2}):(\d{2})\s*[–-]\s*(\d{2}):(\d{2}):(\d{2})$")


def seconds(h, m, s):
    a, b, c = int(h), int(m), int(s)
    if b >= 60 or c >= 60:
        raise ValueError("invalid minute or second")
    return a * 3600 + b * 60 + c


def intervals(ranges):
    pairs = []
    for r in ranges:
        match = TIME_RANGE.fullmatch(r.strip())
        if not match:
            raise ValueError("invalid timestamp span: " + str(r))
        h1, m1, s1, h2, m2, s2 = match.groups()
        start, end = seconds(h1, m1, s1), seconds(h2, m2, s2)
        if end <= start:
            raise ValueError("empty or reverse timestamp span: " + str(r))
        pairs.append((start, end))
    return sorted(pairs)


def union_window_seconds(pairs):
    if not pairs:
        return 0
    spans = []
    for start, end in sorted(pairs):
        if spans and start <= spans[-1][1]:
            spans[-1] = (spans[-1][0], max(end, spans[-1][1]))
        else:
            spans.append((start, end))
    return sum(end - start for start, end in spans)


def coverage(episodes, claims, audits):
    claim_counts = Counter(c["episode_id"] for c in claims)
    audit_ids = {a["claim_id"] for a in audits}
    audit_count = Counter(c["episode_id"] for c in claims if c["claim_id"] in audit_ids)
    rows = []
    for e in episodes:
        references = intervals(e.get("reviewed_timestamp_ranges", []))
        rows.append({
            "id": e["id"],
            "title": e["title"],
            "analysis_status": e["analysis_status"],
            "source_window_count": len(references),
            "source_window_minutes": round(union_window_seconds(references) / 60, 1),
            "claims": claim_counts[e["id"]],
            "second_pass_claim_audits": audit_count[e["id"]],
            "full_transcript_verified": e.get("transcript_status") == "ready",
            "full_audio_verified": False,
        })
    return rows


def markdown(rows):
    windows = sum(x["source_window_minutes"] for x in rows)
    lines = [
        "# Episode-level evidence coverage (NOT listening-time proof)",
        "",
        f"- Episode inventory: **{len(rows)}**",
        f"- Sum of referenced public-transcript time windows: **{windows:.1f} minutes**",
        f"- Episodes with complete transcripts verified: **{sum(x['full_transcript_verified'] for x in rows)}**",
        "- Episodes with complete audio audits: **0**",
        "",
        "**Critical limitation:** Timestamp ranges are *citations/navigation windows* supplied by",
        "the research notes, **not a validated recording of minutes fully read or listened to**.",
        "The total is **not** a coverage percentage; complete episode runtimes are not recorded.",
        "Even a wide window is not evidence that every passage inside it was read.",
        "",
        "| Episode | Referenced windows | Approx. span minutes | Claims | Second-pass audits |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for x in rows:
        lines.append(f"| {x['id']} | {x['source_window_count']} | {x['source_window_minutes']:.1f} | {x['claims']} | {x['second_pass_claim_audits']} |")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args(argv)
    episodes = json.loads(EPISODES.read_text())
    claims = json.loads(CLAIMS.read_text())
    audits = json.loads(AUDITS.read_text())
    rows = coverage(episodes, claims, audits)
    print(json.dumps(rows, indent=2) if args.format == "json" else markdown(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
