"""Tasks 3.07-3.24: Python reference engine (PRD section 6). web/js/engine.js is its port;
see that file's header for the method. Pure Python (no numpy) so the arithmetic matches JS.

Usage: from p3_engine import run; run(engine_data_dict, profile_dict)
Profile keys: district, acres, guntas, soil (deep_black | medium_black | shallow_black | red |
unknown), drainage (drains_well | waterlogs | unknown), water (rainfed | protective | assured),
previous_crop, risk (cautious | balanced | growth), late_sowing, and optional dicts own_yield
(q/acre), own_cost (Rs/acre), price_override (Rs/q) keyed by crop. All [Data - farmer-reported].
"""
import math

CROPS = ["tur", "maize", "soybean", "cotton"]
CONF_RANK = {"High": 3, "Medium": 2, "Low": 1}
SOIL_ROW = {"deep_black": "deep_black_drains_well", "medium_black": "medium_black_drains_well",
            "shallow_black": "shallow_black", "red": "red", "unknown": "mixed_or_unknown"}
M32 = 0xFFFFFFFF


def _imul(a, b):
    """JavaScript Math.imul: 32-bit signed product."""
    r = (a * b) & M32
    return r - (1 << 32) if r & 0x80000000 else r


def _i32(x):
    x &= M32
    return x - (1 << 32) if x & 0x80000000 else x


def mulberry32(seed):
    """Task 3.07: the same sequence as engine.js mulberry32."""
    state = [_i32(seed)]

    def rand():
        a = _i32(state[0] + 0x6D2B79F5)
        state[0] = a
        t = _imul(a ^ ((a & M32) >> 15), 1 | a)
        t = _i32(_i32(t + _imul(t ^ ((t & M32) >> 7), 61 | t)) ^ t)
        return ((t ^ ((t & M32) >> 14)) & M32) / 4294967296
    return rand


def percentile(sorted_xs, p):
    pos = p / 100 * (len(sorted_xs) - 1)
    lo, hi = math.floor(pos), math.ceil(pos)
    return sorted_xs[lo] + (sorted_xs[hi] - sorted_xs[lo]) * (pos - lo)


def pcts(xs):
    s = sorted(xs)
    return {"p10": percentile(s, 10), "p50": percentile(s, 50), "p90": percentile(s, 90)}


def clip(x, lo, hi):
    return min(hi, max(lo, x))


def unit_of(data, district):
    for unit, districts in data["units"].items():
        if district in districts:
            return unit
    raise ValueError(f"unknown district {district}")


def condition_key(p):
    return "waterlogs" if p.get("drainage") == "waterlogs" else SOIL_ROW[p.get("soil") or "unknown"]


def top_seasons(seasons):
    count = {}
    for s in seasons:
        count[s] = count.get(s, 0) + 1
    return sorted(count, key=lambda s: (-count[s], s))[:3]


def simulate_crop(data, profile, unit, crop, ci):
    """Tasks 3.08-3.21 for one crop."""
    rules, key = data["rules"], f"{unit}|{crop}"
    adj = rules["adjustments"]
    out = {"crop": crop, "name": data["crops"][crop]["name"], "flags": [], "eligible": True}
    suff = data["sufficiency"].get(key)
    if not suff or not suff["passes"] or key not in data["yield_draws"] or key not in data["price"]:
        out["eligible"] = False
        out["excluded_reason"] = (f"Not enough local data: {suff['seasons_ok'] if suff else 0} seasons with at least "
                                  f"{rules['exclusions']['min_area_ha']} ha (needs {rules['exclusions']['min_seasons']})")
        return out
    if profile.get("late_sowing") and crop in rules["exclusions"]["late_sowing_excluded"]:
        out["eligible"] = False
        out["excluded_reason"] = f"Late sowing (after mid-July) is outside the usual window for {data['crops'][crop]['name']}"
        return out
    tier = rules["suitability"][condition_key(profile)][crop]
    out["tier"] = tier
    if tier == "Not suitable":
        out["eligible"] = False
        out["excluded_reason"] = "Not suitable for this soil and drainage"
        return out
    yd, pr, cost = data["yield_draws"][key], data["price"][key], data["costs"][crop]
    m = rules["multipliers"][tier]
    out["multiplier"] = m
    own = (profile.get("own_yield") or {}).get(crop)
    if own:
        m = clip(own / yd["five_season_mean_q_per_acre"], *adj["calibration_clip"])
        out["calibrated"] = True
        out["multiplier"] = m
    price_override = (profile.get("price_override") or {}).get(crop)
    phat = price_override or pr["forecast"]
    own_cost = (profile.get("own_cost") or {}).get(crop)
    base_cost = own_cost or cost["a2fl_per_acre"]
    band = adj["override_band"] if own_cost else adj["cost_band"]

    n, n_w = adj["n_draws"], len(yd["weather_seasons"])
    rand = mulberry32(adj["seed"] + ci)
    Y, P, C, W = [0.0] * n, [0.0] * n, [0.0] * n, [0] * n
    for i in range(n):
        w = i % n_w
        season = yd["weather_seasons"][w]
        e = yd["rel_errors"][math.floor(rand() * len(yd["rel_errors"]))]
        u2, u3 = rand(), rand()
        matches = [j for j, s in enumerate(pr["error_seasons"]) if s == season]
        r = (pr["log_errors"][matches[math.floor(u2 * len(matches))]] if matches
             else pr["log_errors"][math.floor(u2 * len(pr["log_errors"]))])
        Y[i] = yd["q_per_acre"][w] * (1 + e) * m
        P[i] = phat * math.exp(r)
        C[i] = base_cost * (1 + band[0] + u3 * (band[1] - band[0]))
        W[i] = season

    wx = data["weather"][unit]
    jas = dict(zip(wx["seasons"], wx["jas_rain_mm"]))
    dry_cut = percentile(sorted(wx["jas_rain_mm"]), 100 / 3)
    med_y = percentile(sorted(Y), 50)
    if profile.get("water") == "protective":   # task 3.13
        for i in range(n):
            if jas[W[i]] <= dry_cut and Y[i] < med_y:
                Y[i] += adj["protective_irrigation_alpha"] * (med_y - Y[i])
        med_y = percentile(sorted(Y), 50)
    NR = [Y[i] * P[i] - C[i] for i in range(n)]

    dry_y = [Y[i] for i in range(n) if jas[W[i]] <= dry_cut]
    nr_sorted = sorted(NR)
    low_cut, high_cut = percentile(nr_sorted, 10), percentile(nr_sorted, 90)
    med_p = percentile(sorted(P), 50)
    out["yield_q"] = pcts(Y)
    out["price"] = {**pcts(P), "forecast": phat, "overridden": bool(price_override)}
    out["cost"] = {"base": base_cost, "low": base_cost * (1 + band[0]), "high": base_cost * (1 + band[1]),
                   "overridden": bool(own_cost)}
    out["net_acre"] = pcts(NR)
    out["loss_chance"] = sum(1 for x in NR if x < 0) / n
    out["break_even_price"] = base_cost / med_y
    out["break_even_yield"] = base_cost / med_p
    out["dry_sensitivity"] = percentile(sorted(dry_y), 50) / med_y - 1
    out["analog_low"] = top_seasons([W[i] for i in range(n) if NR[i] <= low_cut])
    out["analog_high"] = top_seasons([W[i] for i in range(n) if NR[i] >= high_cut])
    bt = data["backtest"].get(key)
    out["confidence"] = bt["confidence"] if bt else "Low"
    out["_nr"] = NR
    return out


def score(net_acre, lam):
    """Task 3.22: (1 - lambda) x base + lambda x low, per acre."""
    return (1 - lam) * net_acre["p50"] + lam * net_acre["p10"]


def rank_crops(eligible, ranking):
    """Tasks 3.22-3.23: same rules and insertion sort as engine.js rankCrops."""
    top = max([abs(c["score"]) for c in eligible], default=0)
    band = ranking["tie_band"] * top

    def before(a, b):
        if abs(a["score"] - b["score"]) <= band:
            if a["loss_chance"] != b["loss_chance"]:
                return a["loss_chance"] < b["loss_chance"]
            if a["confidence"] != b["confidence"]:
                return CONF_RANK[a["confidence"]] > CONF_RANK[b["confidence"]]
        return a["score"] > b["score"]

    ranked = []
    for c in eligible:
        k = len(ranked)
        while k > 0 and before(c, ranked[k - 1]):
            k -= 1
        ranked.insert(k, c)
    for k, c in enumerate(ranked):
        c["rank"], c["close_call"] = k + 1, False
    if len(ranked) >= 2 and abs(ranked[0]["win_rate"] - ranked[1]["win_rate"]) * 100 < ranking["close_call_pp"]:
        ranked[0]["close_call"] = ranked[1]["close_call"] = True
    return ranked


def run(data, profile):
    """Tasks 3.18-3.24: all crops, win rate, ranking, close calls, flags and notices."""
    unit, rules = unit_of(data, profile["district"]), data["rules"]
    area = float(profile.get("acres") or 0) + float(profile.get("guntas") or 0) / 40
    lam = rules["ranking"]["lambda"][profile.get("risk") or "balanced"]
    notices = []
    crops = [simulate_crop(data, profile, unit, c, ci) for ci, c in enumerate(CROPS)]
    eligible = [c for c in crops if c["eligible"]]
    force_low = profile.get("water") == "assured" or (profile.get("soil") == "unknown" and profile.get("drainage") == "unknown")
    if profile.get("water") == "assured":
        notices.append("The models describe rainfed farming. With assured irrigation, every result here has low confidence.")
    n = rules["adjustments"]["n_draws"]
    wins = [0] * len(eligible)
    for i in range(n):
        best, best_v = -1, -math.inf
        for k, c in enumerate(eligible):
            if c["_nr"][i] > best_v:
                best_v, best = c["_nr"][i], k
        if best >= 0:
            wins[best] += 1
    for k, c in enumerate(eligible):
        c["win_rate"] = wins[k] / n
        c["net_field"] = {p: c["net_acre"][p] * area for p in ("p10", "p50", "p90")}
        c["score"] = score(c["net_acre"], lam)
        if force_low:
            c["confidence"] = "Low"
        if profile.get("previous_crop") == c["crop"]:
            c["flags"].append("Cotton after cotton: stronger pest and disease carry-over risk"
                              if c["crop"] == "cotton" else "Same crop as last Kharif: pest and disease carry-over risk")
        if c["crop"] in rules["flags"]["occupies_rabi"]:
            c["flags"].append("Holds the field into winter: little room for a Rabi crop")
        del c["_nr"]
    ranked = rank_crops(eligible, rules["ranking"])
    return {"unit": unit, "area_acres": area, "lambda": lam, "risk": profile.get("risk") or "balanced",
            "notices": notices, "ranked": ranked, "excluded": [c for c in crops if not c["eligible"]]}
