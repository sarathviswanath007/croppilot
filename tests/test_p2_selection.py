"""Tasks 2.23, 2.24: the coded selection rules match selection_rules.md v1.0.

Usage: python3 -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from p2_select_models import select_price, select_yield  # noqa: E402


def ym(b1, m1, m2):
    return {m: {"mae_kg_ha": str(v), "skill_vs_b1": "0"} for m, v in (("B1", b1), ("M1", m1), ("M2", m2))}


def pm(skill, direction, better="P2"):
    return {"ML": {"better_baseline": better, "skill_vs_better_baseline": str(skill),
                   "direction_accuracy": str(direction)}}


class TestYieldRule(unittest.TestCase):
    def test_model_must_beat_b1(self):
        self.assertEqual(select_yield(ym(100, 101, 105))[0], "B1")

    def test_best_candidate_wins_outside_tie(self):
        self.assertEqual(select_yield(ym(100, 95, 90))[0], "M2")

    def test_tie_within_1pct_goes_to_simpler(self):
        self.assertEqual(select_yield(ym(100, 99.5, 102))[0], "B1")   # M1 beats B1 by 0.5%
        self.assertEqual(select_yield(ym(100, 90.5, 90))[0], "M1")    # M1 within 1% of M2


class TestPriceRule(unittest.TestCase):
    def test_both_conditions_needed(self):
        self.assertEqual(select_price(pm(0.05, 0.51))[0], "ML")
        self.assertEqual(select_price(pm(0.049, 0.9))[0], "P2")
        self.assertEqual(select_price(pm(0.2, 0.5, better="P1"))[0], "P1")


if __name__ == "__main__":
    unittest.main()
