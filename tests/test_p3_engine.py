"""Tasks 3.25-3.29: Python reference engine tests, including the PRD 6.9 dummy cases (AC-07).

Usage: python3 -m unittest discover -s tests
"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from p3_engine import mulberry32, rank_crops, run, score  # noqa: E402

DATA = json.loads((ROOT / "data" / "engine_data.json").read_text())
FARMS = {f["id"]: f for f in json.loads((ROOT / "tests" / "test_farms.json").read_text())["farms"]}
RANKING = DATA["rules"]["ranking"]


def dummy(crop, low, base, loss=0.1, win=0.5, conf="Medium"):
    return {"crop": crop, "net_acre": {"p10": low, "p50": base}, "loss_chance": loss, "win_rate": win, "confidence": conf}


def flat_data(q=5.0, price=6000.0, cost=20000.0):
    """engine_data with no randomness: every draw has yield q, price `price`, cost `cost`."""
    d = copy.deepcopy(DATA)
    d["rules"]["adjustments"]["cost_band"] = [0.0, 0.0]
    key = "kalaburagi_yadgir|tur"
    d["yield_draws"][key].update(q_per_acre=[q] * len(d["yield_draws"][key]["weather_seasons"]), rel_errors=[0.0])
    d["price"][key].update(forecast=price, log_errors=[0.0], error_seasons=[2000])
    d["costs"]["tur"]["a2fl_per_acre"] = cost
    return d


class TestPRD69(unittest.TestCase):
    """PRD 6.9 (dummy values, made up to test the formulas)."""

    def test_scores(self):
        a, b = {"p10": -4000, "p50": 10000}, {"p10": 2000, "p50": 8000}
        for lam, sa, sb in ((0.7, 200, 3800), (0.4, 4400, 5600), (0.1, 8600, 7400)):
            self.assertAlmostEqual(score(a, lam), sa)
            self.assertAlmostEqual(score(b, lam), sb)

    def test_rank_flips_with_risk_preference(self):
        expected = {"cautious": ["B", "A"], "balanced": ["B", "A"], "growth": ["A", "B"]}
        for risk, order in expected.items():
            lam = RANKING["lambda"][risk]
            crops = [dummy("A", -4000, 10000, win=0.3), dummy("B", 2000, 8000, win=0.7)]
            for c in crops:
                c["score"] = score(c["net_acre"], lam)
            self.assertEqual([c["crop"] for c in rank_crops(crops, RANKING)], order, risk)

    def test_break_even_and_whole_field(self):
        res = run(flat_data(), {**FARMS["F01"], "soil": "deep_black"})   # Good tier, m = 1.0
        tur = next(c for c in res["ranked"] if c["crop"] == "tur")
        self.assertAlmostEqual(tur["break_even_price"], 4000)
        self.assertAlmostEqual(tur["break_even_yield"], 20000 / 6000)
        self.assertAlmostEqual(tur["net_acre"]["p50"], 10000)
        self.assertAlmostEqual(tur["net_field"]["p50"], 25000)          # 2 acres 20 guntas


class TestEngineCases(unittest.TestCase):
    def test_negative_returns(self):                                     # 3.26
        res = run(flat_data(q=1.0, price=1000.0, cost=20000.0), FARMS["F01"])
        tur = next(c for c in res["ranked"] if c["crop"] == "tur")
        self.assertLess(tur["net_acre"]["p90"], 0)
        self.assertEqual(tur["loss_chance"], 1.0)

    def test_missing_optional_inputs(self):                             # 3.27
        minimal = {k: FARMS["F01"][k] for k in ("district", "acres", "soil", "drainage", "water")}
        res = run(DATA, minimal)
        self.assertEqual(res["risk"], "balanced")
        self.assertEqual(len(res["ranked"]) + len(res["excluded"]), 4)

    def test_unknown_soil_and_drainage(self):                           # 3.28
        res = run(DATA, FARMS["F05"])
        self.assertTrue(all(c["confidence"] == "Low" for c in res["ranked"]))
        self.assertTrue(all(c["tier"] == "Fair" for c in res["ranked"]))

    def test_assured_irrigation(self):                                  # 3.29, 3.24
        res = run(DATA, FARMS["F06"])
        self.assertTrue(res["notices"])
        self.assertTrue(all(c["confidence"] == "Low" for c in res["ranked"]))

    def test_late_sowing_excludes_soybean(self):                        # 3.29
        res = run(DATA, FARMS["F08"])
        self.assertIn("soybean", [c["crop"] for c in res["excluded"]])
        self.assertIn("Late sowing", next(c for c in res["excluded"] if c["crop"] == "soybean")["excluded_reason"])

    def test_insufficient_data_shown_not_hidden(self):                  # 3.08, FR-04
        res = run(DATA, FARMS["F04"])                                    # Raichur: no soybean data
        soy = next(c for c in res["excluded"] if c["crop"] == "soybean")
        self.assertIn("Not enough local data", soy["excluded_reason"])

    def test_calibration_is_clipped(self):                              # 3.12
        res = run(DATA, {**FARMS["F09"], "own_yield": {"tur": 100.0}})
        tur = next(c for c in res["ranked"] if c["crop"] == "tur")
        self.assertTrue(tur["calibrated"])
        self.assertEqual(tur["multiplier"], 1.4)

    def test_protective_irrigation_raises_the_low_end(self):            # 3.13
        rainfed = run(DATA, {**FARMS["F02"], "water": "rainfed"})
        prot = run(DATA, FARMS["F02"])
        for a, b in zip(sorted(rainfed["ranked"], key=lambda c: c["crop"]), sorted(prot["ranked"], key=lambda c: c["crop"])):
            self.assertGreaterEqual(b["yield_q"]["p10"], a["yield_q"]["p10"])

    def test_cost_override_band(self):                                  # 3.17
        res = run(DATA, FARMS["F09"])
        tur = next(c for c in res["ranked"] if c["crop"] == "tur")
        self.assertEqual(tur["cost"]["base"], 18000)
        self.assertAlmostEqual(tur["cost"]["high"], 19800)

    def test_flags(self):                                               # 3.10
        res = run(DATA, FARMS["F04"])
        cotton = next(c for c in res["ranked"] if c["crop"] == "cotton")
        self.assertTrue(any("Cotton after cotton" in f for f in cotton["flags"]))

    def test_deterministic_and_win_rates_sum_to_one(self):
        a, b = run(DATA, FARMS["F03"]), run(DATA, FARMS["F03"])
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        self.assertAlmostEqual(sum(c["win_rate"] for c in a["ranked"]), 1.0)

    def test_prng_known_sequence(self):                                 # 3.07 (same as engine.js)
        r = mulberry32(20261020)
        self.assertEqual([r(), r(), r()], [0.264247833751142, 0.23858783044852316, 0.8627477055415511])


if __name__ == "__main__":
    unittest.main()
