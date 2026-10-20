"""Tasks 1.43/1.44: check the hand-transcribed CACP Karnataka cost tables and derive cost concepts.

Inputs (transcribed by hand from the scanned CACP Kharif 2026-27 report, see raw_sources_log.csv):
  data/cacp_karnataka_cost_breakup_transcribed.csv  Annex 5.6, Rs/ha, 2022-23 to 2024-25
  data/cacp_karnataka_projected_cop_transcribed.csv Annex 5.5, Rs/quintal, KMS 2026-27

Every printed subtotal is re-added from its items, so a misread digit shows up as a mismatch.

Cost concepts [Assumption: derived with the standard CACP definitions, not printed in Annex 5.6]:
  C2    = operational cost + fixed cost
  A2+FL = C2 - rental value of owned land - interest on fixed capital
  A2    = A2+FL - family labour

Output: data/costs_karnataka_per_ha.csv
Usage:  python3 scripts/p1_build_cacp_costs.py
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BREAKUP = ROOT / "data" / "cacp_karnataka_cost_breakup_transcribed.csv"
PROJECTED = ROOT / "data" / "cacp_karnataka_projected_cop_transcribed.csv"
OUT = ROOT / "data" / "costs_karnataka_per_ha.csv"
HA_PER_ACRE = 1 / 2.471
TOLERANCE = 2  # Rs; printed values are individually rounded

SUBTOTALS = {
    "hl_total": ["hl_casual", "hl_attached", "hl_family"],
    "bl_total": ["bl_hired", "bl_owned"],
    "ml_total": ["ml_hired", "ml_owned"],
    "fert_manure_total": ["fert", "manure"],
    "op_total": ["hl_total", "bl_total", "ml_total", "seed", "fert_manure_total", "insecticides",
                 "irrigation", "crop_insurance", "interest_working_capital", "misc"],
    "fixed_total": ["rental_value_owned_land", "rent_leased_in_land", "land_revenue",
                    "depreciation", "interest_fixed_capital"],
}


def read(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    rows = read(BREAKUP)
    errors = []
    out = []
    for r in rows:
        v = {k: float(x) for k, x in r.items() if k not in ("crop", "year", "annex_table")}
        for total, parts in SUBTOTALS.items():
            diff = sum(v[p] for p in parts) - v[total]
            if abs(diff) > TOLERANCE:
                errors.append(f"{r['crop']} {r['year']}: {total} off by {diff:+.0f}")
        c2 = v["op_total"] + v["fixed_total"]
        a2fl = c2 - v["rental_value_owned_land"] - v["interest_fixed_capital"]
        a2 = a2fl - v["hl_family"]
        out.append({
            "crop": r["crop"], "year": r["year"], "state": "Karnataka",
            "a2_per_ha": round(a2), "a2fl_per_ha": round(a2fl), "c2_per_ha": round(c2),
            "a2fl_per_acre": round(a2fl * HA_PER_ACRE), "c2_per_acre": round(c2 * HA_PER_ACRE),
            "yield_q_per_ha": v["yield_q_per_ha"],
            "source": f"CACP Price Policy for Kharif Crops 2026-27, Annex {r['annex_table']}, "
                      f"printed p.{int(v['printed_page'])}",
            "label": "Data (derived)",
        })

    if errors:
        print("SUBTOTAL CHECK FAILED: re-read these values in the PDF")
        for e in errors:
            print("  " + e)
        sys.exit(1)
    print(f"subtotal check passed for {len(rows)} crop-years")

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(f"wrote {OUT.relative_to(ROOT)}")

    # Plausibility check: the A2+FL share of C2 in the latest actual year should be close to
    # the share in CACP's own KMS 2026-27 projection (Annex 5.5).
    latest = {o["crop"]: o for o in out if o["year"] == "2024-25"}
    print(f"\n{'crop':8} {'A2+FL/ha':>9} {'C2/ha':>8} {'A2+FL/C2':>9} {'projected':>10}  A2+FL/acre")
    for p in read(PROJECTED):
        o = latest[p["crop"]]
        proj = float(p["a2fl_rs_per_q"]) / float(p["c2_rs_per_q"])
        print(f"{p['crop']:8} {o['a2fl_per_ha']:9,} {o['c2_per_ha']:8,} "
              f"{o['a2fl_per_ha'] / o['c2_per_ha']:9.3f} {proj:10.3f}  {o['a2fl_per_acre']:,}")


if __name__ == "__main__":
    main()
