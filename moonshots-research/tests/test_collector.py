import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import collector


class InventoryTests(unittest.TestCase):
    def test_seeded_inventory_is_frozen_and_unique(self):
        episodes = collector.load(collector.EPISODES)
        claims = collector.load(collector.CLAIMS)
        self.assertEqual(24, len(episodes))
        self.assertEqual([], collector.validate(episodes, claims))
        self.assertEqual(0, sum(ep["transcript_status"] == "ready" for ep in episodes))

    def test_extract_number_or_special_id(self):
        self.assertEqual("ep-299", collector.episode_id("Thing | EP #299"))
        self.assertEqual("ep-290", collector.episode_id("Moonshots 290"))
        self.assertEqual(collector.episode_id("A Special!"), collector.episode_id("a special"))

    def test_rss_window_and_timezone(self):
        xml = b"""<rss><channel>
        <item><title>Within window EP #300</title><pubDate>Mon, 05 Oct 2026 20:32:00 GMT</pubDate><guid>g300</guid><link>https://example.org/300</link></item>
        <item><title>Before window EP #279</title><pubDate>Thu, 13 Aug 2026 12:00:00 GMT</pubDate><guid>g279</guid></item>
        <item><title>After window EP #302</title><pubDate>Thu, 15 Oct 2026 12:00:00 GMT</pubDate><guid>g302</guid></item>
        </channel></rss>"""
        items = collector.rss_items(xml)
        self.assertEqual(1, len(items))
        self.assertEqual("ep-300", items[0]["id"])
        self.assertEqual("2026-10-05", items[0]["published_date"])

    def test_merge_preserves_workflow_and_updates_publisher_date(self):
        episodes = collector.load(collector.EPISODES)
        before = copy.deepcopy(next(e for e in episodes if e["id"] == "ep-300"))
        before["transcript_status"] = "ready"
        before["analysis_status"] = "completed"
        before["transcript_sha256"] = "example-hash"
        episodes = [before] + [e for e in episodes if e["id"] != "ep-300"]
        incoming = [{"id":"ep-300","title":before["title"],"published_date":"2026-10-06","date_source":"publisher_rss","guid":"g300","source_url":"https://example.org/300","transcript_status":"not_acquired","analysis_status":"pending"}]
        merged, added, updated = collector.synchronize(episodes, incoming)
        actual = next(e for e in merged if e["id"] == "ep-300")
        self.assertEqual(0, added)
        self.assertGreater(updated, 0)
        self.assertEqual("ready", actual["transcript_status"])
        self.assertEqual("completed", actual["analysis_status"])
        self.assertEqual("example-hash", actual["transcript_sha256"])
        self.assertEqual("2026-10-06", actual["published_date"])

    def test_no_fake_independent_verification(self):
        episodes = collector.load(collector.EPISODES)
        claims = collector.load(collector.CLAIMS)
        claims[0]["verification_status"] = "independently_verified"
        self.assertTrue(any("Independent verification" in e for e in collector.validate(episodes, claims)))


    def test_forecast_sources_and_dates(self):
        forecasts = collector.load(collector.FORECASTS)
        claims = collector.load(collector.CLAIMS)
        self.assertEqual(9, len(forecasts))
        self.assertEqual([], collector.validate_forecasts(forecasts, claims))

    def test_forecast_missing_support_is_rejected(self):
        forecasts = collector.load(collector.FORECASTS)
        claims = collector.load(collector.CLAIMS)
        forecasts[0]["supporting_claim_ids"] = ["missing-record"]
        self.assertTrue(any("missing claim" in x for x in collector.validate_forecasts(forecasts, claims)))

    def test_partial_review_is_not_full_transcript(self):
        episodes = collector.load(collector.EPISODES)
        self.assertEqual(24, sum(e.get("analysis_status") == "partial_review" for e in episodes))
        self.assertEqual(0, sum(e.get("transcript_status") == "ready" for e in episodes))
        summary = collector.report(episodes, collector.load(collector.CLAIMS), collector.load(collector.FORECASTS))
        self.assertIn("Episodes partially reviewed via public transcript: **24**", summary)
        self.assertIn("Full transcripts acquired locally: **0**", summary)

    def test_partial_review_requires_source_and_range(self):
        episodes = collector.load(collector.EPISODES)
        claims = collector.load(collector.CLAIMS)
        item = next(e for e in episodes if e["analysis_status"] == "partial_review")
        item.pop("reviewed_timestamp_ranges", None)
        self.assertTrue(any("timestamp coverage" in error for error in collector.validate(episodes, claims)))

    def test_complete_review_requires_full_transcript(self):
        episodes = collector.load(collector.EPISODES)
        claims = collector.load(collector.CLAIMS)
        item = next(e for e in episodes if e["analysis_status"] == "partial_review")
        item["analysis_status"] = "completed"
        self.assertTrue(any("Complete analysis" in error for error in collector.validate(episodes, claims)))

    def test_evidence_needs_assessment_and_publisher(self):
        episodes = collector.load(collector.EPISODES)
        claims = collector.load(collector.CLAIMS)
        first = next(c for c in claims if c.get("evidence"))
        first["evidence"][0].pop("assessment", None)
        self.assertTrue(any("Evidence missing" in error for error in collector.validate(episodes, claims)))

    def test_claim_ledger_batch_counts(self):
        claims = collector.load(collector.CLAIMS)
        self.assertEqual(74, len(claims))
        batch = {"ep-290", "ep-291", "ep-294", "ep-295", "ep-296", "ep-301"}
        self.assertEqual(15, sum(c["episode_id"] in batch for c in claims))

    def test_all_cohort_records_have_timestamped_source(self):
        episodes = collector.load(collector.EPISODES)
        self.assertEqual(24, len(episodes))
        self.assertEqual(24, sum(bool(x.get("public_transcript_url") and x.get("reviewed_timestamp_ranges")) for x in episodes))
        self.assertEqual(0, sum(x.get("analysis_status") == "completed" for x in episodes))
        self.assertEqual(0, sum(x.get("transcript_status") == "ready" for x in episodes))

    def test_final_batch_adds_30_claims_and_11_episodes(self):
        claim_records = collector.load(collector.CLAIMS)
        last_batch = {"ep-281","ep-282","ep-283","ep-284","ep-285","ep-287","ep-288","ep-289","ep-293","special-20260928-builders","special-20260928-star-trek"}
        from_final = [x for x in claim_records if x["episode_id"] in last_batch]
        self.assertEqual(30, len(from_final))
        self.assertEqual(last_batch, {x["episode_id"] for x in from_final})

    def test_themes_have_valid_episode_and_claim_links(self):
        themes = collector.load(collector.THEMES)
        episodes = collector.load(collector.EPISODES)
        claims = collector.load(collector.CLAIMS)
        self.assertEqual(7, len(themes))
        self.assertEqual([], collector.validate_themes(themes, episodes, claims))

    def test_unknown_theme_claim_is_rejected(self):
        themes = collector.load(collector.THEMES)
        episodes = collector.load(collector.EPISODES)
        claims = collector.load(collector.CLAIMS)
        themes[0]["claims"].append("nonexistent-id")
        self.assertTrue(any("unknown claim" in e for e in collector.validate_themes(themes, episodes, claims)))

import quality


class EvidenceAuditTests(unittest.TestCase):
    def test_deep_audits_are_linked_and_conservative(self):
        audits = quality.read(quality.AUDITS)
        claims = quality.read(quality.CLAIMS)
        episodes = quality.read(quality.SPEAKERS)
        self.assertEqual(33, len(audits))
        self.assertEqual([], quality.validate_evidence_audits(audits, claims, episodes))

    def test_sponsor_cannot_be_called_independently_verified(self):
        audits = quality.read(quality.AUDITS)
        claims = quality.read(quality.CLAIMS)
        episodes = quality.read(quality.SPEAKERS)
        promo = next(c for c in claims if c.get("claim_id") == "ms-299-007")
        promo["verification_status"] = "independently_verified"
        self.assertTrue(any("Sponsor claim incorrectly" in x for x in quality.validate_evidence_audits(audits, claims, episodes)))

    def test_missing_audit_reference_is_error(self):
        audits = quality.read(quality.AUDITS)
        claims = quality.read(quality.CLAIMS)
        episodes = quality.read(quality.SPEAKERS)
        audits[0]["claim_id"] = "ms-does-not-exist"
        self.assertTrue(any("missing claim" in x for x in quality.validate_evidence_audits(audits, claims, episodes)))


    def test_unverified_backlog_is_complete_and_deterministic(self):
        claims = quality.read(quality.CLAIMS)
        audits = quality.read(quality.AUDITS)
        forecasts = quality.read(quality.FORECASTS)
        themes = quality.read(quality.THEMES)
        remaining = quality.prioritize_unaudited(claims, audits, forecasts, themes)
        self.assertEqual(len(claims) - len(audits), len(remaining))
        self.assertEqual(41, len(remaining))
        self.assertEqual(len(remaining), len({x["claim_id"] for x in remaining}))
        self.assertEqual(remaining, quality.prioritize_unaudited(claims, audits, forecasts, themes))
        self.assertTrue(all(
            remaining[i]["priority_score"] >= remaining[i + 1]["priority_score"]
            for i in range(len(remaining) - 1)
        ))

    def test_future_prediction_is_not_independently_verified(self):
        audits = quality.read(quality.AUDITS)
        claims = quality.read(quality.CLAIMS)
        episodes = quality.read(quality.SPEAKERS)
        predictive = next(c for c in claims if c.get("claim_id") == "ms-297-001")
        predictive["verification_status"] = "independently_verified"
        self.assertTrue(any("Prospective forecast" in x for x in
                            quality.validate_evidence_audits(audits, claims, episodes)))

    def test_no_audit_uses_post_cutoff_evidence(self):
        audits = quality.read(quality.AUDITS)
        claims = quality.read(quality.CLAIMS)
        episodes = quality.read(quality.SPEAKERS)
        audits[0]["evidence_cutoff"] = "2026-10-16"
        self.assertTrue(any("frozen study cutoff" in x for x in
                            quality.validate_evidence_audits(audits, claims, episodes)))

if __name__ == "__main__":
    unittest.main()
