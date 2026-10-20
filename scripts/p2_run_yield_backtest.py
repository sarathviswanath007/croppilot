"""Tasks 2.06, 2.07, 2.11, 2.12, 2.14-2.17: rolling-origin yield backtest (PRD 9.1, 9.2).

For each test season T (2012 to the latest published season) and each counting test row:
  hindcast       prediction with T's actual weather (does the model understand weather?)
  decision-time  draws under every weather season 1991 .. T-1, times (1 + e) with e from the
                 model's leak-free residual pool; P10 / P50 / P90 kept (task 2.15)
  sensitivity    the same draws using weather seasons 2001 .. T-1 only (task 2.17, A-08)

Models: B1, B2 (baselines), M1 ridge per crop, M2 pooled gradient boosting (p2_models_yield).
A test row is scored only if B1, M1 and M2 all predict it, so every model is compared on the
same rows. B2 is reported on the rows where it can predict (it needs >= 5 published seasons).
[Assumption] If inner CV cannot run for M1 (too few training seasons), M1 uses
RIDGE_FALLBACK_ALPHA and has no interval for that row; the row is marked tuned = False.

Inputs:  data/features_yield.csv, data/weather_features.csv
Outputs: data/backtest_yield_rows.csv     one row per test row x model (hindcast, draws, residual)
         data/backtest_yield_metrics.csv  per crop x model: MAE, MAPE, skill vs B1 with 90% CI,
                                          decision-time MAE and skill, 10-90 coverage, n
Usage:   python3 scripts/p2_run_yield_backtest.py
"""
import csv

import numpy as np

import p2_metrics as M
from p2_asof import CROPS, DATA, UNITS, YIELD_PUBLICATION_LAG, read_csv, weather_seasons_asof, yields_asof
from p2_backtest import MIN_RESIDUALS, decision_draws, inner_cv, rng_for, test_seasons
from p2_build_features_yield import WEATHER_FEATURES, load_weather
from p2_models_yield import (HGB_GRID, HGB_MIN_FIT_ROWS, RIDGE_ALPHAS, RIDGE_MIN_FIT_ROWS, PooledHGB,
                             RidgeYield, b1_predict, b2_predict, baseline_residuals, mae_loss,
                             relative_mae_loss)

MODELS = ["B1", "B2", "M1", "M2"]
RIDGE_FALLBACK_ALPHA = 10.0   # [Assumption]
SENSITIVITY_FIRST_WEATHER = 2001


def load_rows():
    rows = []
    for r in read_csv(DATA / "features_yield.csv"):
        row = {"unit": r["unit"], "crop": r["crop"], "season": int(r["season"]),
               "yield_kg_ha": float(r["yield_kg_ha"]), "flags": r["flags"]}
        row.update({f: float(r[f]) for f in WEATHER_FEATURES})
        rows.append(row)
    return rows


def with_weather(row, season, weather):
    """The test row as it would look under weather season `season`, keeping its own trend year."""
    return {**row, **weather[(row["unit"], season)]}


def percentiles(draws):
    return [float(x) for x in np.percentile(draws, [10, 50, 90])]


def run():
    rows = load_rows()
    weather = load_weather()
    out = []
    for T in test_seasons(rows):
        train = yields_asof(rows, T)
        tests = [r for r in rows if r["season"] == T]
        w_all = weather_seasons_asof(T)
        w_late = weather_seasons_asof(T, first=SENSITIVITY_FIRST_WEATHER)

        # M2: one pooled model per test season
        m2_params, m2_oos = inner_cv(train, PooledHGB, HGB_GRID, relative_mae_loss,
                                     YIELD_PUBLICATION_LAG, HGB_MIN_FIT_ROWS)
        m2 = PooledHGB(m2_params or HGB_GRID[0]).fit(train)

        for crop in CROPS:
            crop_tests = [r for r in tests if r["crop"] == crop]
            if not crop_tests:
                continue
            crop_train = [r for r in train if r["crop"] == crop]
            last_pub = T - YIELD_PUBLICATION_LAG

            # M1: ridge per crop
            m1 = m1_alpha = None
            m1_res = []
            if len(crop_train) >= RIDGE_MIN_FIT_ROWS:
                m1_alpha, m1_oos = inner_cv(crop_train, RidgeYield, RIDGE_ALPHAS, mae_loss,
                                            YIELD_PUBLICATION_LAG, RIDGE_MIN_FIT_ROWS)
                m1_res = [r["yield_kg_ha"] / p - 1 for r, p in m1_oos]
                m1 = RidgeYield(m1_alpha if m1_alpha is not None else RIDGE_FALLBACK_ALPHA).fit(crop_train)

            residuals = {
                "B1": baseline_residuals(rows, crop, b1_predict, last_pub),
                "B2": baseline_residuals(rows, crop, b2_predict, last_pub),
                "M1": m1_res,
                "M2": [r["yield_kg_ha"] / p - 1 for r, p in m2_oos if r["crop"] == crop],
            }
            params = {"B1": "", "B2": "", "M1": f"alpha={m1_alpha}" if m1 else "",
                      "M2": str(m2_params) if m2_params else "untuned"}

            for row in crop_tests:
                b1 = b1_predict(rows, row["unit"], crop, T)
                if b1 is None or m1 is None:
                    continue   # not scorable for every model -> left out for all (see docstring)
                variants = {s: with_weather(row, s, weather) for s in w_all}
                point = {"B1": lambda rs: np.full(len(rs), b1)}
                b2 = b2_predict(rows, row["unit"], crop, T)
                if b2 is not None:
                    point["B2"] = lambda rs, b2=b2: np.full(len(rs), b2)
                point["M1"] = m1.predict
                point["M2"] = m2.predict

                for mi, name in enumerate(MODELS):
                    if name not in point:
                        continue
                    hind = float(point[name]([row])[0])
                    rec = {"crop": crop, "unit": row["unit"], "season": T, "model": name,
                           "actual": row["yield_kg_ha"], "hindcast": round(hind, 1),
                           "rel_error": round(row["yield_kg_ha"] / hind - 1, 4),
                           "tuned": not (name == "M1" and m1_alpha is None) and not (name == "M2" and not m2_params),
                           "params": params[name], "n_train": len(crop_train),
                           "n_residuals": len(residuals[name]), "flags": row["flags"]}
                    if len(residuals[name]) >= MIN_RESIDUALS:
                        preds = point[name]([variants[s] for s in w_all])
                        rng = rng_for(T, CROPS.index(crop), UNITS.index(row["unit"]), mi)
                        draws, w_idx = decision_draws(preds, residuals[name], rng)
                        rec["dt_p10"], rec["dt_p50"], rec["dt_p90"] = percentiles(draws)
                        late = np.isin(np.array(w_all)[w_idx], w_late)
                        rec["dt2001_p10"], rec["dt2001_p50"], rec["dt2001_p90"] = percentiles(draws[late])
                    out.append(rec)
        print(f"test season {T}: done")
    return out


def summarise(out):
    metrics = []
    for crop in CROPS:
        b1_rows = {(r["unit"], r["season"]): r for r in out if r["crop"] == crop and r["model"] == "B1"}
        for name in MODELS:
            rs = [r for r in out if r["crop"] == crop and r["model"] == name]
            if not rs:
                continue
            a = np.array([r["actual"] for r in rs])
            h = np.array([r["hindcast"] for r in rs])
            b = np.array([b1_rows[(r["unit"], r["season"])]["hindcast"] for r in rs])
            seasons = [r["season"] for r in rs]

            def skill_of(idx):
                return M.skill(M.mae(a[idx], h[idx]), M.mae(a[idx], b[idx]))

            lo, hi = M.bootstrap_ci(skill_of, seasons)
            with_dt = [r for r in rs if "dt_p50" in r]
            dt_mae = M.mae([r["actual"] for r in with_dt], [r["dt_p50"] for r in with_dt]) if with_dt else None
            b1_dt = M.mae([r["actual"] for r in with_dt],
                          [b1_rows[(r["unit"], r["season"])]["hindcast"] for r in with_dt]) if with_dt else None
            cov = M.coverage([r["actual"] for r in with_dt], [r["dt_p10"] for r in with_dt],
                             [r["dt_p90"] for r in with_dt]) if with_dt else None
            cov01 = M.coverage([r["actual"] for r in with_dt], [r["dt2001_p10"] for r in with_dt],
                               [r["dt2001_p90"] for r in with_dt]) if with_dt else None
            mae = M.mae(a, h)
            metrics.append({
                "crop": crop, "model": name, "n_rows": len(rs), "n_seasons": len(set(seasons)),
                "n_units": len({r["unit"] for r in rs}), "first_season": min(seasons), "last_season": max(seasons),
                "mae_kg_ha": round(mae, 1), "mape": round(M.mape(a, h), 4),
                "skill_vs_b1": round(M.skill(mae, M.mae(a, b)), 4),
                "skill_ci90_low": round(lo, 4) if lo is not None else "",
                "skill_ci90_high": round(hi, 4) if hi is not None else "",
                "n_with_interval": len(with_dt),
                "dt_mae_kg_ha": round(dt_mae, 1) if dt_mae is not None else "",
                "dt_skill_vs_b1": round(M.skill(dt_mae, b1_dt), 4) if dt_mae is not None else "",
                "coverage_10_90": round(cov, 4) if cov is not None else "",
                "coverage_10_90_weather_from_2001": round(cov01, 4) if cov01 is not None else "",
                "n_untuned_rows": sum(1 for r in rs if r["tuned"] is False),
                "label": "Prediction (backtest)",
            })
    return metrics


def write(path, rows):
    fields = []
    for r in rows:
        fields += [k for k in r if k not in fields]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    out = run()
    write(DATA / "backtest_yield_rows.csv", out)
    metrics = summarise(out)
    write(DATA / "backtest_yield_metrics.csv", metrics)
    for m in metrics:
        print(m["crop"], m["model"], "n", m["n_rows"], "MAE", m["mae_kg_ha"], "skill", m["skill_vs_b1"],
              "dt_skill", m["dt_skill_vs_b1"], "cov", m["coverage_10_90"], "cov01", m["coverage_10_90_weather_from_2001"])


if __name__ == "__main__":
    main()
