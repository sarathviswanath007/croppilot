# Provenance: Phase 2 derived files (20 October 2026)

Re-create everything with (from the project root, `.venv` has numpy and scikit-learn 1.9.1):

```
.venv/bin/python scripts/p2_build_features_yield.py
.venv/bin/python scripts/p2_build_features_price.py
.venv/bin/python scripts/p2_run_yield_backtest.py      # ~10 min (gradient-boosting grid)
.venv/bin/python scripts/p2_run_price_backtest.py
.venv/bin/python scripts/p2_select_models.py
.venv/bin/python scripts/p2_export.py
```

| File | Inputs | Script | Label |
|---|---|---|---|
| `features_yield.csv` | `panel_yield.csv`, `weather_features.csv` | `p2_build_features_yield.py` | Data |
| `features_price.csv` | `prices_monthly.csv`, `harvest_windows.csv`, `msp.csv` | `p2_build_features_price.py` | Data (target, features) |
| `backtest_yield_rows.csv`, `backtest_yield_metrics.csv` | `features_yield.csv`, `weather_features.csv` | `p2_run_yield_backtest.py` | Prediction (backtest) |
| `backtest_price_rows.csv`, `backtest_price_metrics.csv` | `features_price.csv` | `p2_run_price_backtest.py` | Prediction (backtest) |
| `model_selection.csv` | both metrics files, `selection_rules.md` v1.0 | `p2_select_models.py` | Decision |
| `export_yield_draws.json`, `export_price.json`, `drivers.json` | the above, `panel_yield_coverage.csv`, `prices_monthly.csv` | `p2_export.py` | Prediction |

Seed 20261020 everywhere. Rerun check (task 2.32), 20 Oct 2026: full pipeline re-run from scratch; `backtest_yield_metrics.csv`, `backtest_price_metrics.csv`, `model_selection.csv`, `export_yield_draws.json`, `export_price.json` and `drivers.json` byte-identical to the first run.
