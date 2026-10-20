"""Task 0.30: build engine_data.mock.json for UI and engine work before real data exists.

Every number here is a made-up placeholder, NOT data and NOT a prediction.
meta.mock is true so the dashboard can show a MOCK DATA banner.

Usage: python3 scripts/p0_make_mock_engine_data.py
"""
import json
import math
import random
from pathlib import Path

SEED = 20261019
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "contract" / "engine_data.mock.json"

UNITS = {
    "kalaburagi_yadgir": ["Kalaburagi", "Yadgir"],
    "ballari_vijayanagara": ["Ballari", "Vijayanagara"],
    "raichur": ["Raichur"],
    "koppal": ["Koppal"],
    "bidar": ["Bidar"],
}

# Harvest windows, sowing windows and occupancy come from PRD §4.3 and §6.2 [Assumption].
CROPS = {
    "tur": {"name": "Tur (red gram)", "harvest_window": ["Dec", "Jan", "Feb"],
            "window_label": "Assumption", "sowing_window_end": "mid-August", "occupies_rabi": True},
    # Maize replaced green gram (decision D-05). Its windows are placeholders until task 1.42.
    "maize": {"name": "Maize", "harvest_window": ["Oct", "Nov"],
              "window_label": "Assumption", "sowing_window_end": "to confirm", "occupies_rabi": False},
    "soybean": {"name": "Soybean", "harvest_window": ["Oct", "Nov"],
                "window_label": "Assumption", "sowing_window_end": "mid-July", "occupies_rabi": False},
    "cotton": {"name": "Cotton (kapas)", "harvest_window": ["Nov", "Dec", "Jan"],
               "window_label": "Assumption", "sowing_window_end": "mid-August", "occupies_rabi": True},
}

# Dummy central values only, chosen so the UI has something plausible-looking to render.
DUMMY = {  # crop: (yield q/acre, price Rs/q, cost Rs/acre, msp Rs/q)
    "tur": (4.0, 7000, 15000, 7000),
    "maize": (13.0, 2000, 20000, 2200),
    "soybean": (5.0, 4500, 16000, 5000),
    "cotton": (6.5, 7000, 25000, 7000),
}

WEATHER_SEASONS = list(range(1991, 2026))  # 35 seasons, PRD §4.4
PRICE_ERROR_SEASONS = list(range(2012, 2026))

# Suitability matrix and multipliers from PRD §6.2 [Assumption — draft, unreviewed].
# The maize column is not in the PRD: a placeholder for the expert to replace in Phase 6.
SUITABILITY = {
    "deep_black_drains_well": {"tur": "Good", "maize": "Fair", "soybean": "Good", "cotton": "Good"},
    "medium_black_drains_well": {"tur": "Good", "maize": "Fair", "soybean": "Good", "cotton": "Good"},
    "shallow_black": {"tur": "Fair", "maize": "Fair", "soybean": "Fair", "cotton": "Marginal"},
    "red": {"tur": "Fair", "maize": "Fair", "soybean": "Fair", "cotton": "Fair"},
    "waterlogs": {"tur": "Marginal", "maize": "Marginal", "soybean": "Marginal", "cotton": "Fair"},
    "mixed_or_unknown": {"tur": "Fair", "maize": "Fair", "soybean": "Fair", "cotton": "Fair"},
}


def r2(x):
    return round(x, 2)


def build():
    rng = random.Random(SEED)
    data = {
        "meta": {
            "version": "0.1-draft",
            "built": "2026-10-19",
            "target_season": "Kharif 2027",
            "decision_date": "2027-05-31",
            "mock": True,
            "sources": [{"id": "MOCK", "name": "Placeholder values for UI development",
                         "downloaded": "2026-10-19", "coverage": "none: not real data"}],
        },
        "units": UNITS,
        "crops": CROPS,
        "weather": {},
        "sufficiency": {},
        "yield_draws": {},
        "price": {},
        "costs": {},
        "msp": {},
        "rules": {
            "review_status": "unreviewed",
            "suitability": SUITABILITY,
            "multipliers": {"Good": 1.0, "Fair": 0.9, "Marginal": 0.75},
            "exclusions": {"min_seasons": 10, "min_area_ha": 500,
                           "late_sowing_excluded": ["soybean"]},
            "ranking": {"lambda": {"cautious": 0.7, "balanced": 0.4, "growth": 0.1},
                        "tie_band": 0.05, "close_call_pp": 10},
            "adjustments": {"calibration_clip": [0.6, 1.4], "protective_irrigation_alpha": 0.5,
                            "cost_band": [-0.10, 0.15], "override_band": [-0.10, 0.10],
                            "n_draws": 2000},
        },
        "backtest": {},
    }

    for unit in UNITS:
        data["weather"][unit] = {
            "seasons": WEATHER_SEASONS,
            "jas_rain_mm": [r2(max(150.0, rng.gauss(520, 130))) for _ in WEATHER_SEASONS],
            "label": "Data",
        }

    for crop, (y, p, c, m) in DUMMY.items():
        data["costs"][crop] = {"a2fl_per_acre": c, "c2_per_acre": None, "source": "MOCK",
                               "cost_year": "2023-24", "inflation_factor": 1.0,
                               "band": [-0.10, 0.15], "label": "Assumption"}
        data["msp"][crop] = {"value": m, "season": "2026-27", "source": "MOCK",
                             "announced": "2026-05-13", "label": "Data"}
        for unit in UNITS:
            key = f"{unit}|{crop}"
            # Leave one unit short of data so the "not enough local data" path is exercised.
            passes = not (unit == "koppal" and crop == "soybean")
            data["sufficiency"][key] = {"seasons_ok": 18 if passes else 6, "passes": passes}
            unit_shift = rng.uniform(0.85, 1.15)
            data["yield_draws"][key] = {
                "weather_seasons": WEATHER_SEASONS,
                "q_per_acre": [r2(max(0.2, y * unit_shift * rng.gauss(1, 0.25))) for _ in WEATHER_SEASONS],
                "rel_errors": [r2(rng.gauss(0, 0.15)) for _ in range(14)],
                "five_season_mean_q_per_acre": r2(y * unit_shift),
                "data_through": "2023-24",
                "model": "ridge" if crop != "maize" else "baseline_b1",
                "label": "Prediction",
            }
            data["price"][key] = {
                "forecast": round(p * rng.uniform(0.95, 1.05)),
                "log_errors": [round(rng.gauss(0, 0.15), 3) for _ in PRICE_ERROR_SEASONS],
                "error_seasons": PRICE_ERROR_SEASONS,
                "harvest_window_cv": r2(rng.uniform(0.1, 0.3)),
                "model": "persistence",
                "label": "Prediction",
            }
            data["backtest"][key] = {"yield_skill": r2(rng.uniform(-0.05, 0.2)), "price_skill": None,
                                     "coverage": r2(rng.uniform(0.6, 0.9)), "n": 12,
                                     "confidence": rng.choice(["High", "Medium", "Low"])}
    return data


def main():
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
