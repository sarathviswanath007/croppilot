"""Tasks 1.45-1.46: inflate the latest CACP Karnataka costs to the target season -> costs.csv.

PRD 6.5: C = A2+FL per ha (Karnataka, cost year Y) x inflation(Y -> T) / 2.471

[Assumption] Inflation is a flat 3% a year (decision D-09), standing in for CPI-AL until the
official series is collected. Years = target season start minus cost season start
(2024-25 -> Kharif 2027 = 3 years).

Input:  data/costs_karnataka_per_ha.csv (from p1_build_cacp_costs.py)
Output: data/costs.csv
Usage:  python3 scripts/p1_build_costs.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
HA_PER_ACRE = 1 / 2.471
TARGET_SEASON_START = 2027          # Kharif 2027
ANNUAL_INFLATION = 0.03             # [Assumption] D-09
COST_BAND = (-0.10, 0.15)           # PRD 6.5 [Assumption]


def main():
    with (DATA / "costs_karnataka_per_ha.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = []
    for crop in sorted({r["crop"] for r in rows}):
        latest = max((r for r in rows if r["crop"] == crop), key=lambda r: r["year"])
        years = TARGET_SEASON_START - int(latest["year"][:4])
        factor = (1 + ANNUAL_INFLATION) ** years
        a2fl_acre = float(latest["a2fl_per_ha"]) * HA_PER_ACRE
        c2_acre = float(latest["c2_per_ha"]) * HA_PER_ACRE
        out.append({
            "crop": crop, "state": "Karnataka", "cost_year": latest["year"],
            "a2fl_per_acre_cost_year": round(a2fl_acre),
            "inflation_factor": round(factor, 4),
            "inflation_basis": f"flat {ANNUAL_INFLATION:.0%}/yr for {years} yr (placeholder for CPI-AL, D-09)",
            "a2fl_per_acre": round(a2fl_acre * factor),
            "c2_per_acre": round(c2_acre * factor),
            "band_low": COST_BAND[0], "band_high": COST_BAND[1],
            "target_season": f"Kharif {TARGET_SEASON_START}",
            "source": latest["source"], "label": "Assumption",
        })
    with (DATA / "costs.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(f"{'crop':8} {'cost year':>9} {'A2+FL/acre':>11} {'x factor':>9} {'Kharif 2027':>12} {'C2 (P2)':>9}")
    for o in out:
        print(f"{o['crop']:8} {o['cost_year']:>9} {o['a2fl_per_acre_cost_year']:>11,} {o['inflation_factor']:>9} "
              f"{o['a2fl_per_acre']:>12,} {o['c2_per_acre']:>9,}")


if __name__ == "__main__":
    main()
