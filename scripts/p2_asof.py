"""Task 2.01: the information set known on a past decision date (PRD 4.1, 4.5).

Decision date for Kharif season T is 31 May of year T (decision D-01). On that date:
  - yields: only seasons published by then, i.e. season_start_year <= T - YIELD_PUBLICATION_LAG
  - prices: months up to and including May of year T
  - MSP: the season's own MSP only if its announcement date is on or before 31 May T,
    otherwise the previous season's (decision D-08)
  - weather: complete seasons only, i.e. season_start_year <= T - 1 (season T is simulated)

[Assumption] YIELD_PUBLICATION_LAG = 2: district yields for season T-1 (harvested early in T)
are not yet published on 31 May T; season T-2 is. Decision D-12.
[Assumption] A season counts only if the unit has >= 500 ha of the crop (PRD 5.5), so rows
flagged below_500ha are never used for training, baselines or testing.

Every model in Phase 2 reads past data only through these functions.
"""
import csv
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DECISION_MONTH, DECISION_DAY = 5, 31
YIELD_PUBLICATION_LAG = 2   # [Assumption] D-12
FIRST_WEATHER_SEASON = 1991  # PRD 4.4 [Assumption]
UNITS = ["kalaburagi_yadgir", "bidar", "raichur", "koppal", "ballari_vijayanagara"]
CROPS = ["tur", "maize", "soybean", "cotton"]


def read_csv(path):
    with Path(path).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def decision_date(season):
    return dt.date(season, DECISION_MONTH, DECISION_DAY)


def load_panel():
    """Counting yield rows (>= 500 ha) as dicts with numeric year and yield."""
    rows = []
    for r in read_csv(DATA / "panel_yield.csv"):
        if "below_500ha" in r["flags"].split(";"):
            continue
        rows.append({"unit": r["unit"], "crop": r["crop"], "season": int(r["season_start_year"]),
                     "yield_kg_ha": float(r["yield_kg_ha"]), "flags": r["flags"]})
    return rows


def last_published_yield_season(season):
    return season - YIELD_PUBLICATION_LAG


def yields_asof(panel, season):
    """Yield rows published by the decision date of `season`."""
    last = last_published_yield_season(season)
    return [r for r in panel if r["season"] <= last]


def weather_seasons_asof(season, first=FIRST_WEATHER_SEASON):
    """Complete weather seasons available on the decision date of `season`."""
    return list(range(first, season))


def month_key(year, month):
    return f"{year:04d}-{month:02d}"


def last_price_month(season):
    return month_key(season, DECISION_MONTH)


def prices_asof(prices, season):
    """Monthly price rows (keyed by 'YYYY-MM' in r['month']) up to May of `season`."""
    last = last_price_month(season)
    return [r for r in prices if r["month"] <= last]


def load_msp():
    """{crop: {season_start_year: (msp_rs_per_q, announced date or None)}}"""
    out = {}
    for r in read_csv(DATA / "msp.csv"):
        announced = dt.date.fromisoformat(r["announced"]) if r["announced"] else None
        out.setdefault(r["crop"], {})[int(r["season_start_year"])] = (float(r["msp_rs_per_q"]), announced)
    return out


def msp_asof(msp, crop, season):
    """(value, season it belongs to): the season's MSP if announced by 31 May, else last season's."""
    by_season = msp[crop]
    own = by_season.get(season)
    if own and own[1] is not None and own[1] <= decision_date(season):
        return own[0], season
    prev = by_season.get(season - 1)
    return (prev[0], season - 1) if prev else (None, None)
