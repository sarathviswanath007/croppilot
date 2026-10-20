"""Tasks 1.28-1.33: tests for the weather feature builder and weather_features.csv.

Usage: python3 -m unittest discover -s tests
"""
import csv
import datetime as dt
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from p1_build_weather_features import longest_dry_run, season_features  # noqa: E402

UNITS = {"kalaburagi_yadgir", "ballari_vijayanagara", "raichur", "koppal", "bidar"}


def kharif_days(year, rain_by_date=None, tmax=30.0):
    rain_by_date = rain_by_date or {}
    day, out = dt.date(year, 6, 1), []
    while day <= dt.date(year, 10, 31):
        out.append((day, rain_by_date.get(day, 0.0), tmax))
        day += dt.timedelta(days=1)
    return out


class TestFeatureFunctions(unittest.TestCase):
    def test_longest_dry_run(self):
        self.assertEqual(longest_dry_run([0, 0, 5, 0, 0, 0, 3]), 3)
        self.assertEqual(longest_dry_run([2.4, 2.4]), 2)       # below 2.5 mm counts as dry
        self.assertEqual(longest_dry_run([2.5, 10]), 0)        # 2.5 mm is a rainy day

    def test_all_dry_season(self):
        f = season_features(kharif_days(2000))
        self.assertEqual(f["rain_jjas"], 0)
        self.assertEqual(f["rainy_days_jjas"], 0)
        self.assertEqual(f["dry_spell_ja"], 62)                # every day of July and August
        self.assertEqual(f["tmax_as"], 30.0)

    def test_thresholds_and_windows(self):
        rains = {dt.date(2000, 6, 10): 2.5, dt.date(2000, 7, 31): 10.0,
                 dt.date(2000, 9, 5): 64.5, dt.date(2000, 10, 5): 64.4, dt.date(2000, 8, 1): 70.0}
        f = season_features(kharif_days(2000, rains))
        self.assertEqual(f["rainy_days_jjas"], 4)              # June, July, August, September days
        self.assertEqual(f["heavy_rain_days_so"], 1)           # August 70 mm is outside Sep-Oct
        self.assertEqual(f["rain_jjas"], 2.5 + 10 + 70 + 64.5)
        self.assertEqual(f["rain_jas"], 10 + 70 + 64.5)
        self.assertEqual(f["rain_oct"], 64.4)
        self.assertEqual(f["dry_spell_ja"], 30)                # 1-30 July


class TestWeatherFeaturesFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "data" / "weather_features.csv").open(encoding="utf-8") as f:
            cls.rows = list(csv.DictReader(f))

    def test_complete_grid(self):
        self.assertEqual({r["unit"] for r in self.rows}, UNITS)
        for unit in UNITS:
            years = sorted(int(r["season_start_year"]) for r in self.rows if r["unit"] == unit)
            self.assertEqual(years, list(range(1981, 2026)), unit)

    def test_internal_consistency(self):
        for r in self.rows:
            months = sum(float(r[f"rain_{m}"]) for m in ("jun", "jul", "aug", "sep"))
            self.assertAlmostEqual(months, float(r["rain_jjas"]), delta=0.3)
            self.assertLessEqual(float(r["rain_jas"]), float(r["rain_jjas"]))
            self.assertTrue(0 <= int(r["rainy_days_jjas"]) <= 122)
            self.assertTrue(0 <= int(r["dry_spell_ja"]) <= 62)
            self.assertTrue(20 <= float(r["tmax_as"]) <= 45)


if __name__ == "__main__":
    unittest.main()
