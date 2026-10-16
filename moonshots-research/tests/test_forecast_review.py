import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import forecast_review as tracker


class ForecastReviewTests(unittest.TestCase):
    def test_frozen_nine_forecasts_are_future_at_baseline(self):
        forecasts = tracker.load(tracker.FORECASTS)
        self.assertEqual(9, len(forecasts))
        report = tracker.plan(forecasts, date(2026, 10, 15))
        self.assertEqual(9, len(report))
        self.assertTrue(all(x["review_action"] == "not_due" for x in report))

    def test_near_horizon_is_flagged_without_auto_resolution(self):
        forecasts = tracker.load(tracker.FORECASTS)
        report = tracker.plan(forecasts, date(2027, 4, 1), warning_days=30)
        due = next(x for x in report if x["forecast_id"] == "fc-002")
        self.assertEqual("within_review_window", due["review_action"])
        self.assertEqual("open", due["status"])

    def test_overdue_remains_open_until_human_review(self):
        forecasts = tracker.load(tracker.FORECASTS)
        report = tracker.plan(forecasts, date(2027, 11, 1))
        self.assertEqual(9, len([x for x in report if x["review_action"] == "overdue_for_manual_adjudication"]))
        self.assertTrue(all(x["status"] == "open" for x in report))

    def test_resolved_status_is_never_overridden(self):
        forecasts = tracker.load(tracker.FORECASTS)
        forecasts[0]["status"] = "resolved_true"
        report = tracker.plan(forecasts, date(2028, 1, 1))
        prior = next(x for x in report if x["forecast_id"] == forecasts[0]["forecast_id"])
        self.assertEqual("already_marked_resolved_true", prior["review_action"])

    def test_negative_review_window_is_rejected(self):
        with self.assertRaises(ValueError):
            tracker.plan(tracker.load(tracker.FORECASTS), date(2026, 10, 15), -1)


if __name__ == "__main__":
    unittest.main()
