"""Task 2.03: rolling-origin (expanding window) backtest harness (PRD 9.1).

For each test season T from 2012 to the latest season with data:
  - training data = only what was known on 31 May T (p2_asof), so for yields seasons <= T - 2
  - hyperparameters come from inner time-series CV on those training seasons only: each of
    the last N_INNER_VAL training seasons is predicted from seasons <= v - lag, the same gap
    the outer test faces. The out-of-sample inner predictions at the chosen setting are the
    model's residual pool for test season T (so coverage never uses test-season errors).
  - test-season outcomes are only used to score, never to tune, select features or pick models.

Decision-time draws (PRD 4.4): the fitted model is run with T's trend under every complete
historical weather season w (1991 .. T-1), and each prediction is multiplied by (1 + e) with
e drawn from the residual pool. Weather seasons are cycled so each appears equally often.
"""
import numpy as np

TEST_FIRST = 2012
N_INNER_VAL = 8        # [Assumption] inner validation seasons per outer fold
N_DRAWS = 2000         # PRD 4.4 [Assumption]
MIN_RESIDUALS = 10     # [Assumption] fewer residuals than this -> no interval (coverage not scored)
SEED = 20261020        # NFR-09


def test_seasons(rows, first=TEST_FIRST):
    return sorted({r["season"] for r in rows if r["season"] >= first})


def inner_cv(train_rows, make_model, grid, score, lag, min_fit_rows, min_folds=3,
             target="yield_kg_ha"):
    """Pick params from `grid` by inner time-series CV on `train_rows`.

    Returns (best_params, oos) where oos is a list of (row, prediction) at best_params, or
    (None, []) if fewer than `min_folds` validation seasons could be fitted.
    `score(actuals, preds, rows)` returns a loss (lower is better).
    """
    seasons = sorted({r["season"] for r in train_rows})
    folds = []
    for v in seasons[-N_INNER_VAL:]:
        fit = [r for r in train_rows if r["season"] <= v - lag]
        val = [r for r in train_rows if r["season"] == v]
        if len(fit) >= min_fit_rows and val:
            folds.append((fit, val))
    if len(folds) < min_folds:
        return None, []
    best = None
    for params in grid:
        oos = []
        for fit, val in folds:
            model = make_model(params).fit(fit)
            # a pooled model cannot predict a crop absent from `fit` (NaN): leave those rows out
            oos.extend((r, p) for r, p in zip(val, model.predict(val)) if np.isfinite(p))
        loss = score(np.array([r[target] for r, _ in oos]), np.array([p for _, p in oos]),
                     [r for r, _ in oos])
        if best is None or loss < best[0]:
            best = (loss, params, oos)
    return best[1], best[2]


def decision_draws(pred_by_weather, residuals, rng, n=N_DRAWS):
    """pred_by_weather: array of point predictions, one per weather season.
    residuals: relative errors e (actual / pred - 1). Returns (draws, weather index per draw)."""
    preds = np.asarray(pred_by_weather, dtype=float)
    w_idx = np.arange(n) % preds.size
    e = rng.choice(np.asarray(residuals, dtype=float), size=n, replace=True)
    return preds[w_idx] * (1.0 + e), w_idx


def rng_for(*keys):
    return np.random.default_rng([SEED, *keys])
