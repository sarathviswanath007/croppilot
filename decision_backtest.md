# Polaris CropPilot: Decision Backtest (task 3.37, PRD 9.3)

**Run:** 20 October 2026 · `scripts/p3_decision_backtest.py` · rows in `data/decision_backtest_rows.csv`

**What this is.** For each season 2012–2019 and each district unit, CropPilot ranked a standard farm (rain-fed, balanced risk, district-average soil) using only what was known on 31 May that year. Each crop's *realised* profit per acre was then computed from that season's actual district yield, actual harvest-window price and cost. Regret = the best crop's realised profit minus the chosen crop's. `[Prediction (backtest)]`

**Caveats.** These are district averages, not farm outcomes. Costs before 2024-25 are back-cast at 3% a year `[Assumption]`. Only crops with both an actual yield and an actual market price that season are compared, so some unit-seasons compare 2 or 3 crops, not 4. Seasons are few (8), so differences are uncertain.

**Unit-seasons where all three strategies could pick:** 37 (of 37 with ≥ 2 comparable crops).

| Strategy | Mean regret (₹/acre) | Median regret | 10th-percentile realised profit (₹/acre) | Picked the best crop |
|---|---|---|---|---|
| CropPilot top pick | 3,328 | 0 | -5,779 | 29 of 37 (78%) |
| Always tur | 6,986 | 1,824 | -7,853 | 16 of 37 (43%) |
| Last season's most profitable | 3,028 | 0 | -6,595 | 28 of 37 (76%) |

## Per season

| Season | Unit-seasons | CropPilot mean regret | Always-tur mean regret | Last-best mean regret |
|---|---|---|---|---|
| 2012 | 5 | 0 | 5,933 | 4,275 |
| 2013 | 3 | 0 | 11,114 | 0 |
| 2014 | 4 | 266 | 2,738 | 266 |
| 2015 | 5 | 709 | 709 | 0 |
| 2016 | 5 | 6,082 | 6,082 | 0 |
| 2017 | 5 | 0 | 3,458 | 988 |
| 2018 | 5 | 11,005 | 13,174 | 11,058 |
| 2019 | 5 | 6,622 | 13,486 | 5,877 |

## What CropPilot picked

tur: 19, cotton: 13, maize: 5.

## Reading

- CropPilot's pick clearly did better than **always growing tur**: about half the average regret, and the best crop in 78% of unit-seasons versus 43%.
- Against **last season's most profitable crop**, CropPilot is roughly level: slightly higher mean regret (₹3,328 vs ₹3,028 per acre), slightly better 10th-percentile profit (−₹5,779 vs −₹6,595) and about the same hit rate (78% vs 76%). With 37 unit-seasons over 8 seasons, this difference is within noise. CropPilot is **not** shown to beat this heuristic.
- The largest misses are 2016 and 2018–2019, seasons in which prices or yields moved far from their recent history.
