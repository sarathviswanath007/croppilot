"""Tasks 1.36-1.42: clean CEDA monthly prices, aggregate to model units, derive harvest windows.

Cleaning (PRD 5.3, adapted to CEDA's monthly aggregates; decision D-06):
  - keep the four crops (ids from data/map_crop_names.csv); the sparse "Red Gram" id 7 is not used
  - drop a month with a blank or non-positive modal price
  - drop a month whose modal price is < 0.5x or > 2x the median of its neighbouring months
    (+/- 2 months, same district, at least 2 neighbours). This replaces the PRD's 1st/99th
    percentile cap, which would clip genuine low prices from the early 2000s (prices are nominal).
  - flag, but keep, a modal price outside that month's min-max (min/max are sometimes broken
    while the modal price is fine)
  - the PRD's "minimum trading days per month" rule cannot be applied: CEDA has no day counts

Units: districts in one model unit are combined as an arrivals-weighted mean when every
member has arrivals, otherwise a simple mean. Arrivals are summed. [Assumption] CEDA quantities
are tonnes.

Harvest windows (task 1.42, gap G5): for each crop, the share of a year's arrivals that falls
in each calendar month, pooled over units and years. The window is the peak month plus the
adjacent months whose share is at least half the peak's. Marked pending expert check.

Outputs: data/prices_monthly.csv, data/prices_dropped.csv, data/harvest_windows.csv
Usage:   python3 scripts/p1_build_prices.py
"""
import csv
import statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW, DATA = ROOT / "raw", ROOT / "data"
SPIKE_LOW, SPIKE_HIGH = 0.5, 2.0
WINDOW_SHARE_OF_PEAK = 0.5
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def read(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def month_index(t):
    y, m = map(int, t.split("-"))
    return y * 12 + m - 1


def latest(pattern):
    files = sorted(RAW.glob(pattern))
    if not files:
        raise SystemExit(f"missing raw file {pattern}; run p1_download_ceda_prices.py")
    return files[-1]


def load():
    crops = {r["ceda_commodity_id"]: r["crop_key"] for r in read(DATA / "map_crop_names.csv")}
    units = {r["ceda_census2011_name"]: r["model_unit"] for r in read(DATA / "map_district_units.csv")
             if r["ceda_census2011_name"]}
    prices = read(latest("raw_ceda_prices_kk_2*.csv")) + read(latest("raw_ceda_prices_kk_4_*.csv"))
    qty_rows = read(latest("raw_ceda_quantities_kk_2*.csv")) + read(latest("raw_ceda_quantities_kk_4_*.csv"))
    qty = {(r["commodity_id"], r["district"], r["t"]): float(r["qty"]) for r in qty_rows if r["qty"]}
    return crops, units, prices, qty


def clean(crops, units, prices):
    kept, dropped = [], []
    series = defaultdict(dict)  # (crop, district) -> month index -> modal
    for r in prices:
        if r["commodity_id"] not in crops or r["district"] not in units:
            continue
        base = {"crop": crops[r["commodity_id"]], "district": r["district"], "month": r["t"],
                "p_modal": r["p_modal"]}
        if not r["p_modal"] or float(r["p_modal"]) <= 0:
            dropped.append({**base, "reason": "blank or non-positive modal price", "detail": ""})
            continue
        series[(base["crop"], r["district"])][month_index(r["t"])] = float(r["p_modal"])
        kept.append(r)

    same_month = defaultdict(dict)  # (crop, month index) -> district -> modal
    for (crop, district), ser in series.items():
        for m, v in ser.items():
            same_month[(crop, m)][district] = v

    out = []
    for r in kept:
        crop, district, m = crops[r["commodity_id"]], r["district"], month_index(r["t"])
        modal = float(r["p_modal"])
        ser = series[(crop, district)]
        base = {"crop": crop, "district": district, "month": r["t"], "p_modal": r["p_modal"]}
        neighbours = [ser[m + d] for d in (-2, -1, 1, 2) if m + d in ser]
        if len(neighbours) >= 2:
            ratio = modal / st.median(neighbours)
            if not SPIKE_LOW <= ratio <= SPIKE_HIGH:
                dropped.append({**base, "reason": "spike vs neighbouring months",
                                "detail": f"ratio {ratio:.2f} to median of {[round(x) for x in neighbours]}"})
                continue
        # Second check, for months the first cannot judge well: other districts, same month.
        others = [v for d, v in same_month[(crop, m)].items() if d != district]
        if len(others) >= 2:
            ratio = modal / st.median(others)
            if not SPIKE_LOW <= ratio <= SPIKE_HIGH:
                dropped.append({**base, "reason": "outlier vs other districts in the same month",
                                "detail": f"ratio {ratio:.2f} to median of {[round(x) for x in others]}"})
                continue
        lo = float(r["p_min"]) if r["p_min"] else None
        hi = float(r["p_max"]) if r["p_max"] else None
        flag = "modal_outside_min_max" if lo is not None and hi is not None and not lo <= modal <= hi else ""
        out.append({"crop": crop, "district": district, "month": r["t"], "modal": modal,
                    "min": lo, "max": hi, "flag": flag, "commodity_id": r["commodity_id"]})
    return out, dropped


def aggregate(rows, units, qty):
    cells = defaultdict(list)
    for r in rows:
        r["arrivals_t"] = qty.get((r["commodity_id"], r["district"], r["month"]))
        cells[(units[r["district"]], r["crop"], r["month"])].append(r)
    panel = []
    for (unit, crop, month), parts in sorted(cells.items()):
        weights = [p["arrivals_t"] for p in parts]
        weighted = all(w for w in weights)
        if weighted:
            modal = sum(p["modal"] * w for p, w in zip(parts, weights)) / sum(weights)
        else:
            modal = st.mean(p["modal"] for p in parts)
        arrivals = sum(w for w in weights if w)
        flags = sorted({p["flag"] for p in parts if p["flag"]} | ({"unweighted_mean"} if len(parts) > 1 and not weighted else set()))
        panel.append({"unit": unit, "crop": crop, "month": month, "modal_rs_per_q": round(modal, 1),
                      "arrivals_t": round(arrivals, 1) if arrivals else "",
                      "n_districts": len(parts), "districts": "+".join(p["district"] for p in parts),
                      "flags": ";".join(flags), "source": "CEDA Agri Market Data", "label": "Data"})
    return panel


def harvest_windows(panel):
    out = []
    for crop in sorted({p["crop"] for p in panel}):
        shares = defaultdict(list)
        years = defaultdict(lambda: defaultdict(float))
        for p in panel:
            if p["crop"] == crop and p["arrivals_t"]:
                years[(p["unit"], p["month"][:4])][int(p["month"][5:])] += float(p["arrivals_t"])
        for by_month in years.values():
            total = sum(by_month.values())
            if len(by_month) >= 10 and total > 0:  # only near-complete years
                for m in range(1, 13):
                    shares[m].append(by_month.get(m, 0) / total)
        mean_share = {m: st.mean(shares[m]) for m in range(1, 13)}
        peak = max(mean_share, key=mean_share.get)
        window = [peak]
        for step in (-1, 1):  # grow outwards from the peak, wrapping around the year
            m = peak
            while True:
                m = (m - 1 + step) % 12 + 1
                if mean_share[m] < WINDOW_SHARE_OF_PEAK * mean_share[peak] or m in window:
                    break
                window.insert(0, m) if step < 0 else window.append(m)
        out.append({"crop": crop, "window": "-".join(MONTH_NAMES[m - 1] for m in window),
                    "months": ";".join(str(m) for m in window),
                    "share_of_arrivals": round(sum(mean_share[m] for m in window), 3),
                    "peak_month": MONTH_NAMES[peak - 1],
                    "monthly_shares": ";".join(f"{MONTH_NAMES[m - 1]}:{mean_share[m]:.3f}" for m in range(1, 13)),
                    "n_unit_years": len(shares[1]), "status": "pending expert check",
                    "label": "Assumption"})
    return out


def main():
    crops, units, prices, qty = load()
    rows, dropped = clean(crops, units, prices)
    panel = aggregate(rows, units, qty)
    windows = harvest_windows(panel)
    write(DATA / "prices_monthly.csv", panel)
    write(DATA / "prices_dropped.csv", dropped)
    write(DATA / "harvest_windows.csv", windows)

    reasons = defaultdict(int)
    for d in dropped:
        reasons[d["reason"]] += 1
    print(f"district-months kept: {len(rows)}  dropped: {dict(reasons)}")
    print(f"flagged modal outside min-max (kept): {sum(r['flag'] == 'modal_outside_min_max' for r in rows)}")
    print(f"prices_monthly.csv: {len(panel)} unit-months")
    print("\nharvest windows from arrival peaks:")
    for w in windows:
        print(f"  {w['crop']:8} {w['window']:16} {w['share_of_arrivals']:.0%} of arrivals  "
              f"(peak {w['peak_month']}, {w['n_unit_years']} unit-years)")
    print("\nmonths with prices, per unit and crop:")
    count = defaultdict(int)
    for p in panel:
        count[(p["unit"], p["crop"])] += 1
    for unit in sorted({p["unit"] for p in panel}):
        print(f"  {unit:22}" + "".join(f"{c}:{count[(unit, c)]:4}  " for c in ("tur", "maize", "soybean", "cotton")))


if __name__ == "__main__":
    main()
