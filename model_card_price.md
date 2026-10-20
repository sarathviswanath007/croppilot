# Polaris CropPilot: Harvest-Price Model Card (task 2.29)

**Built:** 20 October 2026 · **Rules:** `selection_rules.md` v1.0 §2 · **Seed:** 20261020
**Scripts:** `p2_build_features_price.py`, `p2_run_price_backtest.py`, `p2_select_models.py`, `p2_export.py`
**Results:** `data/backtest_price_metrics.csv`, `data/backtest_price_rows.csv`, `data/export_price.json`
Metrics are `[Prediction (backtest)]`; prices compared against are `[Data]` (CEDA monthly modal prices).

## 1. Purpose and limits

Estimates the average APMC modal price over each crop's harvest-marketing window, made on 31 May. Farmers may sell at other prices (G6). MSP is a reference, never a floor (G11). Prices are nominal ₹ per quintal; cotton is kapas.

## 2. Data, target and features

| Item | Value |
|---|---|
| Prices | CEDA monthly, Census 2011 districts → 5 units, 2002–2025 (maize to May 2025) |
| Windows | Tur Jan–Feb, maize Oct–Jan, soybean Oct–Nov, cotton Nov–Mar, from arrival peaks, **pending expert check** (G5) |
| Target | log(window price ÷ May price). Window price needs ≥ half its months `[Assumption]` |
| Anchor | May price, else April, else March of the same year `[Assumption]` |
| Features | 12-month mean price, last season's window price, MSP as known on 31 May (D-08), each as log ratio to the May price, plus crop indicators |
| Left out | Arrivals vs 5-year mean: CEDA arrivals have reporting breaks (D-16, G22) |

## 3. Models

**P1** persistence (window price = May price) · **P2** seasonal naive (= last season's window price) · **ML** ridge pooled across crops and units, alpha by inner time-series CV. The gradient-boosted alternative (task 2.20, P2 priority) was not built.

## 4. Backtest protocol

Rolling origin, test seasons **2012–2024** (13). Training = seasons ≤ T−1 (their windows close by March, before 31 May T). A row is scored only if every model can predict it. Intervals: 10th–90th percentile of forecast × exp(past log-errors). Baselines use all past seasons, ridge its inner-CV errors.

**Effective sample size.** Prices in neighbouring units move together, so the evidence is closer to **13 seasons per crop** than to the row counts below. All 90% CIs resample whole seasons and are wide.

## 5. Results per crop (including losing models)

Skill = 1 − MAPE ÷ MAPE(better baseline). Direction = share of rows where the predicted move from the May price had the right sign (P1 predicts no move, so it has none).

| Crop | Model | Rows (units) | MAPE (90% CI) | Skill (90% CI) | Direction | Coverage 10–90 (n) |
|---|---|---|---|---|---|---|
| Tur | P1 | 65 (5) | 26.1% (16.8–37.2) | −0.20 (−0.50, 0.00) | — | 65% (65) |
| **Tur** | **P2** (better baseline) | 65 | **21.8%** (13.3–31.8) | — | 71% | **72% (65)** |
| Tur | ML ridge | 65 | 24.4% (14.4–37.2) | −0.12 (−0.56, +0.19) | 65% | 75% (55) |
| **Maize** | **P1** (better baseline) | 46 (5) | **13.0%** (10.1–16.5) | — | — | **67% (46)** |
| Maize | P2 | 46 | 18.4% (13.6–23.9) | −0.41 (−0.97, −0.02) | 50% | 61% (46) |
| Maize | ML ridge | 46 | 12.8% (9.1–16.6) | +0.02 (−0.27, +0.25) | 63% | 67% (46) |
| Soybean | P1 (better baseline) | 23 (2) | 13.7% (8.0–20.8) | — | — | 71% (21) |
| Soybean | P2 | 23 | 15.0% (9.6–21.1) | −0.10 (−0.79, +0.33) | 61% | 76% (21) |
| **Soybean** | **ML ridge** | 23 | **12.1%** (7.8–17.6) | **+0.11 (−0.27, +0.38)** | **61%** | **94% (16)** |
| Cotton | P1 | 29 (4) | 16.6% (11.3–22.8) | −0.16 (−0.58, +0.18) | — | 66% (29) |
| **Cotton** | **P2** (better baseline) | 29 | **14.4%** (11.2–18.2) | — | 62% | **86% (29)** |
| Cotton | ML ridge | 29 | 14.6% (8.9–21.0) | −0.02 (−0.51, +0.38) | 62% | 72% (29) |

## 6. Selection decision (20 October 2026, rules v1.0 §2)

| Crop | Shipped | Reason |
|---|---|---|
| Tur | P2 seasonal naive | Ridge skill −0.12 < 0.05 |
| Maize | P1 persistence | Ridge skill +0.02 < 0.05 |
| **Soybean** | **Ridge (ML)** | Skill +0.11 ≥ 0.05 and direction 61% > 50% |
| Cotton | P2 seasonal naive | Ridge skill −0.02 < 0.05 |

**AC-05:** ML is used for 2 crops (tur yield, soybean price), so contingency 2.25 was not run. Both wins have 90% CIs that include 0. They pass the frozen rules on point estimates and could be chance.

## 7. Known failure cases

- **Tur price swings:** MAPE 22–26% for every model. The worst seasons for the shipped P2 are 2014 (mean error 34%), 2015 (53%) and 2016 (46%), then 2020, 2022–2024 (21–30%). No model, including ML, anticipated these from May data.
- **Soybean ML** rests on 23 rows from 2 units over 13 seasons. Its 94% coverage means its ranges are on the wide side.
- **Cotton in Bidar** has too few price seasons to enter the backtest at all (cotton is scored in 4 units).
- **Thin markets:** some unit-months trade a few tonnes (e.g. Ballari tur March 2025: 2 t). Such anchors are not used at export (D-17).

## 8. Kharif 2027 export (task 2.31, `data/export_price.json`)

Forecasts are made **as of 31 May 2025** (D-14): the May 2026 and May 2027 prices are not in the downloaded data. Soybean is made as of 31 May 2024 (D-18). 17 unit × crop pairs:

- **9** from the unit's own anchor month.
- **6** borrow the median of other units' forecasts for that crop (D-17). These have no usable 2025 anchor: Kalaburagi+Yadgir and Bidar maize and cotton, Ballari tur and Ballari cotton. They are flagged `borrowed_from_units`.
- **2** soybean pairs, as of May 2024.

Each pair carries its model's past log-errors keyed by season, for paired-season sampling in the engine. Pairs with < 5 own errors use the crop's errors from all units (flagged).
