"""Tasks 2.01 and 2.04: tests for the as-of information set and the metrics module.

Usage: python3 -m unittest discover -s tests
"""
import datetime as dt
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import p2_metrics as M  # noqa: E402
from p2_asof import (load_msp, load_panel, msp_asof, prices_asof, weather_seasons_asof,  # noqa: E402
                     yields_asof)
from p2_models_yield import b1_predict  # noqa: E402


class TestAsOf(unittest.TestCase):
    def test_yields_stop_two_seasons_back(self):
        rows = yields_asof(load_panel(), 2015)
        self.assertEqual(max(r["season"] for r in rows), 2013)

    def test_no_small_seasons(self):
        self.assertFalse(any("below_500ha" in r["flags"] for r in load_panel()))

    def test_prices_stop_in_may(self):
        rows = [{"month": m} for m in ("2015-04", "2015-05", "2015-06", "2016-01")]
        self.assertEqual([r["month"] for r in prices_asof(rows, 2015)], ["2015-04", "2015-05"])

    def test_weather_excludes_target_season(self):
        self.assertEqual(weather_seasons_asof(1994), [1991, 1992, 1993])

    def test_msp_previous_season_unless_announced_by_31_may(self):
        msp = load_msp()
        self.assertEqual(msp_asof(msp, "tur", 2020)[1], 2019)          # no announcement date
        self.assertEqual(msp_asof(msp, "tur", 2026), (8450.0, 2026))   # announced 13 May 2026
        fake = {"tur": {2030: (1.0, dt.date(2030, 6, 1)), 2029: (2.0, None)}}
        self.assertEqual(msp_asof(fake, "tur", 2030), (2.0, 2029))     # June: too late

    def test_b1_uses_only_published_seasons(self):
        rows = [{"unit": "bidar", "crop": "tur", "season": s, "yield_kg_ha": float(s)} for s in range(2000, 2012)]
        # decision for 2011: published through 2009 -> mean of 2005..2009
        self.assertEqual(b1_predict(rows, "bidar", "tur", 2011), 2007.0)


class TestMetrics(unittest.TestCase):
    def test_basic(self):
        self.assertAlmostEqual(M.mae([10, 20], [12, 17]), 2.5)
        self.assertAlmostEqual(M.mape([10, 20], [12, 18]), 0.15)
        self.assertAlmostEqual(M.skill(8, 10), 0.2)
        self.assertIsNone(M.skill(8, 0))
        self.assertAlmostEqual(M.coverage([1, 5, 9], [0, 6, 8], [2, 7, 10]), 2 / 3)

    def test_direction(self):
        # anchor 100: up/up right, down/up wrong, flat forecast wrong, unchanged actual left out
        self.assertAlmostEqual(M.direction_accuracy([110, 90, 120, 100], [105, 104, 100, 130], [100] * 4), 1 / 3)

    def test_bootstrap_is_seeded(self):
        x = [1.0, 2.0, 3.0, 4.0]
        f = lambda idx: float(sum(x[i] for i in idx) / len(idx))  # noqa: E731
        self.assertEqual(M.bootstrap_ci(f, [1, 1, 2, 2]), M.bootstrap_ci(f, [1, 1, 2, 2]))


if __name__ == "__main__":
    unittest.main()
