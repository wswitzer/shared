#!/usr/bin/env python3
"""Offline second-pass evidence audit checks; does not fetch transcripts or contact APIs."""
import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent
CLAIMS = BASE / "data" / "claims.json"
AUDITS = BASE / "data" / "evidence_audits.json"
SPEAKERS = BASE / "data" / "episodes.json"
FORECASTS = BASE / "data" / "forecasts.json"
THEMES = BASE / "data" / "themes.json"

CLASSIFICATIONS = {
    "independent_benchmark", "sponsored_advertisement", "political_proposal_and_bill",
    "government_primary_record", "vendor_development_claim", "scientific_institute_statement",
    "competition_organizer", "speaker_internal_metric", "financial_disclosure",
}
OUTCOMES = {
    "bounded_supported", "do_not_generalize", "stage_distinction",
    "primary_document_confirmed", "projection_not_measurement", "under_review",
    "not_independently_verified", "source_statement_confirmed",
}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_evidence_audits(audits, claims, episodes):
    issues = []
    by_claim = {c.get("claim_id"): c for c in claims}
    known_episodes = {e.get("id") for e in episodes}
    ids = set()
    for audit in audits:
        cid = audit.get("claim_id")
        if not cid or cid not in by_claim:
            issues.append("Audit references missing claim: " + str(cid))
            continue
        if cid in ids:
            issues.append("Duplicate audit for claim: " + cid)
        ids.add(cid)
        c = by_claim[cid]
        if c.get("episode_id") not in known_episodes:
            issues.append("Audit claim episode missing: " + cid)
        if audit.get("source_class") not in CLASSIFICATIONS:
            issues.append("Unknown source class: " + cid)
        if audit.get("outcome") not in OUTCOMES:
            issues.append("Unknown outcome: " + cid)
        for field in ("conclusion", "remaining_uncertainty"):
            if not audit.get(field):
                issues.append("Audit lacks " + field + ": " + cid)
        for field in ("checked_date", "evidence_cutoff"):
            try:
                date.fromisoformat(audit[field])
            except (ValueError, KeyError, TypeError):
                issues.append("Invalid " + field + ": " + cid)
        if not audit.get("checked_urls") or not all(
            isinstance(url, str) and url.startswith("https://") for url in audit.get("checked_urls", [])
        ):
            issues.append("Audit lacks verified HTTPS reference: " + cid)
        if audit.get("transcript_audio_verified") is not False:
            issues.append("Audit falsely claims audio verification: " + cid)
        if audit.get("source_class") == "sponsored_advertisement":
            if c.get("kind") != "paid_promotion" or c.get("verification_status") == "independently_verified":
                issues.append("Sponsor claim incorrectly categorized as verified evidence: " + cid)
        if audit.get("outcome") in {"do_not_generalize", "projection_not_measurement", "not_independently_verified"}:
            if c.get("verification_status") == "independently_verified":
                issues.append("Evidence caveat conflicts with claim grade: " + cid)
    return issues


def summary(audits, claims):
    by_status = Counter(c.get("verification_status", "unknown") for c in claims)
    classes = Counter(a.get("source_class", "unknown") for a in audits)
    return {
        "claim_count": len(claims), "audited_claim_count": len(audits),
        "claim_status_counts": dict(sorted(by_status.items())),
        "audited_source_classes": dict(sorted(classes.items())),
        "note": "Classification counts are not ground-truth scores. Audit metadata does not verify source audio.",
    }


def prioritize_unaudited(claims, audits, forecasts, themes):
    """Offline triage points are review priority, not confidence or risk probability."""
    reviewed = {a["claim_id"] for a in audits}
    forecast_refs = {cid for f in forecasts for cid in f.get("supporting_claim_ids", [])}
    theme_refs = {cid for t in themes for cid in t.get("claims", [])}
    risk_words = ("clinical", "cancer", "safety", "revenue", "investment",
                  "finance", "fda", "security", "legislat", "law", "benchmark")
    remaining = []
    for c in claims:
        cid = c["claim_id"]
        if cid in reviewed:
            continue
        state = c.get("verification_status")
        score = {"contested": 6, "podcast_only": 4,
                 "independently_verified": 3, "corroborated_primary": 3}.get(state, 2)
        reasons = ["Second-pass audit missing"]
        if cid in forecast_refs:
            score += 5
            reasons.append("Supports a forecast")
        if cid in theme_refs:
            score += 2
            reasons.append("Feeds a cross-episode theme")
        if any(word in (c.get("claim", "") + c.get("kind", "")).lower() for word in risk_words):
            score += 2
            reasons.append("Regulated, safety-sensitive or quantitative")
        if c.get("kind") == "paid_promotion":
            score += 6
            reasons.append("Sponsor claim must be segregated")
        remaining.append({"claim_id": cid, "episode_id": c["episode_id"],
                          "priority_score": score,
                          "verification_status": state, "reasons": reasons})
    return sorted(remaining, key=lambda item: (-item["priority_score"], item["claim_id"]))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "summary", "backlog"])
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)
    claims, audits, episodes = read(CLAIMS), read(AUDITS), read(SPEAKERS)
    failures = validate_evidence_audits(audits, claims, episodes)
    if failures:
        print("\n".join(failures))
        return 2
    if args.command == "validate":
        print(f"OK: {len(audits)} deep evidence audits tied to {len(claims)} claims")
    elif args.command == "summary":
        print(json.dumps(summary(audits, claims), indent=2, ensure_ascii=False))
    else:
        ranked = prioritize_unaudited(claims, audits, read(FORECASTS), read(THEMES))
        print(json.dumps({"unaudited_count": len(ranked),
                          "items": ranked[:max(0, args.limit)]},
                         indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
