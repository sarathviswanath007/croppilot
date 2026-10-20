"""Tasks 2.27, 2.30, 2.31: Kharif 2027 exports for the engine, using the models chosen in
data/model_selection.csv (selection_rules.md v1.0).

Yield (2.30): for each unit x crop passing the sufficiency rule, the chosen model's prediction
for season 2027 under every weather season 1991 .. 2025 (the latest in weather_features.csv),
plus the chosen model's backtest relative residuals (2012-2019 hindcasts) for (1 + e) draws.
Trained on everything published by 31 May 2027 (yields end 2019-20, gap G3).
Converted to quintals per acre; cotton lint -> kapas with GINNING_OUTTURN.

Price (2.31): forecast of the harvest-window price as of 31 May 2025 (decision D-14), with the
chosen model's past log-errors keyed by season (for paired-season sampling, PRD 4.4).
Baselines: errors over every past season of the unit; ML: its 2012-2024 backtest errors. A unit
with < MIN_UNIT_ERRORS errors borrows the crop's errors from all units (flagged).
[Assumption] D-17 (export only; the backtest is unchanged): an anchor month with arrivals below
MIN_ANCHOR_ARRIVALS_T is not used. A unit with no usable anchor borrows the median of the other
units' forecasts for that crop, with the crop's errors from all units (flagged). If no unit
has a usable anchor on 31 May 2025, the crop's forecasts are made as of 31 May 2024.

Drivers (2.27): permutation importance of the chosen ML yield model on its training rows, with
the direction of each effect (prediction at the feature's 75th vs 25th percentile). Crops on B1
have no weather drivers: B1 is the recent five-season mean.

Outputs: data/export_yield_draws.json, data/export_price.json, data/drivers.json
Usage:   python3 scripts/p2_export.py
"""
import json
import math

import numpy as np

from p2_asof import CROPS, DATA, UNITS, YIELD_PUBLICATION_LAG, read_csv, yields_asof
from p2_backtest import SEED, inner_cv
from p2_build_features_price import PRICE_FEATURES
from p2_build_features_yield import WEATHER_FEATURES, load_weather
from p2_models_yield import (HGB_GRID, HGB_MIN_FIT_ROWS, RIDGE_ALPHAS, RIDGE_MIN_FIT_ROWS, PooledHGB,
                             RidgeYield, b1_predict, mae_loss, relative_mae_loss)
from p2_run_price_backtest import ALPHAS as PRICE_ALPHAS
from p2_run_price_backtest import MIN_FIT_ROWS as PRICE_MIN_FIT_ROWS
from p2_run_price_backtest import PRICE_LAG, RidgePrice, abs_loss, baseline_log_pred
from p2_run_price_backtest import load_rows as load_price_rows
from p2_run_yield_backtest import load_rows as load_yield_rows

TARGET_SEASON = 2027
PRICE_ASOF_SEASON = 2025          # D-14
GINNING_OUTTURN = 0.34            # [Assumption] PRD 5.3 starting value; task 1.23 to confirm
KG_HA_TO_Q_ACRE = 1 / 100 / 2.471
MIN_UNIT_ERRORS = 5               # [Assumption]
MIN_ANCHOR_ARRIVALS_T = 10        # [Assumption] D-17: thinner anchor months are not trusted
MODEL_NAMES = {"M1": "ridge", "M2": "hgbr", "B1": "baseline_b1", "B2": "baseline_b2",
               "ML": "ridge", "P1": "persistence", "P2": "seasonal_naive"}


def to_q_acre(kg_ha, crop):
    q = kg_ha * KG_HA_TO_Q_ACRE
    return q / GINNING_OUTTURN if crop == "cotton" else q


def season_label(y):
    return f"{y}-{str(y + 1)[2:]}"


def fit_yield_model(name, crop, train):
    if name == "M1":
        crop_train = [r for r in train if r["crop"] == crop]
        alpha, _ = inner_cv(crop_train, RidgeYield, RIDGE_ALPHAS, mae_loss, YIELD_PUBLICATION_LAG, RIDGE_MIN_FIT_ROWS)
        return RidgeYield(alpha if alpha is not None else 10.0).fit(crop_train), {"alpha": alpha}
    params, _ = inner_cv(train, PooledHGB, HGB_GRID, relative_mae_loss, YIELD_PUBLICATION_LAG, HGB_MIN_FIT_ROWS)
    return PooledHGB(params or HGB_GRID[0]).fit(train), params


def drivers_for(model, crop, train):
    rows = [r for r in train if r["crop"] == crop]
    base = float(np.mean(np.abs(np.array([r["yield_kg_ha"] for r in rows]) - model.predict(rows))))
    rng = np.random.default_rng(SEED)
    out = []
    for f in WEATHER_FEATURES + ["season"]:
        losses = []
        for _ in range(30):
            vals = rng.permutation([r[f] for r in rows])
            shuffled = [{**r, f: v} for r, v in zip(rows, vals)]
            pred = model.predict(shuffled)
            losses.append(float(np.mean(np.abs(np.array([r["yield_kg_ha"] for r in rows]) - pred))))
        q25, q75 = np.percentile([r[f] for r in rows], [25, 75])
        lo = model.predict([{**r, f: q25} for r in rows]).mean()
        hi = model.predict([{**r, f: q75} for r in rows]).mean()
        out.append({"feature": f, "importance_kg_ha": round(float(np.mean(losses)) - base, 1),
                    "p25": round(float(q25), 1), "p75": round(float(q75), 1),
                    "effect_p25_to_p75_kg_ha": round(float(hi - lo), 1)})
    return sorted(out, key=lambda d: -d["importance_kg_ha"])


def export_yield(selection):
    rows = load_yield_rows()
    weather = load_weather()
    train = yields_asof(rows, TARGET_SEASON)
    w_seasons = sorted({s for (u, s) in weather if s >= 1991})
    passing = {(r["unit"], r["crop"]) for r in read_csv(DATA / "panel_yield_coverage.csv")
               if r["passes_sufficiency"] == "True"}
    bt = read_csv(DATA / "backtest_yield_rows.csv")
    data_through = season_label(max(r["season"] for r in train))
    out, drivers = {}, {}
    for crop in CROPS:
        name = selection[crop]["yield_model"]
        rel = [float(r["rel_error"]) for r in bt if r["crop"] == crop and r["model"] == name]
        model, params = (None, None) if name == "B1" else fit_yield_model(name, crop, train)
        if model is None:
            drivers[crop] = {"model": MODEL_NAMES[name], "drivers": None,
                             "note": "Baseline B1 (mean of the last five published seasons): weather does not change it.",
                             "label": "Prediction"}
        else:
            drivers[crop] = {"model": MODEL_NAMES[name], "params": params, "drivers": drivers_for(model, crop, train),
                             "method": "permutation importance (30 shuffles, seed 20261020) on training rows; "
                                       "effect = mean prediction at the feature's 75th minus 25th percentile",
                             "label": "Prediction"}
        for unit in UNITS:
            if (unit, crop) not in passing:
                continue
            b1 = b1_predict(rows, unit, crop, TARGET_SEASON)
            if model is None:
                preds = [b1] * len(w_seasons)
            else:
                template = {"unit": unit, "crop": crop, "season": TARGET_SEASON}
                preds = model.predict([{**template, **weather[(unit, s)]} for s in w_seasons])
            out[f"{unit}|{crop}"] = {
                "weather_seasons": w_seasons,
                "q_per_acre": [round(to_q_acre(float(p), crop), 3) for p in preds],
                "rel_errors": [round(e, 4) for e in rel],
                "five_season_mean_q_per_acre": round(to_q_acre(b1, crop), 3),
                "data_through": data_through, "model": MODEL_NAMES[name], "label": "Prediction",
                "kg_ha_median": round(float(np.median(preds)), 1),
                "basis": "kapas (lint / 0.34 [Assumption])" if crop == "cotton" else "grain",
            }
    return out, drivers


def window_cv(unit, crop, last_season):
    vals = [float(r["window_price"]) for r in read_csv(DATA / "features_price.csv")
            if r["unit"] == unit and r["crop"] == crop and r["window_price"]
            and last_season - 10 < int(r["season"]) <= last_season]
    return round(float(np.std(vals, ddof=1) / np.mean(vals)), 4) if len(vals) >= 3 else None


def fit_price_ridge(asof):
    train = [r for r in load_price_rows() if r["season"] <= asof - PRICE_LAG]
    alpha, _ = inner_cv(train, RidgePrice, PRICE_ALPHAS, abs_loss, PRICE_LAG, PRICE_MIN_FIT_ROWS, target="target")
    return RidgePrice(alpha if alpha is not None else 10.0).fit(train), train, alpha


def crop_price_forecasts(crop, name, asof, units, feats, arrivals, bt):
    """{unit: entry} for units with a usable anchor on 31 May `asof`, plus [units without one]."""
    ridge, train, alpha = fit_price_ridge(asof)
    bt = [r for r in bt if int(r["season"]) <= asof - PRICE_LAG]

    def errors(unit_filter):
        if name == "ML":
            src = [(int(r["season"]), float(r["log_error"])) for r in bt
                   if r["crop"] == crop and r["model"] == "ML" and unit_filter(r["unit"])]
        else:
            src = [(r["season"], r["target"] - baseline_log_pred(name, r)) for r in train
                   if r["crop"] == crop and unit_filter(r["unit"])]
        return sorted(src)

    out, missing = {}, []
    for unit in units:
        f = feats.get((unit, crop, asof))
        usable = f and f["may_price"] and arrivals.get((unit, crop, f["anchor_month"]), 0) >= MIN_ANCHOR_ARRIVALS_T
        if usable and name == "P2" and not f["f_last_window"]:
            usable = False
        if not usable:
            missing.append(unit)
            continue
        may = float(f["may_price"])
        if name == "P1":
            logp = 0.0
        elif name == "P2":
            logp = float(f["f_last_window"])
        else:
            logp = float(ridge.predict([{"crop": crop, **{k: float(f[k]) for k in PRICE_FEATURES}}])[0])
        errs, borrowed = errors(lambda u, unit=unit: u == unit), False
        if len(errs) < MIN_UNIT_ERRORS:
            errs, borrowed = errors(lambda u: True), True
        out[unit] = {
            "forecast": round(may * math.exp(logp), 1),
            "log_errors": [round(e, 5) for _, e in errs], "error_seasons": [s for s, _ in errs],
            "harvest_window_cv": window_cv(unit, crop, asof - 1),
            "model": MODEL_NAMES[name], "label": "Prediction",
            "anchor_month": f["anchor_month"], "anchor_price": may,
            "errors_borrowed_from_all_units": borrowed,
            "price_data_through": f"May {asof}", "ridge_alpha": alpha if name == "ML" else None,
        }
    return out, missing


def export_price(selection):
    """Per crop: as of 31 May 2025 (D-14); if no unit has a usable anchor then, 31 May 2024 (D-17)."""
    feats = {(r["unit"], r["crop"], int(r["season"])): r for r in read_csv(DATA / "features_price.csv")}
    arrivals = {(r["unit"], r["crop"], r["month"]): float(r["arrivals_t"] or 0)
                for r in read_csv(DATA / "prices_monthly.csv")}
    bt = read_csv(DATA / "backtest_price_rows.csv")
    passing = {(r["unit"], r["crop"]) for r in read_csv(DATA / "panel_yield_coverage.csv")
               if r["passes_sufficiency"] == "True"}
    out = {}
    for crop in CROPS:
        name = selection[crop]["price_model"]
        units = [u for u in UNITS if (u, crop) in passing]
        for asof in (PRICE_ASOF_SEASON, PRICE_ASOF_SEASON - 1):
            got, missing = crop_price_forecasts(crop, name, asof, units, feats, arrivals, bt)
            if got:
                break
        for unit, entry in got.items():
            out[f"{unit}|{crop}"] = entry
        if not got:
            continue
        errs = sorted({(s, e) for v in got.values() for s, e in zip(v["error_seasons"], v["log_errors"])})
        for unit in missing:
            out[f"{unit}|{crop}"] = {
                "forecast": round(float(np.median([v["forecast"] for v in got.values()])), 1),
                "log_errors": [e for _, e in errs], "error_seasons": [s for s, _ in errs],
                "harvest_window_cv": window_cv(unit, crop, asof - 1),
                "model": MODEL_NAMES[name], "label": "Prediction",
                "anchor_month": None, "anchor_price": None, "errors_borrowed_from_all_units": True,
                "borrowed_from_units": sorted(got), "price_data_through": f"May {asof}",
                "ridge_alpha": None,
            }
    return out


def main():
    selection = {r["crop"]: r for r in read_csv(DATA / "model_selection.csv")}
    yields, drivers = export_yield(selection)
    prices = export_price(selection)
    meta = {"target_season": "Kharif 2027", "built": "2026-10-20", "rules": "selection_rules.md v1.0",
            "seed": SEED, "script": "scripts/p2_export.py"}
    (DATA / "export_yield_draws.json").write_text(json.dumps({"meta": meta, "yield_draws": yields}, indent=1))
    (DATA / "export_price.json").write_text(json.dumps(
        {"meta": {**meta, "price_asof": "2025-05-31, or 2024-05-31 where noted (D-14, D-17)"}, "price": prices}, indent=1))
    (DATA / "drivers.json").write_text(json.dumps({"meta": meta, "drivers": drivers}, indent=1))
    for k, v in yields.items():
        print(f"yield {k:28} {v['model']:12} median {np.median(v['q_per_acre']):6.2f} q/acre  n_err {len(v['rel_errors'])}")
    for k, v in prices.items():
        print(f"price {k:28} {v['model']:15} {v['price_data_through']:9} Rs {v['forecast']:8.0f}/q (May {v['anchor_price'] or 0:.0f})  n_err {len(v['log_errors'])}{' errors-borrowed' if v['errors_borrowed_from_all_units'] else ''}{' FORECAST-BORROWED' if v.get('borrowed_from_units') else ''}")
    print(json.dumps(drivers["tur"]["drivers"][:5], indent=0))


if __name__ == "__main__":
    main()
