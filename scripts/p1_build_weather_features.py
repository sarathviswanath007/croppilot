"""Tasks 1.28-1.33: daily NASA POWER weather -> seasonal features per model unit (PRD 4.2).

Districts in the same unit are averaged day by day first (an areal series), then features
are computed from that series, so dry spells and heavy-rain days reflect the unit as a whole.

Features for Kharif season Y (calendar year Y; matches agricultural year Y to Y+1):
  rain_jun .. rain_oct       monthly rainfall, mm
  rain_jjas                  June-September total, mm
  rain_jas                   July-September total, mm (protective-irrigation rule, PRD 6.3)
  rainy_days_jjas            days >= 2.5 mm, June-September (IMD convention)
  dry_spell_ja               longest run of days < 2.5 mm within July-August
  heavy_rain_days_so         days >= 64.5 mm, September-October
  tmax_as                    mean daily max temperature, August-September, C

Outputs: data/weather_daily.csv, data/weather_features.csv
Usage:   python3 scripts/p1_build_weather_features.py
"""
import csv
import datetime as dt
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW, DATA = ROOT / "raw", ROOT / "data"
RAINY_MM, HEAVY_MM = 2.5, 64.5
FILL = -999.0  # NASA POWER missing-value code
MONTHS = {6: "jun", 7: "jul", 8: "aug", 9: "sep", 10: "oct"}


def read_power(path):
    """Yield (date, rain, tmax, tmin) from a NASA POWER CSV, skipping the header block."""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = lines.index("-END HEADER-") + 1
    for row in csv.DictReader(lines[start:]):
        day = dt.date(int(row["YEAR"]), 1, 1) + dt.timedelta(days=int(row["DOY"]) - 1)
        yield day, float(row["PRECTOTCORR"]), float(row["T2M_MAX"]), float(row["T2M_MIN"])


def longest_dry_run(rains):
    best = run = 0
    for r in rains:
        run = run + 1 if r < RAINY_MM else 0
        best = max(best, run)
    return best


def season_features(days):
    """days: list of (date, rain, tmax) for one unit and one calendar year."""
    by_month = defaultdict(list)
    for d, rain, tmax in days:
        by_month[d.month].append((rain, tmax))
    f = {f"rain_{name}": round(sum(r for r, _ in by_month[m]), 1) for m, name in MONTHS.items()}
    jjas = [r for m in (6, 7, 8, 9) for r, _ in by_month[m]]
    f["rain_jjas"] = round(sum(jjas), 1)
    f["rain_jas"] = round(sum(r for m in (7, 8, 9) for r, _ in by_month[m]), 1)
    f["rainy_days_jjas"] = sum(r >= RAINY_MM for r in jjas)
    f["dry_spell_ja"] = longest_dry_run([r for d, r, _ in sorted(days) if d.month in (7, 8)])
    f["heavy_rain_days_so"] = sum(r >= HEAVY_MM for m in (9, 10) for r, _ in by_month[m])
    tmax_as = [t for m in (8, 9) for _, t in by_month[m]]
    f["tmax_as"] = round(sum(tmax_as) / len(tmax_as), 2)
    return f


def main():
    with (DATA / "district_points.csv").open(encoding="utf-8") as fh:
        points = list(csv.DictReader(fh))

    # unit -> date -> list of (rain, tmax, tmin) across member districts
    series = defaultdict(lambda: defaultdict(list))
    missing = 0
    for p in points:
        files = sorted(RAW.glob(f"raw_nasapower_daily_{p['icrisat_name'].lower()}_*.csv"))
        if not files:
            raise SystemExit(f"no NASA POWER file for {p['icrisat_name']}; run p1_download_nasa_power.py")
        for day, rain, tmax, tmin in read_power(files[-1]):
            if FILL in (rain, tmax, tmin):
                missing += 1
                continue
            series[p["model_unit"]][day].append((rain, tmax, tmin))

    daily = []
    for unit in sorted(series):
        for day in sorted(series[unit]):
            vals = series[unit][day]
            n = len(vals)
            daily.append({"unit": unit, "date": day.isoformat(),
                          "rain_mm": round(sum(v[0] for v in vals) / n, 2),
                          "tmax_c": round(sum(v[1] for v in vals) / n, 2),
                          "tmin_c": round(sum(v[2] for v in vals) / n, 2), "n_points": n})

    by_unit_year = defaultdict(list)
    for d in daily:
        day = dt.date.fromisoformat(d["date"])
        if 6 <= day.month <= 10:
            by_unit_year[(d["unit"], day.year)].append((day, d["rain_mm"], d["tmax_c"]))

    features = []
    for (unit, year), days in sorted(by_unit_year.items()):
        if len(days) < 153:  # June-October must be complete
            print(f"skipping {unit} {year}: only {len(days)} of 153 days")
            continue
        features.append({"unit": unit, "season_start_year": year,
                         "season": f"{year}-{(year + 1) % 100:02d}",
                         **season_features(days), "source": "NASA POWER", "label": "Data"})

    for name, rows in (("weather_daily.csv", daily), ("weather_features.csv", features)):
        with (DATA / name).open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    years = sorted({f["season_start_year"] for f in features})
    print(f"missing daily values skipped: {missing}")
    print(f"weather_features.csv: {len(features)} rows, {len(series)} units, seasons {years[0]}-{years[-1]}")


if __name__ == "__main__":
    main()
