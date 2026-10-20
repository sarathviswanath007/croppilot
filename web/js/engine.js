/* CropPilot engine (tasks 3.07-3.24, 3.33). JavaScript port of scripts/p3_engine.py; the two
 * must agree within 1% on percentiles and exactly on ranks (task 3.35, AC-06).
 *
 * PRD section 6, per crop:
 *   eligibility -> suitability tier and multiplier m (or farmer calibration r, clipped)
 *   draw i: weather season w = i mod nW;  Y = yhat(T, w) x (1 + e) x m
 *           protective irrigation: draws in the driest third of Jul-Sep seasons that are below
 *           the median move alpha of the way toward it [Assumption: only draws below the median]
 *           P = Phat x exp(r), r paired with season w when that season has a price error
 *           C = base cost x (1 + u), u uniform in the cost band
 *   NR = Y x P - C; P10/P50/P90; chance of loss; win rate (draws aligned by index);
 *   break-even price = C / median Y, break-even yield = C / median P;
 *   score = (1 - lambda) x P50 + lambda x P10, tie-break and close-call rules from rules.ranking.
 * Every draw uses exactly three PRNG calls (model error, price error, cost), in that order.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.CropEngine = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  var CROPS = ["tur", "maize", "soybean", "cotton"];
  var CONF_RANK = { High: 3, Medium: 2, Low: 1 };
  var SOIL_ROW = { deep_black: "deep_black_drains_well", medium_black: "medium_black_drains_well",
                   shallow_black: "shallow_black", red: "red", unknown: "mixed_or_unknown" };

  function mulberry32(a) {
    return function () {
      a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function percentile(sorted, p) {   // linear interpolation, as numpy's default
    var pos = (p / 100) * (sorted.length - 1), lo = Math.floor(pos), hi = Math.ceil(pos);
    return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo);
  }
  function sortedCopy(xs) { return xs.slice().sort(function (a, b) { return a - b; }); }
  function pcts(xs) { var s = sortedCopy(xs); return { p10: percentile(s, 10), p50: percentile(s, 50), p90: percentile(s, 90) }; }
  function clip(x, lo, hi) { return Math.min(hi, Math.max(lo, x)); }

  function unitOf(data, district) {
    for (var u in data.units) if (data.units[u].indexOf(district) >= 0) return u;
    throw new Error("unknown district " + district);
  }

  function conditionKey(p) {
    return p.drainage === "waterlogs" ? "waterlogs" : SOIL_ROW[p.soil || "unknown"];
  }

  function topSeasons(seasons) {   // the three most frequent seasons, ties by earlier year
    var count = {};
    seasons.forEach(function (s) { count[s] = (count[s] || 0) + 1; });
    return Object.keys(count).map(Number)
      .sort(function (a, b) { return count[b] - count[a] || a - b; }).slice(0, 3);
  }

  function simulateCrop(data, profile, unit, crop, ci) {
    var rules = data.rules, adj = rules.adjustments, key = unit + "|" + crop;
    var out = { crop: crop, name: data.crops[crop].name, flags: [], eligible: true };
    var suff = data.sufficiency[key];
    if (!suff || !suff.passes || !data.yield_draws[key] || !data.price[key]) {
      out.eligible = false;
      out.excluded_reason = "Not enough local data: " + (suff ? suff.seasons_ok : 0) +
        " seasons with at least " + rules.exclusions.min_area_ha + " ha (needs " + rules.exclusions.min_seasons + ")";
      return out;
    }
    if (profile.late_sowing && rules.exclusions.late_sowing_excluded.indexOf(crop) >= 0) {
      out.eligible = false;
      out.excluded_reason = "Late sowing (after mid-July) is outside the usual window for " + data.crops[crop].name;
      return out;
    }
    var tier = rules.suitability[conditionKey(profile)][crop];
    out.tier = tier;
    if (tier === "Not suitable") {
      out.eligible = false;
      out.excluded_reason = "Not suitable for this soil and drainage";
      return out;
    }
    var yd = data.yield_draws[key], pr = data.price[key], cost = data.costs[crop];
    var m = rules.multipliers[tier];
    out.multiplier = m;
    var own = profile.own_yield && profile.own_yield[crop];
    if (own) {
      m = clip(own / yd.five_season_mean_q_per_acre, adj.calibration_clip[0], adj.calibration_clip[1]);
      out.calibrated = true;
      out.multiplier = m;
    }
    var priceOverride = profile.price_override && profile.price_override[crop];
    var phat = priceOverride || pr.forecast;
    var ownCost = profile.own_cost && profile.own_cost[crop];
    var baseCost = ownCost || cost.a2fl_per_acre;
    var band = ownCost ? adj.override_band : adj.cost_band;

    var n = adj.n_draws, nW = yd.weather_seasons.length;
    var rand = mulberry32(adj.seed + ci);
    var Y = new Array(n), P = new Array(n), C = new Array(n), W = new Array(n);
    for (var i = 0; i < n; i++) {
      var w = i % nW, season = yd.weather_seasons[w];
      var e = yd.rel_errors[Math.floor(rand() * yd.rel_errors.length)];
      var u2 = rand(), u3 = rand();
      var matches = [];
      for (var j = 0; j < pr.error_seasons.length; j++) if (pr.error_seasons[j] === season) matches.push(j);
      var r = matches.length ? pr.log_errors[matches[Math.floor(u2 * matches.length)]]
                             : pr.log_errors[Math.floor(u2 * pr.log_errors.length)];
      Y[i] = yd.q_per_acre[w] * (1 + e) * m;
      P[i] = phat * Math.exp(r);
      C[i] = baseCost * (1 + band[0] + u3 * (band[1] - band[0]));
      W[i] = season;
    }

    var wx = data.weather[unit], jas = {};
    wx.seasons.forEach(function (s, k) { jas[s] = wx.jas_rain_mm[k]; });
    var dryCut = percentile(sortedCopy(wx.jas_rain_mm), 100 / 3);
    var medY = percentile(sortedCopy(Y), 50);
    if (profile.water === "protective") {
      for (i = 0; i < n; i++)
        if (jas[W[i]] <= dryCut && Y[i] < medY) Y[i] += adj.protective_irrigation_alpha * (medY - Y[i]);
      medY = percentile(sortedCopy(Y), 50);
    }
    var NR = new Array(n);
    for (i = 0; i < n; i++) NR[i] = Y[i] * P[i] - C[i];

    var dryY = [];
    for (i = 0; i < n; i++) if (jas[W[i]] <= dryCut) dryY.push(Y[i]);
    var nrSorted = sortedCopy(NR), lowCut = percentile(nrSorted, 10), highCut = percentile(nrSorted, 90);
    var lowS = [], highS = [], losses = 0;
    for (i = 0; i < n; i++) {
      if (NR[i] <= lowCut) lowS.push(W[i]);
      if (NR[i] >= highCut) highS.push(W[i]);
      if (NR[i] < 0) losses++;
    }
    var medP = percentile(sortedCopy(P), 50);
    out.yield_q = pcts(Y);
    out.price = pcts(P);
    out.price.forecast = phat;
    out.price.overridden = !!priceOverride;
    out.cost = { base: baseCost, low: baseCost * (1 + band[0]), high: baseCost * (1 + band[1]), overridden: !!ownCost };
    out.net_acre = pcts(NR);
    out.loss_chance = losses / n;
    out.break_even_price = baseCost / medY;
    out.break_even_yield = baseCost / medP;
    out.dry_sensitivity = percentile(sortedCopy(dryY), 50) / medY - 1;
    out.analog_low = topSeasons(lowS);
    out.analog_high = topSeasons(highS);
    var bt = data.backtest[key];
    out.confidence = bt ? bt.confidence : "Low";
    out._nr = NR;
    return out;
  }

  function score(netAcre, lambda) { return (1 - lambda) * netAcre.p50 + lambda * netAcre.p10; }

  /* Task 3.22-3.23: sort by score; within tie_band x |top score|, lower chance of loss, then higher
   * confidence ranks first. Insertion sort so Python gives the identical order. */
  function rankCrops(eligible, ranking) {
    var top = eligible.reduce(function (a, c) { return Math.max(a, Math.abs(c.score)); }, 0);
    var band = ranking.tie_band * top;
    function before(a, b) {
      if (Math.abs(a.score - b.score) <= band) {
        if (a.loss_chance !== b.loss_chance) return a.loss_chance < b.loss_chance;
        if (a.confidence !== b.confidence) return CONF_RANK[a.confidence] > CONF_RANK[b.confidence];
      }
      return a.score > b.score;
    }
    var ranked = [];
    eligible.forEach(function (c) {
      var k = ranked.length;
      while (k > 0 && before(c, ranked[k - 1])) k--;
      ranked.splice(k, 0, c);
    });
    ranked.forEach(function (c, k) { c.rank = k + 1; c.close_call = false; });
    if (ranked.length >= 2 && Math.abs(ranked[0].win_rate - ranked[1].win_rate) * 100 < ranking.close_call_pp)
      ranked[0].close_call = ranked[1].close_call = true;
    return ranked;
  }

  function run(data, profile) {
    var unit = unitOf(data, profile.district), rules = data.rules;
    var area = (Number(profile.acres) || 0) + (Number(profile.guntas) || 0) / 40;
    var lambda = rules.ranking.lambda[profile.risk || "balanced"];
    var notices = [];
    var crops = CROPS.map(function (c, ci) { return simulateCrop(data, profile, unit, c, ci); });
    var eligible = crops.filter(function (c) { return c.eligible; });
    var forceLow = profile.water === "assured" || (profile.soil === "unknown" && profile.drainage === "unknown");
    if (profile.water === "assured")
      notices.push("The models describe rainfed farming. With assured irrigation, every result here has low confidence.");
    var n = rules.adjustments.n_draws, wins = eligible.map(function () { return 0; });
    for (var i = 0; i < n; i++) {
      var best = -1, bestV = -Infinity;
      eligible.forEach(function (c, k) { if (c._nr[i] > bestV) { bestV = c._nr[i]; best = k; } });
      if (best >= 0) wins[best]++;
    }
    eligible.forEach(function (c, k) {
      c.win_rate = wins[k] / n;
      c.net_field = { p10: c.net_acre.p10 * area, p50: c.net_acre.p50 * area, p90: c.net_acre.p90 * area };
      c.score = score(c.net_acre, lambda);
      if (forceLow) c.confidence = "Low";
      if (profile.previous_crop === c.crop)
        c.flags.push(c.crop === "cotton"
          ? "Cotton after cotton: stronger pest and disease carry-over risk"
          : "Same crop as last Kharif: pest and disease carry-over risk");
      if (rules.flags.occupies_rabi.indexOf(c.crop) >= 0)
        c.flags.push("Holds the field into winter: little room for a Rabi crop");
      delete c._nr;
    });
    var ranked = rankCrops(eligible, rules.ranking);
    return {
      unit: unit, area_acres: area, lambda: lambda, risk: profile.risk || "balanced", notices: notices,
      ranked: ranked, excluded: crops.filter(function (c) { return !c.eligible; }),
    };
  }

  return { run: run, score: score, rankCrops: rankCrops, mulberry32: mulberry32, percentile: percentile, CROPS: CROPS };
});
