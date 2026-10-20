# Polaris CropPilot: Leakage Checklist (task 2.02, risk R7)

Use this for every code review of Phase 2 scripts. Each item states where the Phase 2 code enforces it. Status reviewed 20 October 2026.

| # | Check | Where enforced | Status |
|---|---|---|---|
| L1 | Yields used for season T are only those published by 31 May T (seasons ≤ T−2, D-12) | `p2_asof.yields_asof`; B1/B2 via `p2_models_yield.unit_history`; tested in `tests/test_p2_asof_metrics.py` | ✅ |
| L2 | Prices used for season T stop at May of T | Features built from months ≤ May T (`p2_build_features_price`); price training uses seasons ≤ T−1, whose windows close by March T | ✅ |
| L3 | The season's MSP is used only if announced on or before 31 May; otherwise the previous season's (D-08) | `p2_asof.msp_asof`; tested | ✅ |
| L4 | The test season's weather is never used for decision-time predictions | Draws use `weather_seasons_asof(T)` = 1991 … T−1 | ✅ |
| L5 | Actual weather is used only for training and hindcasts, labelled as such | `p2_run_yield_backtest`: `hindcast` vs `dt_*` columns | ✅ |
| L6 | Hyperparameters are chosen by inner CV on training seasons only, with the same publication gap | `p2_backtest.inner_cv` (lag 2 for yield, 1 for price) | ✅ |
| L7 | Residual pools for backtest intervals contain no test-season errors | Yield: inner-CV errors; baselines: past seasons ≤ T−2; price: seasons ≤ T−1 | ✅ |
| L8 | Features are not chosen using test results | Feature set fixed in D-12 and D-16, both decided before the relevant backtest ran | ✅ |
| L9 | Model choice follows the frozen rules, coded, not judged | `p2_select_models.py` implements `selection_rules.md` v1.0 | ✅ |
| L10 | Current-season sown area is never used | Not in any feature set | ✅ |
| L11 | Any change made after seeing test results is logged as such | D-13 (bug fix, results seen) | ✅ |
| L12 | Export intervals use backtest (out-of-sample) errors only | `p2_export.py`: hindcast residuals 2012–2019 / price log-errors | ✅ |

**Known soft spot:** the 31 May publication lag (L1) is an `[Assumption]`. If DES publishes faster, the backtest is slightly pessimistic for B1; if slower, slightly optimistic.
