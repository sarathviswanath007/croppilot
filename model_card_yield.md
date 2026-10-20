# Polaris CropPilot: Yield Model Card (task 2.28)

**Built:** 20 October 2026 · **Rules:** `selection_rules.md` v1.0 (frozen 19 Oct 2026, before any result) · **Seed:** 20261020
**Scripts:** `p2_build_features_yield.py`, `p2_run_yield_backtest.py`, `p2_select_models.py`, `p2_export.py`
**Results:** `data/backtest_yield_metrics.csv`, `data/backtest_yield_rows.csv`, `data/model_selection.csv`
All metrics below are `[Prediction (backtest)]`; yields compared against are `[Data]` (ICRISAT DLD).

## 1. Purpose and limits

Estimates a **district-average** Kharif yield for each model unit × crop, before sowing, as a range across weather seasons. It does not predict any one farm's yield (G1). Ranges reflect past weather and past model error only. Pests, input supply and management are not modelled.

## 2. Training data

| Item | Value |
|---|---|
| Yields | ICRISAT DLD, 1990-91 to 2019-20 (D-04). 2020–2025 are unpublished in this source (G3) |
| Rows used | 426 unit × crop × season rows with ≥ 500 ha: tur 142, cotton 136, maize 118, soybean 30 |
| Weather | NASA POWER, one point per district, averaged per unit (G10, A-07) |
| Known on 31 May T | Yields through season T−2 (`[Assumption]`, D-12) |
| Maize | All seasons combined, not Kharif-only (G15) |
| Cotton | Lint; converted to kapas at export with ginning outturn 0.34 `[Assumption]` (task 1.23 still open) |

## 3. Features

Unit indicator, season year (trend), monthly rain June–October, June–September total, rainy days (≥ 2.5 mm) June–September, longest July–August dry spell, mean August–September Tmax. Left out: heavy-rain days (always ~0 in NASA POWER, G10); irrigated share (not in the panel).

## 4. Models and baselines

| ID | Model | Tuning |
|---|---|---|
| B1 | Mean of the unit's five most recent published seasons (primary baseline) | — |
| B2 | Unit linear trend | — |
| M1 | Ridge per crop, standardised features | alpha from 11 values (0.01–1000), inner time-series CV |
| M2 | Gradient boosting (scikit-learn `HistGradientBoostingRegressor`) pooled across crops, crop and unit as categories; target = yield ÷ crop mean | 8 settings (depth, learning rate, iterations), inner CV |

M3 (random forest, P2) was not built.

## 5. Backtest protocol

Rolling origin, test seasons **2012–2019** (8 seasons). For each test season T: training data = only what was published on 31 May T; hyperparameters from inner CV on the last 8 training seasons, each predicted with the same 2-season gap. Test outcomes were used only for scoring. The full set-up was logged before the first run (D-12). One bug was fixed after the first run (D-13, M2 tuning), with no change to rules, features or grids.

- **Hindcast** uses the season's actual weather.
- **Decision-time** uses the median of 2,000 draws: the model under every weather season 1991 to T−1, times (1 + e), with e from that fold's leak-free inner-CV residuals.
- **Coverage** is the share of test rows whose actual yield fell between the 10th and 90th percentile draws (target 70–90%).
- **Skill** = 1 − MAE(model) ÷ MAE(B1). 90% intervals come from resampling whole seasons (n = 8 seasons, so they are wide).

## 6. Results per crop (including losing models)

| Crop | Model | Rows (seasons × units) | MAE kg/ha | MAPE | Skill vs B1 (90% CI) | Decision-time skill | Coverage 10–90 (n) |
|---|---|---|---|---|---|---|---|
| Tur | B1 | 40 (8 × 5) | 230.9 | 34% | — | +0.02 | 73% (40) |
| Tur | B2 | 40 | 214.0 | 32% | +0.07 (+0.01, +0.14) | +0.08 | 75% (40) |
| Tur | M1 ridge | 40 | 210.7 | 29% | +0.09 (+0.01, +0.16) | +0.10 | 63% (40) |
| **Tur** | **M2 boosting** | 40 | **206.8** | 28% | **+0.10 (−0.03, +0.24)** | +0.09 | **70% (40)** |
| **Maize** | **B1** | 38 (8 × 5) | **833.5** | 34% | — | −0.02 | **47% (38)** |
| Maize | B2 | 38 | 870.7 | 34% | −0.04 (−0.11, +0.02) | −0.12 | 55% (38) |
| Maize | M1 ridge | 38 | 831.5 | 33% | +0.002 (−0.07, +0.10) | −0.06 | 50% (38) |
| Maize | M2 boosting | 38 | 907.6 | 38% | −0.09 (−0.20, +0.05) | −0.11 | 87% (38) |
| **Soybean** | **B1** | 16 (8 × 2) | **471.6** | 47% | — | −0.07 | **80% (10)** |
| Soybean | B2 | 15 | 532.9 | 59% | −0.09 (−0.36, +0.09) | −0.02 | 83% (6) |
| Soybean | M1 ridge | 16 | 500.9 | 58% | −0.06 (−0.46, +0.22) | +0.26 (n 6) | 100% (6) |
| Soybean | M2 boosting | 16 | 486.1 | 50% | −0.03 (−0.25, +0.14) | −0.10 | 75% (16) |
| **Cotton (lint)** | **B1** | 34 (8 × 5) | **119.1** | 29% | — | +0.00 | **79% (34)** |
| Cotton | B2 | 34 | 134.3 | 33% | −0.13 (−0.27, −0.01) | −0.12 | 82% (34) |
| Cotton | M1 ridge | 34 | 118.1 | 28% | +0.009 (−0.13, +0.11) | −0.05 | 82% (34) |
| Cotton | M2 boosting | 34 | 131.7 | 34% | −0.11 (−0.32, +0.06) | −0.26 | 88% (34) |

Soybean M1 could not be tuned in 6 of 16 rows (too few training seasons; fallback alpha 10, D-12), and those rows have no interval.
Sensitivity (task 2.17, A-08): using weather seasons from 2001 instead of 1991 changes coverage by at most about 6 points (largest: soybean M2, 75% → 81%) for any crop and model.

## 7. Selection decision (20 October 2026, rules v1.0)

| Crop | Shipped | Reason |
|---|---|---|
| **Tur** | **M2 gradient boosting (ML)** | MAE 206.8 vs B1 230.9, skill +0.10, outside the 1% tie margin |
| Maize | B1 baseline | Ridge beats B1 by 0.2%: inside the 1% tie margin, so the simpler B1 |
| Soybean | B1 baseline | Both models lose to B1 |
| Cotton | B1 baseline | Ridge beats B1 by 0.9%: inside the 1% tie margin, so the simpler B1 |

The app must say for maize, soybean and cotton that the estimate is the recent five-season average with its past error spread, not a weather model.

## 8. What drives the tur model (task 2.27, `data/drivers.json`)

Permutation importance on training rows (M2, depth 3, learning rate 0.1, 100 iterations). Effect = mean predicted change when the feature moves from its 25th to its 75th percentile.

| Feature | Importance (kg/ha MAE increase) | Effect P25 → P75 |
|---|---|---|
| Season year (trend) | 93.4 | +273 kg/ha (1998 → 2012) |
| June rain | 10.8 | +23 kg/ha |
| June–Sept rain | 10.1 | +18 kg/ha |
| Rainy days | 10.1 | +11 kg/ha |
| July rain | 8.1 | +55 kg/ha |
| Aug–Sept Tmax | 6.7 | −32 kg/ha |
| July–Aug dry spell | 4.8 | −24 kg/ha |

**Honest reading:** most of tur's skill comes from the **technology trend**, not weather. Weather effects are real but small next to model error. Tree models do not extrapolate trends, so the Kharif 2027 tur estimate stays near the level of the latest training years.

## 9. Known failure cases

- **Tur 2016–2017 jumps:** Bidar 2017 (actual 1,651 kg/ha vs M2 706) and Kalaburagi+Yadgir 2016–2018. Yields rose far above any trend seen in training. B1 and M2 miss these by about 470–950 kg/ha.
- **Maize ranges are too narrow** (47% coverage vs the 70–90% target). Misses mostly come in runs: 2012–2013 actuals above the range, 2015–2016 mostly below it. This is consistent with Kharif and Rabi maize being mixed in the source (G15). Maize gets a **Low** confidence badge under the frozen thresholds.
- **Soybean** has only 16 test rows in 2 units. Interval results rest on 6–16 rows.
- **Data ends 2019-20** (G3): Kharif 2027 is 8 seasons past the last observed yield.
- **Extreme seasons** (three possible crop failures, G19) are kept in training and widen the residual pool.

## 10. Confidence-threshold check (task 2.26, A-09; thresholds unchanged)

| Crop | Coverage of shipped model | Against `selection_rules.md` §3 |
|---|---|---|
| Tur | 70% (n 40) | Inside 70–90%, but skill +0.10 has a CI below 0. Meets the "High" skill bar only at the point estimate |
| Maize | 47% (n 38) | Outside 60–95%: **Low** |
| Soybean | 80% (n 10) | Inside 70–90%, very small n |
| Cotton | 79% (n 34) | Inside 70–90%: Medium (baseline used) |

## 11. Kharif 2027 export (task 2.30)

`data/export_yield_draws.json`: 17 unit × crop pairs (soybean only in Kalaburagi+Yadgir and Bidar), 35 weather seasons (1991–2025), and the shipped model's backtest relative errors (tur 40, maize 38, soybean 16, cotton 34). Quintals per acre; cotton in kapas. Data through 2019-20.
