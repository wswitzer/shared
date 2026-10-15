#!/usr/bin/env python3
"""Deterministic, dependency-free Moonshots episode inventory and provenance checks."""
import argparse
import copy
import hashlib
import json
import re
import shutil
import sys
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EPISODES = ROOT / "data" / "episodes.json"
CLAIMS = ROOT / "data" / "claims.json"
RSS = "https://feeds.megaphone.fm/DVVTS2890392624"
START, END = "2026-08-14", "2026-10-14"
PRIVATE = ROOT / ".private" / "transcripts"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def norm(title):
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def episode_id(title):
    match = re.search(r"(?:#|\bep\s*#?\s*)(\d{3})\b", title, re.I)
    if match:
        return "ep-" + match.group(1)
    return "special-" + hashlib.sha256(norm(title).encode()).hexdigest()[:12]


def rss_items(raw):
    root = ET.fromstring(raw)
    rows = []
    for item in root.findall(".//channel/item"):
        title = (item.findtext("title") or "").strip()
        if not title:
            continue
        pub = (item.findtext("pubDate") or "").strip()
        try:
            date = parsedate_to_datetime(pub).date().isoformat()
        except (TypeError, ValueError, IndexError):
            continue  # never guess an unknown publication date
        if not START <= date <= END:
            continue
        rows.append({
            "id": episode_id(title), "title": title, "published_date": date,
            "date_source": "publisher_rss", "guid": item.findtext("guid"),
            "source_url": item.findtext("link") or "",
            "transcript_status": "not_acquired", "analysis_status": "pending",
        })
    return rows


def fetch_rss(url):
    req = urllib.request.Request(url, headers={"User-Agent": "MoonshotsResearch/0.1 (+personal research)"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def synchronize(existing, incoming):
    out = {x["id"]: copy.deepcopy(x) for x in existing}
    title_to_id = {norm(x["title"]): x["id"] for x in existing}
    added, updated = 0, 0
    for row in incoming:
        key = row["id"] if row["id"] in out else title_to_id.get(norm(row["title"]), row["id"])
        if key not in out:
            out[key] = row
            added += 1
        else:
            current = out[key]
            # Publisher feed wins for metadata, never for workflow progress.
            for field in ("title", "published_date", "date_source", "guid", "source_url"):
                if row.get(field) and current.get(field) != row[field]:
                    current[field] = row[field]
                    updated += 1
    return sorted(out.values(), key=lambda x: (x["published_date"], x["id"]), reverse=True), added, updated


def validate(episodes, claims):
    errors = []
    ids = [x.get("id") for x in episodes]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate episode IDs")
    for ep in episodes:
        if not START <= ep.get("published_date", "") <= END:
            errors.append("Episode outside frozen window: " + str(ep.get("id")))
        if ep.get("transcript_status") not in {"not_acquired", "ready", "unavailable"}:
            errors.append("Unknown transcript state: " + str(ep.get("id")))
    claim_ids = set()
    for c in claims:
        cid = c.get("claim_id", "<missing>")
        if cid in claim_ids:
            errors.append("Duplicate claim ID " + cid)
        claim_ids.add(cid)
        if c.get("episode_id") not in ids or not c.get("speaker") or not c.get("timecode") or not c.get("source_url"):
            errors.append("Claim lacks source/attribution: " + cid)
        state = c.get("verification_status")
        if state not in {"podcast_only", "corroborated_primary", "independently_verified", "contested"}:
            errors.append("Invalid verification status: " + cid)
        if state != "podcast_only" and not c.get("evidence"):
            errors.append("Corroborated/verified claim lacks evidence: " + cid)
        if state == "independently_verified" and not any(e.get("independent") for e in c.get("evidence", [])):
            errors.append("Independent verification not backed by independent source: " + cid)
    return errors


def report(episodes, claims):
    counts = Counter(e["transcript_status"] for e in episodes)
    analyzed = sum(1 for e in episodes if e.get("analysis_status") == "completed")
    verified = Counter(c["verification_status"] for c in claims)
    lines = [
        "# Moonshots research coverage", "",
        "Frozen window: " + START + " to " + END, "",
        f"- Episodes inventoried: **{len(episodes)}**",
        f"- Full transcripts acquired locally: **{counts['ready']}**",
        f"- Episodes fully analyzed: **{analyzed}**",
        f"- Claims in ledger: **{len(claims)}**",
        f"- Independently verified claims: **{verified['independently_verified']}**", "",
        "## Episode inventory", "",
        "| Date | Episode | Transcript | Analysis |",
        "| --- | --- | --- | --- |",
    ]
    for e in episodes:
        safe_title = e["title"].replace("|", "—")
        lines.append(f"| {e['published_date']} | {safe_title} | {e['transcript_status']} | {e.get('analysis_status', 'pending')} |")
    lines.extend(["", "This is a coverage report, not evidence that unprocessed titles are true.", ""])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sync = sub.add_parser("sync")
    sync.add_argument("--rss-file", type=Path)
    sync.add_argument("--feed-url", default=RSS)
    sub.add_parser("status")
    sub.add_parser("validate")
    imp = sub.add_parser("import-transcript")
    imp.add_argument("--episode", required=True)
    imp.add_argument("--file", type=Path, required=True)
    rep = sub.add_parser("report")
    rep.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    episodes = load(EPISODES)
    claims = load(CLAIMS)
    if args.command == "sync":
        raw = args.rss_file.read_bytes() if args.rss_file else fetch_rss(args.feed_url)
        incoming = rss_items(raw)
        if not incoming:
            print("No episodes in window: preserving inventory; investigate RSS coverage.", file=sys.stderr)
            return 2
        merged, added, updated = synchronize(episodes, incoming)
        errors = validate(merged, claims)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 2
        save(EPISODES, merged)
        print(f"RSS items={len(incoming)}; added={added}; updated_fields={updated}; inventory={len(merged)}")
    elif args.command == "import-transcript":
        e = next((x for x in episodes if x["id"] == args.episode), None)
        if e is None:
            parser.error("Unknown episode ID")
        content = args.file.read_bytes()
        if len(content.strip()) < 50:
            parser.error("Transcript too short; refusing to mark ready")
        PRIVATE.mkdir(parents=True, exist_ok=True)
        target = PRIVATE / (e["id"] + ".md")
        target.write_bytes(content)
        e["transcript_status"] = "ready"
        e["transcript_sha256"] = hashlib.sha256(content).hexdigest()
        save(EPISODES, episodes)
        print("Saved privately:", target)
    elif args.command == "validate":
        errors = validate(episodes, claims)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 2
        print(f"OK: {len(episodes)} episodes and {len(claims)} attributed claims")
    elif args.command == "status":
        print(report(episodes, claims).split("## Episode inventory")[0])
    elif args.command == "report":
        output = report(episodes, claims)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
            print("Wrote", args.output)
        else:
            print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
