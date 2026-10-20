"""Tasks 3.31, 3.32: assemble data/engine_data.json from the Phase 1-2 outputs (contract v0.2).

Sources:
  yield_draws, drivers   data/export_yield_draws.json, data/drivers.json        (Phase 2)
  price                  data/export_price.json                                 (Phase 2)
  models, backtest       data/model_selection.csv, backtest_*_metrics.csv       (Phase 2)
  costs                  data/costs.csv (A2+FL per acre inflated to Kharif 2027, D-09)
  msp                    data/msp.csv, season 2026-27 (latest announced; Kharif 2027 MSP unknown)
  weather                data/weather_features.csv rain_jas, 1991-2025
  sufficiency            data/panel_yield_coverage.csv
  rules                  config/rules.json
Confidence badge per unit x crop from selection_rules.md section 3 (frozen thresholds), using
the shipped yield model's crop-level skill and coverage and the unit's seasons of data. The farm
conditions in section 3 (unknown soil and drainage, assured irrigation) are applied by the engine.

Output: data/engine_data.json (validated; size logged for NFR-04)
Usage:  python3 scripts/p3_build_engine_data.py
"""
import json
import subprocess
import sys

from p2_asof import CROPS, DATA, ROOT, UNITS, read_csv

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
UNIT_DISTRICTS = {"kalaburagi_yadgir": ["Kalaburagi", "Yadgir"], "bidar": ["Bidar"], "raichur": ["Raichur"],
                  "koppal": ["Koppal"], "ballari_vijayanagara": ["Ballari", "Vijayanagara"]}
CROP_INFO = {  # sowing windows are [Assumption] (PRD 6.2), to confirm with the expert
    "tur": {"name": "Tur (red gram)", "sowing_window_end": "mid-August", "occupies_rabi": True},
    "maize": {"name": "Maize", "sowing_window_end": "to confirm", "occupies_rabi": False},
    "soybean": {"name": "Soybean", "sowing_window_end": "mid-July", "occupies_rabi": False},
    "cotton": {"name": "Cotton (kapas)", "sowing_window_end": "mid-August", "occupies_rabi": True},
}
YIELD_MODEL_NAMES = {"B1": "5-season average (baseline B1)", "M1": "Ridge regression (ML)",
                     "M2": "Gradient boosting (ML)"}
PRICE_MODEL_NAMES = {"P1": "May price carried forward (baseline P1)",
                     "P2": "Last season's harvest price (baseline P2)", "ML": "Ridge regression (ML)"}


def confidence(is_ml, skill, cov, seasons):
    """selection_rules.md v1.0 section 3, model-based part."""
    if cov is None:
        return "Low"
    if is_ml and skill >= 0.10 and 0.70 <= cov <= 0.90 and seasons >= 15:
        return "High"
    if (skill > 0 or not is_ml) and 0.60 <= cov <= 0.95 and seasons >= 10:
        return "Medium"
    return "Low"


def num(x):
    return float(x) if x not in ("", None) else None


def main():
    ydraws = json.loads((DATA / "export_yield_draws.json").read_text())["yield_draws"]
    prices = json.loads((DATA / "export_price.json").read_text())["price"]
    drivers = json.loads((DATA / "drivers.json").read_text())["drivers"]
    rules = json.loads((ROOT / "config" / "rules.json").read_text())
    rules.pop("_comment", None)
    selection = {r["crop"]: r for r in read_csv(DATA / "model_selection.csv")}
    ym = {(r["crop"], r["model"]): r for r in read_csv(DATA / "backtest_yield_metrics.csv")}
    pm = {(r["crop"], r["model"]): r for r in read_csv(DATA / "backtest_price_metrics.csv")}
    windows = {r["crop"]: [MONTHS[int(m) - 1] for m in r["months"].split(";")]
               for r in read_csv(DATA / "harvest_windows.csv")}
    coverage = {(r["unit"], r["crop"]): r for r in read_csv(DATA / "panel_yield_coverage.csv")}

    weather = {}
    for r in read_csv(DATA / "weather_features.csv"):
        if int(r["season_start_year"]) >= 1991:
            w = weather.setdefault(r["unit"], {"seasons": [], "jas_rain_mm": [], "label": "Data"})
            w["seasons"].append(int(r["season_start_year"]))
            w["jas_rain_mm"].append(float(r["rain_jas"]))

    yield_draws = {k: {f: v[f] for f in ("weather_seasons", "q_per_acre", "rel_errors",
                                         "five_season_mean_q_per_acre", "data_through", "model", "label", "basis")}
                   for k, v in ydraws.items()}
    price = {}
    for k, v in prices.items():
        entry = {f: v[f] for f in ("forecast", "log_errors", "error_seasons", "model", "label")}
        if v.get("harvest_window_cv") is not None:
            entry["harvest_window_cv"] = v["harvest_window_cv"]
        entry["data_through"] = v["price_data_through"]
        entry["anchor_month"] = v["anchor_month"]
        if v.get("borrowed_from_units"):
            entry["borrowed_from_units"] = v["borrowed_from_units"]
        price[k] = entry

    models, backtest = {}, {}
    for crop in CROPS:
        sel = selection[crop]
        yrow, prow = ym[(crop, sel["yield_model"])], pm[(crop, sel["price_model"])]
        b1 = ym[(crop, "B1")]
        models[crop] = {
            "yield_model": YIELD_MODEL_NAMES[sel["yield_model"]], "yield_reason": sel["yield_reason"],
            "yield_is_ml": sel["yield_model"] in ("M1", "M2"),
            "yield_mae_kg_ha": num(yrow["mae_kg_ha"]), "b1_mae_kg_ha": num(b1["mae_kg_ha"]),
            "yield_skill": num(yrow["skill_vs_b1"]),
            "yield_skill_ci90": [num(yrow["skill_ci90_low"]), num(yrow["skill_ci90_high"])],
            "yield_coverage": num(yrow["coverage_10_90"]), "yield_n_rows": int(yrow["n_rows"]),
            "yield_test_seasons": f"{yrow['first_season']}-{yrow['last_season']}",
            "price_model": PRICE_MODEL_NAMES[sel["price_model"]], "price_reason": sel["price_reason"],
            "price_is_ml": sel["price_model"] == "ML",
            "price_mape": num(prow["mape"]), "price_skill": num(prow["skill_vs_better_baseline"]),
            "price_coverage": num(prow["coverage_10_90"]), "price_n_rows": int(prow["n_rows"]),
            "price_test_seasons": f"{prow['first_season']}-{prow['last_season']}",
            "label": "Prediction (backtest)",
        }
        for unit in UNITS:
            cov_row = coverage[(unit, crop)]
            seasons = int(cov_row["seasons_ge_500ha"])
            if cov_row["passes_sufficiency"] != "True":
                continue
            m = models[crop]
            backtest[f"{unit}|{crop}"] = {
                "yield_skill": m["yield_skill"], "price_skill": m["price_skill"],
                "coverage": m["yield_coverage"], "n": seasons,
                "confidence": confidence(m["yield_is_ml"], m["yield_skill"], m["yield_coverage"], seasons),
            }

    sufficiency = {f"{r['unit']}|{r['crop']}": {"seasons_ok": int(r["seasons_ge_500ha"]),
                                               "passes": r["passes_sufficiency"] == "True"}
                   for r in read_csv(DATA / "panel_yield_coverage.csv")}
    costs = {}
    for r in read_csv(DATA / "costs.csv"):
        costs[r["crop"]] = {"a2fl_per_acre": float(r["a2fl_per_acre"]), "c2_per_acre": num(r["c2_per_acre"]),
                            "source": r["source"], "cost_year": r["cost_year"],
                            "inflation_factor": float(r["inflation_factor"]),
                            "band": [float(r["band_low"]), float(r["band_high"])], "label": "Assumption"}
    msp = {}
    for r in read_csv(DATA / "msp.csv"):
        if r["season"] == "2026-27":
            msp[r["crop"]] = {"value": float(r["msp_rs_per_q"]), "season": r["season"], "source": r["source"],
                              "label": "Data", **({"announced": r["announced"]} if r["announced"] else {})}
    sources = [{"id": r["source"], "name": r["file"], "url": r["url"], "downloaded": r["downloaded"],
                "coverage": r["coverage"]} for r in read_csv(ROOT / "raw" / "raw_sources_log.csv")]

    data = {
        "meta": {"version": "0.2", "built": "2026-10-20", "target_season": "Kharif 2027",
                 "decision_date": "2027-05-31", "mock": False, "sources": sources},
        "units": UNIT_DISTRICTS,
        "crops": {c: {"name": CROP_INFO[c]["name"], "harvest_window": windows[c], "window_label": "Assumption",
                      "sowing_window_end": CROP_INFO[c]["sowing_window_end"],
                      "occupies_rabi": CROP_INFO[c]["occupies_rabi"]} for c in CROPS},
        "weather": weather, "sufficiency": sufficiency, "yield_draws": yield_draws, "price": price,
        "costs": costs, "msp": msp, "rules": rules, "backtest": backtest,
        "drivers": drivers, "models": models,
    }
    out = DATA / "engine_data.json"
    out.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False))
    print(f"engine_data.json: {out.stat().st_size / 1024:.1f} KB (NFR-04 limit 1,000 KB)")
    for k, v in backtest.items():
        print(f"  {k:30} confidence {v['confidence']}")
    sys.exit(subprocess.call([sys.executable, str(ROOT / "scripts" / "p0_validate_engine_data.py"), str(out)]))


if __name__ == "__main__":
    main()
