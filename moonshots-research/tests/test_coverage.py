import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import coverage as cov


class CoverageReportTests(unittest.TestCase):
    def test_parse_and_merge_windows(self):
        parts = cov.intervals(["00:01:00–00:03:00", "00:02:00–00:04:00"])
        self.assertEqual(180, cov.union_window_seconds(parts))

    def test_bad_window_is_rejected(self):
        with self.assertRaises(ValueError):
            cov.intervals(["00:09:00–00:08:00"])
        with self.assertRaises(ValueError):
            cov.intervals(["01:60:10–02:03:00"])

    def test_all_episodes_have_citation_windows(self):
        import json
        e = json.loads(cov.EPISODES.read_text())
        c = json.loads(cov.CLAIMS.read_text())
        a = json.loads(cov.AUDITS.read_text())
        rows = cov.coverage(e, c, a)
        self.assertEqual(24, len(rows))
        self.assertTrue(all(x["source_window_count"] >= 1 for x in rows))
        self.assertEqual(0, sum(x["full_audio_verified"] for x in rows))
        self.assertEqual(24, sum(x["full_transcript_verified"] for x in rows))
        self.assertEqual(len(c), sum(x["claims"] for x in rows))
        self.assertEqual(len(a), sum(x["second_pass_claim_audits"] for x in rows))

    def test_summary_is_not_a_coverage_percentage(self):
        import json
        rows = cov.coverage(json.loads(cov.EPISODES.read_text()),
                            json.loads(cov.CLAIMS.read_text()),
                            json.loads(cov.AUDITS.read_text()))
        content = cov.markdown(rows)
        self.assertIn("NOT listening-time proof", content)
        self.assertIn("**not** a coverage percentage", content)


if __name__ == "__main__":
    unittest.main()
