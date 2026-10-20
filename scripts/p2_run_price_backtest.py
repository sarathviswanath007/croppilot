"""Tasks 2.09, 2.10, 2.19, 2.22: rolling-origin harvest-price backtest (PRD 4.3, 9.1, 9.2).

Unit: model unit x crop x season. Modelled quantity: log(harvest-window price / May price).
  P1  persistence: window price = May price (log ratio 0)
  P2  seasonal naive: window price = last season's window price
  ML  ridge pooled across crops and units: PRICE_FEATURES + crop indicators, standardised;
      alpha by inner time-series CV on training seasons (lag 1: season T-1's window has
      closed by 31 May T, so it is known)
For test season T (2012 .. latest), models train on seasons <= T - 1. A test row is scored only
if every model can predict it (it needs a May anchor and last season's window price).

Intervals: P10 / P90 of forecast x exp(r), r = the model's past log-errors for that crop
(baselines: every past season <= T - 1; ridge: its inner-CV out-of-sample errors). No interval
with fewer than MIN_RESIDUALS errors.

Metric uncertainty (task 2.22): 90% CIs by resampling whole seasons. Districts in one season
move together, so the effective sample size is closer to the number of seasons than to rows.

Inputs:  data/features_price.csv
Outputs: data/backtest_price_rows.csv, data/backtest_price_metrics.csv
Usage:   python3 scripts/p2_run_price_backtest.py
"""
import math

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import p2_metrics as M
from p2_asof import CROPS, DATA, read_csv
from p2_backtest import MIN_RESIDUALS, inner_cv, test_seasons
from p2_build_features_price import PRICE_FEATURES
from p2_run_yield_backtest import write

MODELS = ["P1", "P2", "ML"]
ALPHAS = [float(a) for a in np.logspace(-2, 3, 11)]
MIN_FIT_ROWS = 30   # [Assumption]
PRICE_LAG = 1


def load_rows():
    """Rows usable by every model: May anchor, target and last window price present."""
    rows = []
    for r in read_csv(DATA / "features_price.csv"):
        if not (r["target"] and r["f_last_window"] and r["f_msp"]):
            continue
        row = {"unit": r["unit"], "crop": r["crop"], "season": int(r["season"]),
               "may_price": float(r["may_price"]), "window_price": float(r["window_price"]),
               "target": float(r["target"]), "flags": r["flags"]}
        row.update({f: float(r[f]) for f in PRICE_FEATURES})
        rows.append(row)
    return rows


class RidgePrice:
    def __init__(self, alpha):
        self.alpha = alpha

    @staticmethod
    def design(rows):
        crops = np.array([[r["crop"] == c for c in CROPS] for r in rows], dtype=float)
        return np.hstack([crops, np.array([[r[f] for f in PRICE_FEATURES] for r in rows])])

    @staticmethod
    def feature_names():
        return [f"crop_{c}" for c in CROPS] + PRICE_FEATURES

    def fit(self, rows):
        self.pipe = make_pipeline(StandardScaler(), Ridge(alpha=self.alpha))
        self.pipe.fit(self.design(rows), [r["target"] for r in rows])
        return self

    def predict(self, rows):
        return self.pipe.predict(self.design(rows))


def abs_loss(actual, pred, rows):
    return float(np.mean(np.abs(actual - pred)))


def baseline_log_pred(name, row):
    return 0.0 if name == "P1" else row["f_last_window"]


def run():
    rows = load_rows()
    out = []
    for T in test_seasons(rows):
        train = [r for r in rows if r["season"] <= T - PRICE_LAG]
        alpha, oos = inner_cv(train, RidgePrice, ALPHAS, abs_loss, PRICE_LAG, MIN_FIT_ROWS, target="target")
        ridge = RidgePrice(alpha if alpha is not None else 10.0).fit(train)
        for crop in CROPS:
            past = [r for r in train if r["crop"] == crop]
            pools = {name: [r["target"] - baseline_log_pred(name, r) for r in past] for name in ("P1", "P2")}
            pools["ML"] = [r["target"] - p for r, p in oos if r["crop"] == crop]
            for row in (r for r in rows if r["season"] == T and r["crop"] == crop):
                logp = {"P1": 0.0, "P2": row["f_last_window"], "ML": float(ridge.predict([row])[0])}
                for name in MODELS:
                    fc = row["may_price"] * math.exp(logp[name])
                    rec = {"crop": crop, "unit": row["unit"], "season": T, "model": name,
                           "may_price": row["may_price"], "actual": row["window_price"],
                           "forecast": round(fc, 1), "log_error": round(row["target"] - logp[name], 5),
                           "params": f"alpha={alpha}" if name == "ML" else "",
                           "tuned": alpha is not None or name != "ML", "n_residuals": len(pools[name])}
                    if len(pools[name]) >= MIN_RESIDUALS:
                        lo, hi = np.percentile(fc * np.exp(pools[name]), [10, 90])
                        rec["p10"], rec["p90"] = round(float(lo), 1), round(float(hi), 1)
                    out.append(rec)
        print(f"test season {T}: done")
    return out


def summarise(out):
    metrics = []
    for crop in CROPS:
        by = {name: [r for r in out if r["crop"] == crop and r["model"] == name] for name in MODELS}
        if not by["P1"]:
            continue
        a = np.array([r["actual"] for r in by["P1"]])
        may = np.array([r["may_price"] for r in by["P1"]])
        fc = {name: np.array([r["forecast"] for r in by[name]]) for name in MODELS}
        seasons = [r["season"] for r in by["P1"]]
        mapes = {name: M.mape(a, fc[name]) for name in MODELS}
        better = min(("P1", "P2"), key=lambda n: mapes[n])
        for name in MODELS:
            def skill_of(idx, name=name):
                return M.skill(M.mape(a[idx], fc[name][idx]), M.mape(a[idx], fc[better][idx]))
            lo, hi = M.bootstrap_ci(skill_of, seasons)
            mlo, mhi = M.bootstrap_ci(lambda idx, name=name: M.mape(a[idx], fc[name][idx]), seasons)
            with_iv = [r for r in by[name] if "p10" in r]
            cov = M.coverage([r["actual"] for r in with_iv], [r["p10"] for r in with_iv],
                             [r["p90"] for r in with_iv]) if with_iv else None
            direction = None if name == "P1" else M.direction_accuracy(a, fc[name], may)
            metrics.append({
                "crop": crop, "model": name, "better_baseline": better, "n_rows": len(a),
                "n_seasons": len(set(seasons)), "n_units": len({r["unit"] for r in by[name]}),
                "first_season": min(seasons), "last_season": max(seasons),
                "mape": round(mapes[name], 4), "mape_ci90_low": round(mlo, 4), "mape_ci90_high": round(mhi, 4),
                "skill_vs_better_baseline": round(M.skill(mapes[name], mapes[better]), 4),
                "skill_ci90_low": round(lo, 4), "skill_ci90_high": round(hi, 4),
                "direction_accuracy": round(direction, 4) if direction is not None else "",
                "n_with_interval": len(with_iv), "coverage_10_90": round(cov, 4) if cov is not None else "",
                "label": "Prediction (backtest)",
            })
    return metrics


def main():
    out = run()
    write(DATA / "backtest_price_rows.csv", out)
    metrics = summarise(out)
    write(DATA / "backtest_price_metrics.csv", metrics)
    for m in metrics:
        print(m["crop"], m["model"], "n", m["n_rows"], "seasons", m["n_seasons"], "MAPE", m["mape"],
              "skill", m["skill_vs_better_baseline"], f"[{m['skill_ci90_low']}, {m['skill_ci90_high']}]",
              "dir", m["direction_accuracy"], "cov", m["coverage_10_90"])


if __name__ == "__main__":
    main()
