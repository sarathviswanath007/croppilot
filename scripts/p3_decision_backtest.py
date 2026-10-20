"""Task 3.37: decision backtest (PRD 9.3). Does CropPilot's top pick beat simple heuristics?

For each test season T (2012-2019, the seasons with published yields) and model unit:
  1. Rebuild the engine inputs as known on 31 May T: the shipped yield model per crop (selection
     rules v1.0) refitted on yields <= T-2, run under weather seasons 1991..T-1 with leak-free
     residuals; the shipped price model per crop with May-T anchors and past errors only.
  2. Rank a standard farm with the Python engine: rainfed, balanced risk, district-average
     conditions (suitability multiplier 1.0 for every crop), no farmer overrides.
  3. Realised net return per crop = actual district yield T x actual harvest-window price T - cost T.
  4. Compare CropPilot's top pick with "always tur" and "last season's most profitable crop"
     (by realised return in T-1, which a farmer knows from their own experience).
A crop enters a unit-season only if the engine could rank it AND it has an actual yield and an
actual harvest-window price. Unit-seasons with fewer than 2 such crops are skipped.

[Assumption] Cost in season T = CACP Karnataka A2+FL 2024-25 x 1.03^(T - 2024), the same flat
3%/yr as D-09 run backwards. The same factor applies to every crop, so it shifts all returns but
barely changes which crop is best.
[Assumption] The sufficiency rule uses the full-sample coverage table; confidence is set to
Medium for every crop (it only affects near-ties).

Output: decision_backtest.md, data/decision_backtest_rows.csv
Usage:  python3 scripts/p3_decision_backtest.py   (about 2 minutes)
"""
import ast
import copy
import json
import math

import numpy as np

from p2_asof import CROPS, DATA, ROOT, UNITS, YIELD_PUBLICATION_LAG, read_csv, yields_asof
from p2_backtest import inner_cv
from p2_build_features_yield import load_weather
from p2_export import GINNING_OUTTURN, KG_HA_TO_Q_ACRE
from p2_models_yield import PooledHGB, b1_predict, baseline_residuals, relative_mae_loss
from p2_run_price_backtest import ALPHAS, MIN_FIT_ROWS, PRICE_LAG, RidgePrice, abs_loss, baseline_log_pred
from p2_run_price_backtest import load_rows as load_price_rows
from p2_run_yield_backtest import load_rows as load_yield_rows
from p2_run_yield_backtest import write
from p3_engine import run

SEASONS = range(2012, 2020)
COST_GROWTH = 1.03          # [Assumption] D-09, applied backwards
MODEL_NAMES = {"B1": "baseline_b1", "M2": "hgbr", "M1": "ridge", "P1": "persistence", "P2": "seasonal_naive", "ML": "ridge"}


def q_acre(kg_ha, crop):
    q = kg_ha * KG_HA_TO_Q_ACRE
    return q / GINNING_OUTTURN if crop == "cotton" else q


def main():
    yrows = load_yield_rows()
    prows = load_price_rows()
    feats = {(r["unit"], r["crop"], int(r["season"])): r for r in read_csv(DATA / "features_price.csv")}
    weather = load_weather()
    wx_rows = read_csv(DATA / "weather_features.csv")
    selection = {r["crop"]: r for r in read_csv(DATA / "model_selection.csv")}
    bt_params = {int(r["season"]): ast.literal_eval(r["params"]) for r in read_csv(DATA / "backtest_yield_rows.csv")
                 if r["model"] == "M2" and r["params"].startswith("{")}
    base_cost = {r["crop"]: float(r["a2fl_per_acre_cost_year"]) for r in read_csv(DATA / "costs.csv")}
    base_data = json.loads((DATA / "engine_data.json").read_text())
    actual_yield = {(r["unit"], r["crop"], r["season"]): r["yield_kg_ha"] for r in yrows}
    actual_price = {k: float(v["window_price"]) for k, v in feats.items() if v["window_price"]}

    def realised(unit, crop, season):
        y, p = actual_yield.get((unit, crop, season)), actual_price.get((unit, crop, season))
        if y is None or p is None:
            return None
        return q_acre(y, crop) * p - base_cost[crop] * COST_GROWTH ** (season - 2024)

    out = []
    for T in SEASONS:
        train = yields_asof(yrows, T)
        w_seasons = list(range(1991, T))
        d = copy.deepcopy(base_data)
        d["rules"]["suitability"]["mixed_or_unknown"] = {c: "Good" for c in CROPS}   # district-average conditions
        d["weather"] = {u: {"seasons": w_seasons, "label": "Data",
                            "jas_rain_mm": [float(next(r["rain_jas"] for r in wx_rows if r["unit"] == u and int(r["season_start_year"]) == s)) for s in w_seasons]}
                        for u in UNITS}
        d["yield_draws"], d["price"] = {}, {}
        d["costs"] = {c: {**d["costs"][c], "a2fl_per_acre": base_cost[c] * COST_GROWTH ** (T - 2024)} for c in CROPS}
        d["backtest"] = {k: {**v, "confidence": "Medium"} for k, v in d["backtest"].items()}

        ptrain = [r for r in prows if r["season"] <= T - PRICE_LAG]
        alpha, p_oos = inner_cv(ptrain, RidgePrice, ALPHAS, abs_loss, PRICE_LAG, MIN_FIT_ROWS, target="target")
        ridge = RidgePrice(alpha if alpha is not None else 10.0).fit(ptrain)

        for crop in CROPS:
            ymodel, pmodel = selection[crop]["yield_model"], selection[crop]["price_model"]
            if ymodel == "M2":
                params = bt_params[T]
                _, oos = inner_cv(train, PooledHGB, [params], relative_mae_loss, YIELD_PUBLICATION_LAG, 50)
                rel = [r["yield_kg_ha"] / p - 1 for r, p in oos if r["crop"] == crop]
                model = PooledHGB(params).fit(train)
            else:
                rel = baseline_residuals(yrows, crop, b1_predict, T - YIELD_PUBLICATION_LAG)
                model = None
            if pmodel == "ML":
                perr = sorted((r["season"], r["target"] - p) for r, p in p_oos if r["crop"] == crop)
            else:
                perr = sorted((r["season"], r["target"] - baseline_log_pred(pmodel, r)) for r in ptrain if r["crop"] == crop)
            for unit in UNITS:
                key = f"{unit}|{crop}"
                if not d["sufficiency"][key]["passes"]:
                    continue
                b1 = b1_predict(yrows, unit, crop, T)
                f = feats.get((unit, crop, T))
                if b1 is None or not f or not f["may_price"] or len(rel) < 10 or len(perr) < 5:
                    continue
                if model is None:
                    preds = [b1] * len(w_seasons)
                else:
                    preds = model.predict([{"unit": unit, "crop": crop, "season": T, **weather[(unit, s)]} for s in w_seasons])
                may = float(f["may_price"])
                if pmodel == "P1":
                    logp = 0.0
                elif pmodel == "P2":
                    if not f["f_last_window"]:
                        continue
                    logp = float(f["f_last_window"])
                else:
                    if not f["f_last_window"]:
                        continue
                    logp = float(ridge.predict([{"crop": crop, **{k: float(f[k]) for k in ("f_mean12", "f_last_window", "f_msp")}}])[0])
                d["yield_draws"][key] = {"weather_seasons": w_seasons, "q_per_acre": [q_acre(float(p), crop) for p in preds],
                                         "rel_errors": rel, "five_season_mean_q_per_acre": q_acre(b1, crop),
                                         "data_through": "", "model": MODEL_NAMES[ymodel], "label": "Prediction"}
                d["price"][key] = {"forecast": may * math.exp(logp), "log_errors": [e for _, e in perr],
                                   "error_seasons": [s for s, _ in perr], "model": MODEL_NAMES[pmodel], "label": "Prediction"}

        for unit in UNITS:
            profile = {"district": d["units"][unit][0], "acres": 1, "guntas": 0, "soil": "unknown",
                       "drainage": "drains_well", "water": "rainfed", "previous_crop": "none", "risk": "balanced"}
            res = run(d, profile)
            ranked = [c["crop"] for c in res["ranked"]]
            real = {c: realised(unit, c, T) for c in ranked}
            comparable = [c for c in ranked if real[c] is not None]
            if len(comparable) < 2:
                continue
            best = max(comparable, key=lambda c: real[c])
            prev = {c: realised(unit, c, T - 1) for c in comparable}
            prev_ok = [c for c in comparable if prev[c] is not None]
            picks = {"croppilot": comparable[0], "always_tur": "tur" if "tur" in comparable else None,
                     "last_best": max(prev_ok, key=lambda c: prev[c]) if prev_ok else None}
            row = {"season": T, "unit": unit, "crops": ";".join(comparable), "best": best, "best_return": round(real[best])}
            for s, c in picks.items():
                row[f"{s}_pick"] = c or ""
                row[f"{s}_return"] = round(real[c]) if c else ""
                row[f"{s}_regret"] = round(real[best] - real[c]) if c else ""
            out.append(row)
        print(f"season {T}: {sum(1 for r in out if r['season'] == T)} unit-seasons")

    write(DATA / "decision_backtest_rows.csv", out)
    report(out)


def report(rows):
    full = [r for r in rows if all(r[f"{s}_pick"] for s in ("croppilot", "always_tur", "last_best"))]
    lines = ["# Polaris CropPilot: Decision Backtest (task 3.37, PRD 9.3)", "",
             "**Run:** 20 October 2026 · `scripts/p3_decision_backtest.py` · rows in `data/decision_backtest_rows.csv`", "",
             "**What this is.** For each season 2012–2019 and each district unit, CropPilot ranked a standard farm "
             "(rain-fed, balanced risk, district-average soil) using only what was known on 31 May that year. "
             "Each crop's *realised* profit per acre was then computed from that season's actual district yield, actual "
             "harvest-window price and cost. Regret = the best crop's realised profit minus the chosen crop's. `[Prediction (backtest)]`", "",
             "**Caveats.** These are district averages, not farm outcomes. Costs before 2024-25 are back-cast at 3% a year "
             "`[Assumption]`. Only crops with both an actual yield and an actual market price that season are compared, so "
             "some unit-seasons compare 2 or 3 crops, not 4. Seasons are few (8), so differences are uncertain.", "",
             f"**Unit-seasons where all three strategies could pick:** {len(full)} (of {len(rows)} with ≥ 2 comparable crops).", "",
             "| Strategy | Mean regret (₹/acre) | Median regret | 10th-percentile realised profit (₹/acre) | Picked the best crop |",
             "|---|---|---|---|---|"]
    names = {"croppilot": "CropPilot top pick", "always_tur": "Always tur", "last_best": "Last season's most profitable"}
    for s, label in names.items():
        reg = np.array([r[f"{s}_regret"] for r in full], dtype=float)
        ret = np.array([r[f"{s}_return"] for r in full], dtype=float)
        hit = sum(1 for r in full if r[f"{s}_pick"] == r["best"])
        lines.append(f"| {label} | {reg.mean():,.0f} | {np.median(reg):,.0f} | {np.percentile(ret, 10):,.0f} | {hit} of {len(full)} ({hit / len(full):.0%}) |")
    lines += ["", "## Per season", "", "| Season | Unit-seasons | CropPilot mean regret | Always-tur mean regret | Last-best mean regret |", "|---|---|---|---|---|"]
    for T in sorted({r["season"] for r in full}):
        rs = [r for r in full if r["season"] == T]
        m = lambda s: np.mean([r[f"{s}_regret"] for r in rs])  # noqa: E731
        lines.append(f"| {T} | {len(rs)} | {m('croppilot'):,.0f} | {m('always_tur'):,.0f} | {m('last_best'):,.0f} |")
    lines += ["", "## What CropPilot picked", ""]
    picks = {}
    for r in full:
        picks[r["croppilot_pick"]] = picks.get(r["croppilot_pick"], 0) + 1
    lines.append(", ".join(f"{c}: {n}" for c, n in sorted(picks.items(), key=lambda x: -x[1])) + ".")
    (ROOT / "decision_backtest.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[12:20]))


if __name__ == "__main__":
    main()
