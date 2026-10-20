"""Tasks 1.36-1.42: tests for prices_monthly.csv and harvest_windows.csv.

Usage: python3 -m unittest discover -s tests
"""
import csv
import unittest
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
UNITS = {"kalaburagi_yadgir", "ballari_vijayanagara", "raichur", "koppal", "bidar"}
CROPS = {"tur", "maize", "soybean", "cotton"}


def read(name):
    with (DATA / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


class TestPricesMonthly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read("prices_monthly.csv")

    def test_keys_unique_and_known(self):
        keys = Counter((r["unit"], r["crop"], r["month"]) for r in self.rows)
        self.assertEqual(max(keys.values()), 1)
        self.assertTrue({r["unit"] for r in self.rows} <= UNITS)
        self.assertEqual({r["crop"] for r in self.rows}, CROPS)

    def test_prices_positive_and_plausible(self):
        # Rs per quintal for raw tur, maize, soybean and kapas, 2002-2025 [Assumption]
        for r in self.rows:
            self.assertTrue(300 <= float(r["modal_rs_per_q"]) <= 20000, r)

    def test_no_month_to_month_spikes_left(self):
        # Cleaning works at district level; a unit series can still move, but never by > 2.5x.
        series = {}
        for r in sorted(self.rows, key=lambda r: r["month"]):
            key = (r["unit"], r["crop"])
            price = float(r["modal_rs_per_q"])
            if key in series:
                prev_month, prev = series[key]
                if int(r["month"][:4]) * 12 + int(r["month"][5:]) - (int(prev_month[:4]) * 12 + int(prev_month[5:])) == 1:
                    self.assertTrue(0.4 <= price / prev <= 2.5, (key, r["month"], prev, price))
            series[key] = (r["month"], price)


class TestHarvestWindows(unittest.TestCase):
    def test_windows_contiguous_and_cover_a_large_share(self):
        rows = read("harvest_windows.csv")
        self.assertEqual({r["crop"] for r in rows}, CROPS)
        for r in rows:
            months = [int(m) for m in r["months"].split(";")]
            for a, b in zip(months, months[1:]):
                self.assertEqual(b, a % 12 + 1, r["crop"])  # consecutive, wrapping Dec -> Jan
            self.assertGreaterEqual(float(r["share_of_arrivals"]), 0.45, r["crop"])
            self.assertEqual(r["status"], "pending expert check")


if __name__ == "__main__":
    unittest.main()
