# Polaris CropPilot: Model Selection Rules (tasks 0.31–0.34)

**Status:** FROZEN — transcribed from PRD §4.2, §4.3 and §6.8, approved as written by the project owner (task 0.34). No model or backtest results existed at the time of freezing.
**Frozen on:** 19 October 2026, project owner · **Version:** 1.0

After the freeze, any change needs a dated entry in the change log at the bottom with its reason. A change made after seeing test results must say so.

---

## 1. Yield model selection (PRD §4.2)

**Candidates.** M1 ridge per crop (default), M2 pooled HistGradientBoostingRegressor, optional M3 random forest.
**Baselines.** B1 = mean of the unit's previous five published seasons (primary). B2 = unit linear trend.
**Evaluation.** Rolling-origin hindcast backtests, test seasons 2012 to latest, PRD §9.1. MAE in kg/ha.

**Rule, applied per crop:**

1. Compute hindcast MAE for each candidate model and for B1, over the same test seasons and units.
2. Pick the candidate with the lowest MAE.
3. Use it **only if** its MAE is lower than B1's, so yield MAE skill = 1 − MAE(model) ÷ MAE(B1) > 0.
4. Otherwise use **B1** with its empirical error distribution, and say so in the app and the model card.
5. Ties (MAE within 1%) go to the simpler model: B1 > M1 > M2 > M3. `[Assumption — tie rule added by this draft; not in PRD]`
6. Hyperparameters come from inner time-series CV on training seasons only.

## 2. Harvest-price model ship rule (PRD §4.3)

**Candidates.** Pooled ridge; gradient-boosted alternative.
**Baselines.** P1 persistence (harvest price = May price). P2 seasonal naive (= last year's harvest-window price).
**Better baseline** = whichever of P1, P2 has the lower MAPE for that crop.

**Rule, applied per crop.** Use the ML price model only if **both** hold in backtests `[Assumption thresholds]`:

1. Price MAPE skill = 1 − MAPE(model) ÷ MAPE(better baseline) **≥ 0.05**.
2. Direction-of-change accuracy (vs the May price) **> 50%**.

Otherwise use the better baseline with its empirical log-errors.

The model card must state that the effective sample size is closer to (years × crops) than to (years × crops × districts), and show uncertainty around the metrics.

## 3. Confidence badge thresholds (PRD §6.8) `[Assumption]`

Evaluated per unit × crop. "Coverage" = share of test seasons whose actual yield fell inside the 10th–90th percentile draws.

| Badge | All of these must hold |
|---|---|
| **High** | The chosen model is ML and beat B1 with yield skill ≥ 0.10; coverage between 70% and 90%; ≥ 15 seasons of data for the unit and crop |
| **Medium** | (Skill > 0, **or** the baseline is used) **and** coverage between 60% and 95%; ≥ 10 seasons |
| **Low** | Anything else, **or** soil and drainage both "don't know", **or** assured irrigation |

Farm-profile conditions under **Low** override any model-based badge.

## 4. Shared definitions

- Seasons count only if the unit has ≥ 500 ha of the crop that season (data sufficiency rule, PRD §5.5).
- All metrics are reported per crop, with n. Pooled results never replace per-crop results.
- Test seasons are never used for tuning, feature selection or model choice.

---

## Change log

| Date | Section | Change | Reason | Seen test results first? |
|---|---|---|---|---|
| 2026-10-19 | All | Frozen as v1.0, unchanged from the draft (includes the 1% tie rule in §1.5) | Approved by the project owner | No: no results existed |
