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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "summary"])
    args = parser.parse_args(argv)
    claims, audits, episodes = read(CLAIMS), read(AUDITS), read(SPEAKERS)
    failures = validate_evidence_audits(audits, claims, episodes)
    if failures:
        print("\n".join(failures))
        return 2
    if args.command == "validate":
        print(f"OK: {len(audits)} deep evidence audits tied to {len(claims)} claims")
    else:
        print(json.dumps(summary(audits, claims), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
