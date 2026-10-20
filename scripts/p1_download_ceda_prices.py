"""Task 1.04: download monthly prices and arrivals from CEDA Agri Market Data.

Calls the same API the CEDA website uses (agmarknet.ceda.ashoka.edu.in/api/prices and
/api/quantities), for the Kalyana-Karnataka districts (Census 2011 boundaries) and the
four candidate crops. Writes one raw CSV per endpoint and logs it in raw/raw_sources_log.csv.

Usage: .venv/bin/python scripts/p1_download_ceda_prices.py [commodity_id ...]
(no ids = all commodities below)
"""
import csv
import datetime as dt
import json
import sys
import ssl
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
API = "https://agmarknet.ceda.ashoka.edu.in/api"
STATE_ID = 29  # Karnataka (Census 2011)
START, END = "2001-01-01", dt.date.today().isoformat()

try:  # python.org builds on macOS ship without CA certificates
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()

# Census 2011 districts. Vijayanagara (2021) is inside Bellary here.
DISTRICTS = {579: "Gulbarga", 580: "Yadgir", 558: "Bidar", 559: "Raichur", 560: "Koppal", 565: "Bellary"}

# Both tur entries are kept; which one to use is decided in task 1.36.
COMMODITIES = {49: "Arhar (Tur/Red Gram)(Whole)", 7: "Red Gram", 4: "Maize",
               13: "Soyabean", 15: "Cotton"}  # maize replaced green gram (decision D-05)


def post(endpoint, body, tries=4):
    data = json.dumps(body).encode()
    for attempt in range(tries):
        try:
            req = urllib.request.Request(f"{API}/{endpoint}", data=data,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120, context=SSL_CTX) as r:
                return json.load(r).get("data", [])
        except Exception as e:  # the API fails intermittently; retry with backoff
            if attempt == tries - 1:
                raise RuntimeError(f"{endpoint} {body}: {e}") from e
            time.sleep(3 * (attempt + 1))


def main():
    commodities = {c: COMMODITIES[c] for c in map(int, sys.argv[1:])} or COMMODITIES
    tag = "" if commodities is COMMODITIES else "_" + "-".join(map(str, commodities))
    today = dt.date.today().strftime("%Y%m%d")
    failures = []
    for endpoint in ("prices", "quantities"):
        rows = []
        for cid, cname in commodities.items():
            for did, dname in DISTRICTS.items():
                body = {"state_id": STATE_ID, "commodity_id": cid, "district_id": did,
                        "calculation_type": "m", "start_date": START, "end_date": END}
                try:
                    got = post(endpoint, body)
                except RuntimeError as e:
                    # Record the gap instead of stopping; it goes into the gap register.
                    failures.append(f"{endpoint} {cname} {dname}: {e.__cause__}")
                    print(f"{endpoint:10} {cname:30} {dname:9} FAILED ({e.__cause__})")
                    continue
                for r in got:
                    rows.append({"commodity_id": cid, **r})
                print(f"{endpoint:10} {cname:30} {dname:9} {len(got):4} months")
                time.sleep(0.5)
        out = RAW / f"raw_ceda_{endpoint}_kk{tag}_{today}.csv"
        fields = sorted({k for r in rows for k in r}, key=lambda k: (k != "t", k))
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        months = sorted(r["t"] for r in rows)
        coverage = f"{len(rows)} district-months, {months[0]} to {months[-1]}" if months else "empty"
        with (RAW / "raw_sources_log.csv").open("a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([out.name, "CEDA Agri Market Data", f"{API}/{endpoint}",
                                    dt.date.today().isoformat(), coverage,
                                    f"Monthly {endpoint}; {START} to {END}; Census 2011 districts; "
                                    "commodity ids " + ",".join(map(str, commodities))])
        print(f"wrote {out.name}: {coverage}")
    if failures:
        (RAW / f"raw_ceda_failures{tag}_{today}.txt").write_text("\n".join(failures) + "\n", encoding="utf-8")
        print(f"{len(failures)} request(s) failed; see raw_ceda_failures{tag}_{today}.txt")


if __name__ == "__main__":
    main()
