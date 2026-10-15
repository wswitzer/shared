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
        self.assertEqual(5, len(forecasts))
        self.assertEqual([], collector.validate_forecasts(forecasts, claims))

    def test_forecast_missing_support_is_rejected(self):
        forecasts = collector.load(collector.FORECASTS)
        claims = collector.load(collector.CLAIMS)
        forecasts[0]["supporting_claim_ids"] = ["missing-record"]
        self.assertTrue(any("missing claim" in x for x in collector.validate_forecasts(forecasts, claims)))

    def test_partial_review_is_not_full_transcript(self):
        episodes = collector.load(collector.EPISODES)
        self.assertEqual(7, sum(e.get("analysis_status") == "partial_review" for e in episodes))
        self.assertEqual(0, sum(e.get("transcript_status") == "ready" for e in episodes))
        summary = collector.report(episodes, collector.load(collector.CLAIMS), collector.load(collector.FORECASTS))
        self.assertIn("Episodes partially reviewed via public transcript: **7**", summary)
        self.assertIn("Full transcripts acquired locally: **0**", summary)

if __name__ == "__main__":
    unittest.main()
