import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "experiments"))
import decision_eval as decision


class DecisionEvaluationTests(unittest.TestCase):
    def setUp(self):
        fixtures = HERE / "experiments" / "fixtures"
        self.gold = decision.read_rows(fixtures / "synthetic_gold.json")
        self.outputs = decision.read_rows(fixtures / "synthetic_predictions.json")

    def test_synthetic_demo_is_reproducible(self):
        summary = decision.evaluate(self.gold, self.outputs, confidence_threshold=0.8)
        self.assertEqual(8, summary["n"])
        self.assertEqual(6, summary["automated_decisions"])
        self.assertEqual(1, summary["errors"])
        self.assertEqual(0.75, summary["coverage"])
        self.assertEqual(0.8333, summary["selective_accuracy"])
        self.assertEqual(2, summary["confidence_deferrals"])
        self.assertEqual(0.008, summary["total_cost_usd"])
        self.assertEqual(10.0, summary["mean_latency_ms"])

    def test_raises_on_missing_predictions(self):
        with self.assertRaises(ValueError):
            decision.evaluate(self.gold, self.outputs[:-1])

    def test_raises_on_duplicate_prediction(self):
        with self.assertRaises(ValueError):
            decision.evaluate(self.gold, self.outputs + [dict(self.outputs[0])])

    def test_raises_on_out_of_range_confidence(self):
        rows = [dict(p) for p in self.outputs]
        rows[0]["confidence"] = 1.3
        with self.assertRaises(ValueError):
            decision.evaluate(self.gold, rows)

    def test_full_deferral_does_not_divide_by_zero(self):
        summary = decision.evaluate(self.gold, self.outputs, confidence_threshold=1)
        self.assertEqual(0, summary["automated_decisions"])
        self.assertIsNone(summary["selective_accuracy"])


if __name__ == "__main__":
    unittest.main()
