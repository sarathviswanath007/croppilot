"""Tasks 2.06, 2.07, 2.11, 2.12: yield baselines and candidate models (PRD 4.2).

Rows are dicts with unit, crop, season, yield_kg_ha and the weather features
(see p2_build_features_yield.WEATHER_FEATURES). Every function only sees the rows it is given;
p2_asof decides what is known on the decision date.

  B1  mean of the unit's five most recent published counting seasons (primary baseline).
      [Assumption] needs >= 3 such seasons, otherwise no prediction.
  B2  the unit's own linear trend over all its published counting seasons.
      [Assumption] needs >= 5 seasons.
  M1  ridge per crop: unit indicators + season year + weather, standardised; alpha by inner CV.
  M2  HistGradientBoostingRegressor pooled across crops, crop and unit as categorical features.
      [Assumption] target is yield / the crop's mean training yield (multiplied back after), so
      maize's larger kg/ha numbers do not dominate the shared loss. Settings by inner CV.
"""
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from p2_asof import CROPS, UNITS, YIELD_PUBLICATION_LAG
from p2_backtest import SEED
from p2_build_features_yield import WEATHER_FEATURES

B1_SEASONS, B1_MIN = 5, 3
B2_MIN = 5
RIDGE_ALPHAS = [float(a) for a in np.logspace(-2, 3, 11)]
RIDGE_MIN_FIT_ROWS = 10    # [Assumption]
HGB_GRID = [{"max_depth": d, "learning_rate": lr, "max_iter": n}
            for d in (2, 3) for lr in (0.05, 0.1) for n in (100, 300)]
HGB_MIN_LEAF = 10          # [Assumption]
HGB_MIN_FIT_ROWS = 50      # [Assumption]


def unit_history(rows, unit, crop, season, lag=YIELD_PUBLICATION_LAG):
    """(seasons, yields) of the unit and crop published by the decision date of `season`."""
    hist = sorted((r["season"], r["yield_kg_ha"]) for r in rows
                  if r["unit"] == unit and r["crop"] == crop and r["season"] <= season - lag)
    return [s for s, _ in hist], [y for _, y in hist]


def b1_predict(rows, unit, crop, season):
    _, ys = unit_history(rows, unit, crop, season)
    ys = ys[-B1_SEASONS:]
    return float(np.mean(ys)) if len(ys) >= B1_MIN else None


def b2_predict(rows, unit, crop, season):
    ss, ys = unit_history(rows, unit, crop, season)
    if len(ys) < B2_MIN:
        return None
    slope, intercept = np.polyfit(ss, ys, 1)
    return float(intercept + slope * season)


def baseline_residuals(rows, crop, predict, upto_season):
    """Relative errors of a baseline over past seasons <= upto_season, each predicted as-of itself."""
    out = []
    for r in rows:
        if r["crop"] == crop and r["season"] <= upto_season:
            p = predict(rows, r["unit"], crop, r["season"])
            if p:
                out.append(r["yield_kg_ha"] / p - 1.0)
    return out


def _weather_matrix(rows):
    return np.array([[r[f] for f in WEATHER_FEATURES] for r in rows], dtype=float)


class RidgeYield:
    """M1 for one crop."""

    def __init__(self, alpha):
        self.alpha = alpha

    @staticmethod
    def design(rows):
        units = np.array([[r["unit"] == u for u in UNITS] for r in rows], dtype=float)
        year = np.array([[r["season"]] for r in rows], dtype=float)
        return np.hstack([units, year, _weather_matrix(rows)])

    @staticmethod
    def feature_names():
        return [f"unit_{u}" for u in UNITS] + ["season_year"] + WEATHER_FEATURES

    def fit(self, rows):
        self.pipe = make_pipeline(StandardScaler(), Ridge(alpha=self.alpha))
        self.pipe.fit(self.design(rows), [r["yield_kg_ha"] for r in rows])
        return self

    def predict(self, rows):
        return self.pipe.predict(self.design(rows))


class PooledHGB:
    """M2 across all crops."""

    def __init__(self, params):
        self.params = params

    @staticmethod
    def design(rows):
        cats = np.array([[CROPS.index(r["crop"]), UNITS.index(r["unit"])] for r in rows], dtype=float)
        year = np.array([[r["season"]] for r in rows], dtype=float)
        return np.hstack([cats, year, _weather_matrix(rows)])

    def fit(self, rows):
        self.crop_mean = {c: float(np.mean([r["yield_kg_ha"] for r in rows if r["crop"] == c]))
                          for c in {r["crop"] for r in rows}}
        y = [r["yield_kg_ha"] / self.crop_mean[r["crop"]] for r in rows]
        self.model = HistGradientBoostingRegressor(
            categorical_features=[0, 1], min_samples_leaf=HGB_MIN_LEAF, random_state=SEED, **self.params)
        self.model.fit(self.design(rows), y)
        return self

    def predict(self, rows):
        scale = np.array([self.crop_mean.get(r["crop"], np.nan) for r in rows])
        return self.model.predict(self.design(rows)) * scale


def mae_loss(actual, pred, rows):
    return float(np.mean(np.abs(actual - pred)))


def relative_mae_loss(actual, pred, rows):
    return float(np.mean(np.abs(actual - pred) / actual))
