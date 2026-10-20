"""Tasks 2.08 and 2.18: harvest-price target and features per unit x crop x season (PRD 4.3).

For Kharif season Y (sown in year Y), with the harvest-marketing window from
data/harvest_windows.csv (months Jun-Dec belong to year Y, Jan-May to Y + 1):
  window_price     mean monthly modal price over the window                       [Data target]
                   [Assumption] needs at least half the window's months (rounded up)
  may_price        modal price of May Y, else April, else March Y (anchor_month)  [Data]
  target           log(window_price / may_price)                                    (modelled)
Features, all known on 31 May Y (p2_asof):
  f_mean12         log(mean modal Jun Y-1 .. May Y / may_price); needs >= 6 months
  f_last_window    log(window_price of Y-1 / may_price)
  f_msp            log(MSP as of 31 May Y / may_price) (decision D-08)
  f_arrivals       log(mean monthly window arrivals of Y-1 / mean of the windows Y-1 .. Y-5);
                   needs >= 3 of those windows
[Assumption] A missing f_mean12 or f_arrivals is set to 0 (= "no change from normal") and
flagged; a missing May anchor or last window price leaves the row out of model training.

Inputs:  data/prices_monthly.csv, data/harvest_windows.csv, data/msp.csv
Output:  data/features_price.csv
Usage:   python3 scripts/p2_build_features_price.py
"""
import csv
import math

from p2_asof import DATA, load_msp, month_key, msp_asof, read_csv

ALL_FEATURES = ["f_mean12", "f_last_window", "f_msp", "f_arrivals"]
# f_arrivals is kept in the file but not used by the models: CEDA arrivals have reporting
# breaks (e.g. Raichur cotton ~2,600 t/month -> 24 -> 55,000), decision D-16, gap G22.
PRICE_FEATURES = ["f_mean12", "f_last_window", "f_msp"]
FIRST_SEASON, LAST_SEASON = 2002, 2025


def load_prices():
    """{(unit, crop): {'YYYY-MM': (modal, arrivals or None)}}"""
    out = {}
    for r in read_csv(DATA / "prices_monthly.csv"):
        arr = float(r["arrivals_t"]) if r["arrivals_t"] else None
        out.setdefault((r["unit"], r["crop"]), {})[r["month"]] = (float(r["modal_rs_per_q"]), arr)
    return out


def load_windows():
    return {r["crop"]: [int(m) for m in r["months"].split(";")] for r in read_csv(DATA / "harvest_windows.csv")}


def window_months(months, season):
    return [month_key(season if m >= 6 else season + 1, m) for m in months]


def window_stats(series, months, season):
    """(mean modal price, mean monthly arrivals or None) over the window, or (None, None)."""
    got = [series[k] for k in window_months(months, season) if k in series]
    if len(got) < math.ceil(len(months) / 2):
        return None, None
    arrivals = [a for _, a in got if a is not None]
    return sum(p for p, _ in got) / len(got), (sum(arrivals) / len(arrivals) if arrivals else None)


def anchor(series, season):
    for m in (5, 4, 3):
        k = month_key(season, m)
        if k in series:
            return series[k][0], k
    return None, None


def build():
    prices, windows, msp = load_prices(), load_windows(), load_msp()
    rows = []
    for (unit, crop), series in sorted(prices.items()):
        months = windows[crop]
        for y in range(FIRST_SEASON, LAST_SEASON + 1):
            win, _ = window_stats(series, months, y)
            may, anchor_month = anchor(series, y)
            if win is None and may is None:
                continue
            last_win, last_arr = window_stats(series, months, y - 1)
            past_arr = [a for k in range(1, 6) for a in [window_stats(series, months, y - k)[1]] if a]
            m12 = [series[month_key(y - 1 + (m < 6), m)][0] for m in (6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5)
                   if month_key(y - 1 + (m < 6), m) in series]
            msp_value, msp_season = msp_asof(msp, crop, y)
            flags = []
            row = {"unit": unit, "crop": crop, "season": y, "window_price": round(win, 1) if win else "",
                   "may_price": may or "", "anchor_month": anchor_month or "",
                   "last_window_price": round(last_win, 1) if last_win else "",
                   "msp_asof": msp_value or "", "msp_season": msp_season or ""}
            if may:
                row["target"] = round(math.log(win / may), 5) if win else ""
                if len(m12) >= 6:
                    row["f_mean12"] = round(math.log(sum(m12) / len(m12) / may), 5)
                else:
                    row["f_mean12"] = 0.0
                    flags.append("f_mean12_imputed")
                row["f_last_window"] = round(math.log(last_win / may), 5) if last_win else ""
                row["f_msp"] = round(math.log(msp_value / may), 5) if msp_value else ""
                if last_arr and len(past_arr) >= 3:
                    row["f_arrivals"] = round(math.log(last_arr / (sum(past_arr) / len(past_arr))), 5)
                else:
                    row["f_arrivals"] = 0.0
                    flags.append("f_arrivals_imputed")
            row["flags"] = ";".join(flags)
            rows.append(row)
    return rows


def main():
    rows = build()
    fields = ["unit", "crop", "season", "window_price", "may_price", "anchor_month", "last_window_price",
              "msp_asof", "msp_season", "target", *ALL_FEATURES, "flags"]
    with (DATA / "features_price.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, restval="")
        w.writeheader()
        w.writerows(rows)
    n_target = sum(1 for r in rows if r.get("target") not in ("", None))
    print(f"features_price.csv: {len(rows)} rows, {n_target} with a target")


if __name__ == "__main__":
    main()
