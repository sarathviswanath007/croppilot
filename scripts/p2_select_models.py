"""Tasks 2.23, 2.24, 2.26: apply selection_rules.md v1.0 per crop, exactly as written.

Yield (section 1): lowest hindcast MAE among M1, M2; used only if its MAE < B1's. Ties (MAE
within 1% of the lowest) go to the simpler model: B1 > M1 > M2.
Price (section 2): ML only if MAPE skill vs the better of P1, P2 >= 0.05 AND direction
accuracy > 50%; otherwise the better baseline.
Task 2.26 (A-09): reports where each crop's backtest sits against the confidence thresholds
(section 3). The thresholds themselves are not changed.

Inputs:  data/backtest_yield_metrics.csv, data/backtest_price_metrics.csv
Output:  data/model_selection.csv
Usage:   python3 scripts/p2_select_models.py
"""
from p2_asof import CROPS, DATA, read_csv
from p2_run_yield_backtest import write

YIELD_ORDER = ["B1", "M1", "M2"]          # simplest first
TIE = 0.01
PRICE_MIN_SKILL, PRICE_MIN_DIRECTION = 0.05, 0.5


def select_yield(metrics):
    """metrics: {model: row}. Returns (model, reason)."""
    mae = {m: float(metrics[m]["mae_kg_ha"]) for m in YIELD_ORDER if m in metrics}
    best_candidate = min(("M1", "M2"), key=lambda m: mae[m])
    if mae[best_candidate] >= mae["B1"]:
        return "B1", f"{best_candidate} MAE {mae[best_candidate]} does not beat B1 {mae['B1']}"
    lowest = min(mae.values())
    for m in YIELD_ORDER:
        if mae[m] <= lowest * (1 + TIE):
            if m == best_candidate:
                return m, f"{m} MAE {mae[m]} beats B1 {mae['B1']} (skill {metrics[m]['skill_vs_b1']}), outside the 1% tie margin"
            return m, f"{best_candidate} MAE {mae[best_candidate]} beats B1 {mae['B1']} by < 1%: tie goes to the simpler {m}"


def select_price(metrics):
    better = metrics["ML"]["better_baseline"]
    ml = metrics["ML"]
    skill, direction = float(ml["skill_vs_better_baseline"]), float(ml["direction_accuracy"])
    if skill >= PRICE_MIN_SKILL and direction > PRICE_MIN_DIRECTION:
        return "ML", f"skill {skill} >= 0.05 and direction {direction} > 0.5 vs {better}"
    why = []
    if skill < PRICE_MIN_SKILL:
        why.append(f"skill {skill} < 0.05")
    if direction <= PRICE_MIN_DIRECTION:
        why.append(f"direction {direction} <= 0.5")
    return better, f"ML fails ({'; '.join(why)}); {better} is the better baseline"


def threshold_note(row):
    cov = row["coverage_10_90"]
    if cov == "":
        return "no interval scored"
    cov = float(cov)
    band = "inside 70-90%" if 0.7 <= cov <= 0.9 else ("inside 60-95%" if 0.6 <= cov <= 0.95 else "outside 60-95%")
    return f"coverage {cov:.2f} ({band}, n {row['n_with_interval']})"


def main():
    ym = {}
    for r in read_csv(DATA / "backtest_yield_metrics.csv"):
        ym.setdefault(r["crop"], {})[r["model"]] = r
    pm = {}
    for r in read_csv(DATA / "backtest_price_metrics.csv"):
        pm.setdefault(r["crop"], {})[r["model"]] = r
    out = []
    for crop in CROPS:
        y_model, y_reason = select_yield(ym[crop])
        p_model, p_reason = select_price(pm[crop])
        out.append({"crop": crop, "yield_model": y_model, "yield_reason": y_reason,
                    "yield_skill": ym[crop][y_model]["skill_vs_b1"],
                    "yield_threshold_check": threshold_note(ym[crop][y_model]),
                    "price_model": p_model, "price_reason": p_reason,
                    "price_skill": pm[crop][p_model]["skill_vs_better_baseline"],
                    "price_threshold_check": threshold_note(pm[crop][p_model]),
                    "rules": "selection_rules.md v1.0", "decided": "2026-10-20"})
    write(DATA / "model_selection.csv", out)
    n_ml = sum(1 for r in out if r["yield_model"] in ("M1", "M2") or r["price_model"] == "ML")
    for r in out:
        print(f"{r['crop']:8} yield {r['yield_model']:3} | price {r['price_model']:3} | {r['yield_reason']} | {r['price_reason']}")
    print(f"crops using ML for yield or price: {n_ml} (AC-05 needs >= 2; contingency 2.25 {'not needed' if n_ml >= 2 else 'REQUIRED'})")


if __name__ == "__main__":
    main()
