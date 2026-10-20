"""Tasks 1.19 and 1.24: tests for the mapping tables and panel_yield.csv.

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


class TestMappings(unittest.TestCase):
    def test_every_current_district_maps_to_one_unit(self):
        rows = read("map_district_units.csv")
        districts = [r["current_district"] for r in rows]
        self.assertEqual(len(districts), 7)
        self.assertEqual(len(set(districts)), 7)
        self.assertEqual({r["model_unit"] for r in rows}, UNITS)

    def test_source_names_map_at_most_once(self):
        rows = read("map_district_units.csv")
        for col in ("icrisat_name", "ceda_census2011_name", "ceda_district_id"):
            names = [r[col] for r in rows if r[col]]
            self.assertEqual(len(names), len(set(names)), col)

    def test_crop_map_covers_the_four_crops_once(self):
        rows = read("map_crop_names.csv")
        self.assertEqual([r["crop_key"] for r in rows].count("tur"), 1)
        self.assertEqual({r["crop_key"] for r in rows}, CROPS)
        for col in ("icrisat_item", "ceda_commodity_id"):
            self.assertEqual(len({r[col] for r in rows}), 4, col)


class TestPanelYield(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel = read("panel_yield.csv")

    def test_keys_unique_and_known(self):
        keys = Counter((p["unit"], p["season"], p["crop"]) for p in self.panel)
        self.assertEqual(max(keys.values()), 1)
        self.assertTrue({p["unit"] for p in self.panel} <= UNITS)
        self.assertTrue({p["crop"] for p in self.panel} <= CROPS)

    def test_no_missing_or_zero_values(self):
        for p in self.panel:
            self.assertGreater(float(p["area_ha"]), 0)
            self.assertGreater(float(p["yield_kg_ha"]), 0)

    def test_unit_conversions(self):
        for p in self.panel:
            area, prod, yld = float(p["area_ha"]), float(p["production_t"]), float(p["yield_kg_ha"])
            self.assertAlmostEqual(prod * 1000 / area, yld, delta=yld * 0.01 + 1)
            self.assertAlmostEqual(float(p["yield_q_per_acre"]), yld / 100 / 2.471, places=2)

    def test_cotton_is_lint(self):
        for p in self.panel:
            self.assertEqual(p["yield_basis"], "lint" if p["crop"] == "cotton" else "grain")

    def test_out_of_range_rows_are_only_the_reviewed_ones(self):
        # Reviewed 2026-10-19: internally consistent in ICRISAT; kept as possible crop failures.
        expected = {("bidar", "1997-98", "tur"), ("kalaburagi_yadgir", "1992-93", "tur"),
                    ("kalaburagi_yadgir", "2009-10", "soybean")}
        flagged = {(p["unit"], p["season"], p["crop"]) for p in self.panel
                   if "yield_out_of_sanity_range" in p["flags"]}
        self.assertEqual(flagged, expected)

    def test_koppal_merge_years_flagged(self):
        koppal_years = {p["season"] for p in self.panel if p["unit"] == "koppal"}
        for p in self.panel:
            if p["unit"] == "raichur" and p["crop"] == "tur":
                self.assertEqual("includes_koppal" in p["flags"], p["season"] not in koppal_years)


if __name__ == "__main__":
    unittest.main()
