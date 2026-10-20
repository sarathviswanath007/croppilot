"""Task 2.04: backtest metrics (PRD 9.2). Plain numpy; every function returns a float or None.

  mae, mape                     errors of predictions vs actuals
  skill(model, baseline)        1 - model / baseline (MAE skill for yield, MAPE skill for price)
  coverage(actual, lo, hi)      share of actuals inside [lo, hi] (the 10th-90th percentile draws)
  direction_accuracy            share of seasons where the sign of (forecast - anchor) matches
                                the sign of (actual - anchor); the anchor is the May price
  bootstrap_ci                  percentile CI of a metric, resampling whole seasons (clusters),
                                because districts in one season are not independent (PRD 4.3)
"""
import numpy as np


def _arrays(*xs):
    return [np.asarray(x, dtype=float) for x in xs]


def mae(actual, pred):
    a, p = _arrays(actual, pred)
    return float(np.mean(np.abs(a - p))) if a.size else None


def mape(actual, pred):
    a, p = _arrays(actual, pred)
    return float(np.mean(np.abs(a - p) / np.abs(a))) if a.size else None


def skill(model_error, baseline_error):
    if model_error is None or not baseline_error:
        return None
    return 1.0 - model_error / baseline_error


def coverage(actual, lo, hi):
    a, l, h = _arrays(actual, lo, hi)
    return float(np.mean((a >= l) & (a <= h))) if a.size else None


def direction_accuracy(actual, pred, anchor):
    """Seasons with no actual change (actual == anchor) are left out; a flat forecast counts as wrong."""
    a, p, z = _arrays(actual, pred, anchor)
    moved = a != z
    if not moved.any():
        return None
    return float(np.mean(np.sign(p[moved] - z[moved]) == np.sign(a[moved] - z[moved])))


def bootstrap_ci(metric, clusters, n_boot=2000, level=0.90, seed=20261020):
    """Percentile CI of metric(index_array), resampling clusters (e.g. seasons) with replacement.

    metric: function taking an array of row indices and returning a float (or None).
    clusters: one label per row.
    """
    clusters = np.asarray(clusters)
    labels = np.unique(clusters)
    rows_of = {c: np.flatnonzero(clusters == c) for c in labels}
    rng = np.random.default_rng(seed)
    stats = []
    for _ in range(n_boot):
        pick = rng.choice(labels, size=labels.size, replace=True)
        value = metric(np.concatenate([rows_of[c] for c in pick]))
        if value is not None:
            stats.append(value)
    if not stats:
        return None, None
    tail = (1 - level) / 2 * 100
    return float(np.percentile(stats, tail)), float(np.percentile(stats, 100 - tail))
