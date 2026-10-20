"""Tasks 1.20-1.25 and 1.49-1.50: build panel_yield.csv from ICRISAT DLD (decision D-04).

Steps (PRD 5.3):
  1. Keep the Kalyana-Karnataka districts and the four crops (data/map_*.csv).
  2. Treat -1 as missing and area 0 as "not grown"; log every dropped value with its reason.
  3. Harmonise districts into the five model units: area is summed, yield is the
     area-weighted mean of ICRISAT's reported yields. (ICRISAT cotton area and production are
     rounded to whole thousands, so recomputing yield from them would add error.)
  4. Flag rows that need care, and check yields against sanity ranges (R4).
  5. Write the coverage grid and apply the data sufficiency rule (PRD 5.5).

[Assumption] ICRISAT "Year" Y is the agricultural year Y to Y+1 (e.g. 1990 -> 1990-91).
[Assumption] Cotton yield stays in kg lint/ha here; lint -> kapas happens in the engine (task 3.14).

Outputs: data/panel_yield.csv, data/panel_yield_dropped.csv, data/panel_yield_coverage.csv
Usage:   python3 scripts/p1_build_panel_yield.py
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "raw_icrisat_apy_unapportioned_india_20261019.json"
DATA = ROOT / "data"
HA_PER_ACRE = 1 / 2.471
MIN_AREA_HA = 500       # PRD 5.5 [Assumption]
MIN_SEASONS = 10        # PRD 5.5 [Assumption]

# Plausible district-average yields, kg/ha (cotton as lint) [Assumption]. Outside = flagged.
SANITY_KG_HA = {"tur": (100, 2500), "maize": (300, 10000), "soybean": (200, 3500), "cotton": (50, 1200)}


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields=None):
    fields = fields or list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def season_label(year):
    return f"{year}-{(year + 1) % 100:02d}"


def load_icrisat():
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    headers = [h["header"] for h in raw["headers"]]
    return [dict(zip(headers, r)) for r in raw["data"] if r[headers.index("State Name")] == "Karnataka"]


def build():
    crops = {r["icrisat_item"]: r["crop_key"] for r in read_csv(DATA / "map_crop_names.csv")}
    units = {r["icrisat_name"]: r["model_unit"] for r in read_csv(DATA / "map_district_units.csv")
             if r["icrisat_name"]}

    rows = [r for r in load_icrisat() if r["Dist Name"] in units]
    years = sorted({int(r["Year"]) for r in rows})

    dropped = []
    present = defaultdict(set)  # (district, year) -> crops with data, to detect merged years
    cells = defaultdict(list)   # (unit, year, crop) -> [(district, area_ha, yield_kg_ha)]
    for r in rows:
        district, year = r["Dist Name"], int(r["Year"])
        for item, crop in crops.items():
            area_k, yld = float(r[f"{item} AREA"]), float(r[f"{item} YIELD"])
            base = {"district": district, "season": season_label(year), "crop": crop,
                    "area_1000ha": area_k, "yield_kg_ha": yld}
            if area_k < 0 or yld < 0:
                dropped.append({**base, "reason": "missing in source (-1)"})
                continue
            present[(district, year)].add(crop)
            if area_k == 0:
                dropped.append({**base, "reason": "not grown (area 0)"})
                continue
            if yld == 0:
                dropped.append({**base, "reason": "area > 0 but yield 0"})
                continue
            cells[(units[district], year, crop)].append((district, area_k * 1000, yld))

    panel = []
    for (unit, year, crop), parts in sorted(cells.items()):
        area = sum(a for _, a, _ in parts)
        yld = sum(a * y for _, a, y in parts) / area
        lo, hi = SANITY_KG_HA[crop]
        flags = []
        if unit == "raichur" and not present[("Koppal", year)]:
            flags.append("includes_koppal")
        if unit == "kalaburagi_yadgir" and not present[("Yadagiri", year)]:
            flags.append("yadgir_inside_kalaburagi")
        if crop == "maize":
            flags.append("all_seasons_not_kharif_only")
        if area < MIN_AREA_HA:
            flags.append("below_500ha")
        if not lo <= yld <= hi:
            flags.append("yield_out_of_sanity_range")
        panel.append({
            "unit": unit, "season": season_label(year), "season_start_year": year, "crop": crop,
            "area_ha": round(area), "production_t": round(area * yld / 1000, 1),
            "yield_kg_ha": round(yld, 1), "yield_q_per_acre": round(yld / 100 * HA_PER_ACRE, 3),
            "yield_basis": "lint" if crop == "cotton" else "grain",
            "n_districts": len(parts), "districts": "+".join(d for d, _, _ in parts),
            "flags": ";".join(flags), "source": "ICRISAT DLD unapportioned", "label": "Data",
        })
    return panel, dropped, years


def coverage(panel, years):
    grid = []
    for unit in sorted({p["unit"] for p in panel}):
        for crop in sorted({p["crop"] for p in panel}):
            ok = [p["season_start_year"] for p in panel
                  if p["unit"] == unit and p["crop"] == crop and p["area_ha"] >= MIN_AREA_HA]
            grid.append({"unit": unit, "crop": crop, "seasons_ge_500ha": len(ok),
                         "first": season_label(min(ok)) if ok else "", "last": season_label(max(ok)) if ok else "",
                         "passes_sufficiency": len(ok) >= MIN_SEASONS,
                         "years_in_source": f"{season_label(years[0])} to {season_label(years[-1])}"})
    return grid


def main():
    panel, dropped, years = build()
    grid = coverage(panel, years)
    write_csv(DATA / "panel_yield.csv", panel)
    write_csv(DATA / "panel_yield_dropped.csv", dropped)
    write_csv(DATA / "panel_yield_coverage.csv", grid)

    print(f"panel rows: {len(panel)}  dropped values: {len(dropped)}")
    reasons = defaultdict(int)
    for d in dropped:
        reasons[d["reason"]] += 1
    for k, v in reasons.items():
        print(f"  dropped - {k}: {v}")
    bad = [p for p in panel if "yield_out_of_sanity_range" in p["flags"]]
    print(f"rows outside sanity range: {len(bad)}")
    for p in bad:
        print(f"  {p['unit']} {p['season']} {p['crop']} {p['yield_kg_ha']} kg/ha on {p['area_ha']} ha")

    crops = sorted({g["crop"] for g in grid})
    print(f"\nseasons with >= {MIN_AREA_HA} ha (pass = at least {MIN_SEASONS})")
    print(f"{'unit':22}" + "".join(f"{c:>10}" for c in crops))
    for unit in sorted({g["unit"] for g in grid}):
        cells = {g["crop"]: g for g in grid if g["unit"] == unit}
        print(f"{unit:22}" + "".join(
            f"{cells[c]['seasons_ge_500ha']:>7} {'ok' if cells[c]['passes_sufficiency'] else '--'}" for c in crops))


if __name__ == "__main__":
    main()
