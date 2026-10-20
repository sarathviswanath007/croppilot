"""Task 2.05: yield feature matrix = counting panel rows x same-season weather (PRD 4.2).

One row per unit x crop x season with >= 500 ha (rows below that are left out; PRD 5.5).
Weather columns are the actual weather of that season: they are used for training and for
hindcasts only. At decision time the models are run under every historical weather season.

Features used by the models (fixed before any backtest was run; decision D-12):
  unit indicator, season year (trend), rain_jun .. rain_oct, rain_jjas, rainy_days_jjas,
  dry_spell_ja, tmax_as
  Left out: heavy_rain_days_so. NASA POWER gives 0 in almost every season (gap G10), so it
  carries no signal. Irrigated share (optional in the PRD) is not in the panel.

Inputs:  data/panel_yield.csv, data/weather_features.csv
Output:  data/features_yield.csv
Usage:   python3 scripts/p2_build_features_yield.py
"""
import csv

from p2_asof import DATA, load_panel, read_csv

WEATHER_FEATURES = ["rain_jun", "rain_jul", "rain_aug", "rain_sep", "rain_oct", "rain_jjas",
                    "rainy_days_jjas", "dry_spell_ja", "tmax_as"]


def load_weather():
    """{(unit, season_start_year): {feature: float}}"""
    return {(r["unit"], int(r["season_start_year"])): {f: float(r[f]) for f in WEATHER_FEATURES}
            for r in read_csv(DATA / "weather_features.csv")}


def build():
    weather = load_weather()
    rows = []
    for r in load_panel():
        w = weather.get((r["unit"], r["season"]))
        if w is None:
            raise SystemExit(f"no weather for {r['unit']} {r['season']}")
        rows.append({"unit": r["unit"], "crop": r["crop"], "season": r["season"],
                     "yield_kg_ha": r["yield_kg_ha"], **w, "flags": r["flags"]})
    rows.sort(key=lambda r: (r["crop"], r["unit"], r["season"]))
    return rows


def main():
    rows = build()
    with (DATA / "features_yield.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    counts = {}
    for r in rows:
        counts[r["crop"]] = counts.get(r["crop"], 0) + 1
    print(f"features_yield.csv: {len(rows)} rows", counts)


if __name__ == "__main__":
    main()
