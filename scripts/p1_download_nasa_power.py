"""Task 1.08: download NASA POWER daily weather for each district reference point.

Parameters: PRECTOTCORR (rain, mm/day), T2M_MAX (C), T2M_MIN (C). Community AG. No API key.
Points come from data/district_points.csv. One raw CSV per district, logged in raw_sources_log.csv.

Usage: .venv/bin/python scripts/p1_download_nasa_power.py
"""
import csv
import datetime as dt
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
API = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMS = "PRECTOTCORR,T2M_MAX,T2M_MIN"
START, END = "19810101", "20251231"

try:  # python.org builds on macOS ship without CA certificates
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()


def main():
    today = dt.date.today()
    with (ROOT / "data" / "district_points.csv").open(encoding="utf-8") as f:
        points = list(csv.DictReader(f))
    for p in points:
        query = urllib.parse.urlencode({"parameters": PARAMS, "community": "AG", "format": "CSV",
                                        "latitude": p["latitude"], "longitude": p["longitude"],
                                        "start": START, "end": END})
        url = f"{API}?{query}"
        out = RAW / f"raw_nasapower_daily_{p['icrisat_name'].lower()}_{today:%Y%m%d}.csv"
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url, timeout=300, context=SSL_CTX) as r:
                    body = r.read()
                break
            except Exception as e:
                if attempt == 3:
                    raise
                print(f"  retry {p['icrisat_name']}: {e}")
                time.sleep(5 * (attempt + 1))
        out.write_bytes(body)
        n_days = body.count(b"\n") - body.split(b"-END HEADER-")[0].count(b"\n") - 2
        with (RAW / "raw_sources_log.csv").open("a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([out.name, "NASA POWER", url, today.isoformat(),
                                    f"{START}-{END}, {n_days} days, point {p['latitude']},{p['longitude']}",
                                    f"Daily {PARAMS}; community AG"])
        print(f"{p['icrisat_name']:9} {n_days} days -> {out.name}")
        time.sleep(1)


if __name__ == "__main__":
    main()
