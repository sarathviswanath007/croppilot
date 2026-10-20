/* CropPilot web app (Phase 5, decisions D-22, D-24, D-25). Loads data/engine_data.json, asks three
 * short questions, runs the engine (js/engine.js) in the browser and shows one clear answer.
 * All on-screen text comes from js/i18n.js (English / Kannada). No data leaves the page; no AI calls.
 * Labels (FR-14): one tag per block of numbers, plus a tag on any number whose kind differs.
 */
"use strict";
(function () {
  const E = window.CropEngine;
  const app = document.getElementById("app");
  const DISTRICTS = ["Kalaburagi", "Yadgir", "Bidar", "Raichur", "Koppal", "Ballari", "Vijayanagara"];
  const ICON = {
    tur: `<svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="31" fill="#e8f2df"/><path d="M12 46C18 24 38 13 53 16c-5 18-23 31-41 30z" fill="#86b25a" stroke="#4f7a2c" stroke-width="2"/><circle cx="23" cy="39" r="4.2" fill="#8a5a2b"/><circle cx="32" cy="32" r="4.2" fill="#8a5a2b"/><circle cx="41" cy="25" r="4.2" fill="#8a5a2b"/></svg>`,
    maize: `<svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="31" fill="#fdf0cf"/><path d="M32 56c-10-6-14-18-12-30 4 8 8 14 12 30z" fill="#6aa04a"/><path d="M32 56c10-6 14-18 12-30-4 8-8 14-12 30z" fill="#7fb85a"/><ellipse cx="32" cy="27" rx="8.5" ry="18" fill="#f2b632" stroke="#c98a12" stroke-width="2"/><g fill="#e09a14"><circle cx="29" cy="16" r="1.6"/><circle cx="35" cy="16" r="1.6"/><circle cx="29" cy="22" r="1.6"/><circle cx="35" cy="22" r="1.6"/><circle cx="29" cy="28" r="1.6"/><circle cx="35" cy="28" r="1.6"/><circle cx="29" cy="34" r="1.6"/><circle cx="35" cy="34" r="1.6"/></g></svg>`,
    soybean: `<svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="31" fill="#f4ecd9"/><path d="M14 40c2-10 10-18 22-22 8-3 14 0 14 4-2 10-12 19-26 22-6 1-10-1-10-4z" fill="#c9a865" stroke="#8f7238" stroke-width="2"/><circle cx="24" cy="36" r="5" fill="#e3c98a"/><circle cx="32" cy="30" r="5" fill="#e3c98a"/><circle cx="40" cy="24" r="5" fill="#e3c98a"/></svg>`,
    cotton: `<svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="31" fill="#eef1f4"/><path d="M32 58V44" stroke="#7a5230" stroke-width="3"/><path d="M18 44c6 4 22 4 28 0l-4 6H22z" fill="#7a5230"/><g fill="#ffffff" stroke="#b9c0c8" stroke-width="2"><circle cx="24" cy="32" r="9"/><circle cx="40" cy="32" r="9"/><circle cx="32" cy="22" r="10"/><circle cx="32" cy="36" r="8"/></g></svg>`,
    logo: `<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="15" fill="#2f7a4f"/><path d="M16 25V13" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/><path d="M16 15c0-5 4-8 8-8 0 5-4 8-8 8zM16 18c0-4-3-7-7-7 0 4 3 7 7 7z" fill="#f2b632"/></svg>`,
    rain: `<svg viewBox="0 0 40 40"><path d="M11 22a7 7 0 0 1 1-14 9 9 0 0 1 17 3 6 6 0 0 1 0 11z" fill="#b8c7d6"/><path d="M14 27l-2 5M21 27l-2 5M28 27l-2 5" stroke="#3b7dc4" stroke-width="2.4" stroke-linecap="round"/></svg>`,
    drop: `<svg viewBox="0 0 40 40"><path d="M20 5c6 9 11 14 11 20a11 11 0 0 1-22 0c0-6 5-11 11-20z" fill="#3b7dc4"/><path d="M20 19v10M15 24h10" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/></svg>`,
    canal: `<svg viewBox="0 0 40 40"><path d="M4 14c4-3 8-3 12 0s8 3 12 0 8-3 8-3M4 22c4-3 8-3 12 0s8 3 12 0 8-3 8-3M4 30c4-3 8-3 12 0s8 3 12 0 8-3 8-3" fill="none" stroke="#3b7dc4" stroke-width="3" stroke-linecap="round"/></svg>`,
    risk1: `<svg viewBox="0 0 40 40"><rect x="7" y="24" width="7" height="10" rx="2" fill="#2f7a4f"/><rect x="17" y="16" width="7" height="18" rx="2" fill="#e3dccb"/><rect x="27" y="8" width="7" height="26" rx="2" fill="#e3dccb"/></svg>`,
    risk2: `<svg viewBox="0 0 40 40"><rect x="7" y="24" width="7" height="10" rx="2" fill="#f2b632"/><rect x="17" y="16" width="7" height="18" rx="2" fill="#f2b632"/><rect x="27" y="8" width="7" height="26" rx="2" fill="#e3dccb"/></svg>`,
    risk3: `<svg viewBox="0 0 40 40"><rect x="7" y="24" width="7" height="10" rx="2" fill="#d9772b"/><rect x="17" y="16" width="7" height="18" rx="2" fill="#d9772b"/><rect x="27" y="8" width="7" height="26" rx="2" fill="#d9772b"/></svg>`,
  };
  const swatch = (bg) => `<span class="swatch" style="background:${bg}"></span>`;
  const SOIL_SWATCH = {
    deep_black: swatch("#2b2724"), medium_black: swatch("#4d443b"),
    shallow_black: swatch("repeating-radial-gradient(circle at 30% 30%, #6e6152 0 3px, #8d8070 3px 6px)"),
    red: swatch("#a5502e"), unknown: swatch("conic-gradient(#2b2724 0 25%, #a5502e 0 50%, #4d443b 0 75%, #c9a865 0)"),
  };
  const WATER_ICON = { rainfed: ICON.rain, protective: ICON.drop, "assured": ICON.canal };
  const RISK_ICON = { cautious: ICON.risk1, balanced: ICON.risk2, growth: ICON.risk3 };
  const ENGINE_FLAGS = [["Cotton after cotton", "flag.cotton"], ["Same crop as last Kharif", "flag.same"], ["Holds the field into winter", "flag.rabi"]];

  let DATA = null;
  let lang = "en";
  try { lang = localStorage.getItem("croppilot.lang") === "kn" ? "kn" : "en"; } catch (err) { /* storage unavailable */ }
  const state = {
    view: "welcome", step: 1,
    district: null, acres: 2, guntas: 0, soil: null, drainage: null, water: null,
    previous_crop: null, risk: null, late_sowing: false,
    own_yield: {}, own_cost: {}, price_override: {},
    open: null, chosen: null, reason: "",
  };

  /* ---------- text and number helpers ---------- */
  function t(key, vars) {
    const s = (window.I18N[lang][key] ?? window.I18N.en[key] ?? key);
    return typeof s === "string" ? s.replace(/\{(\w+)\}/g, (m, k) => (vars && k in vars ? vars[k] : m)) : s;
  }
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const tx = (key, vars) => esc(t(key, vars));
  const inr = (x) => { const r = Math.round(x); return (r < 0 ? "−₹" : "₹") + Math.abs(r).toLocaleString("en-IN"); };
  const fmt = (x, d = 1) => Number(x).toLocaleString("en-IN", { minimumFractionDigits: d, maximumFractionDigits: d });
  const n100 = (x) => Math.round(x * 100);
  const pct = (x) => Math.round(x * 100) + "%";
  const tag = (k) => `<span class="tag ${k}">${tx("tag." + k)}</span>`;
  const acresText = (a) => t(a === 1 ? "acre.one" : "acre.many", { n: Number.isInteger(a) ? String(a) : fmt(a, 2) });
  const area = () => (Number(state.acres) || 0) + (Number(state.guntas) || 0) / 40;
  const unitKey = (unit, crop) => unit + "|" + crop;
  const cropName = (c) => t("crop." + c);
  const cropFull = (c) => t("cropFull." + c);
  const dist = (d) => t("dist." + d);
  const MONTHS_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const month = (m) => t("month")[MONTHS_EN.indexOf(m)] || m;
  const monthYear = (s) => s.replace(/^([A-Z][a-z]{2}) (\d{4})$/, (x, m, y) => month(m) + " " + y);
  const modelName = (s) => t("m." + s);
  function flagText(f) {
    const hit = ENGINE_FLAGS.find(([prefix]) => f.startsWith(prefix));
    return hit ? t(hit[1]) : f;
  }
  function excludedText(c) {
    const r = c.excluded_reason;
    if (r.startsWith("Not enough local data")) return t("ex.data", { n: (r.match(/(\d+) seasons/) || [, "0"])[1] });
    if (r.startsWith("Late sowing")) return t("ex.late");
    if (r.startsWith("Not suitable")) return t("ex.soil");
    return r;
  }

  function choiceGrid(key, options, wide) {
    return `<div class="choices${wide ? " wide" : ""}" role="group">` + options.map(([v, label, sub, icon]) =>
      `<button type="button" class="choice" data-key="${key}" data-v="${v}" aria-pressed="${state[key] === v}">
        ${icon ? `<span class="ico">${icon}</span>` : ""}<span class="txt"><b>${esc(label)}</b>${sub ? `<span class="sub">${esc(sub)}</span>` : ""}</span></button>`).join("") + `</div>`;
  }

  /* ---------- views ---------- */
  function welcome() {
    const tiles = E.CROPS.map((c) => `<div class="crop-tile">${ICON[c]}<b>${esc(cropName(c))}</b>${lang === "en" ? `<span class="kn" lang="kn">${esc(window.I18N.kn["crop." + c])}</span>` : ""}</div>`).join("");
    return `<section class="hero">
      <h1>${tx("w.h1")}</h1>
      <p class="lead">${tx("w.lead")}</p>
      <div class="crop-row">${tiles}</div>
      <div class="how">
        <div><span class="n">1</span><b>${tx("w.how1")}</b><span>${tx("w.how1s")}</span></div>
        <div><span class="n">2</span><b>${tx("w.how2")}</b><span>${tx("w.how2s")}</span></div>
        <div><span class="n">3</span><b>${tx("w.how3")}</b><span>${tx("w.how3s")}</span></div>
      </div>
      <button class="btn primary btn-big" id="start">${tx("w.start")}</button>
      <div class="trust"><span>${tx("w.trust1")}</span><span>${tx("w.trust2")}</span><span>${tx("w.trust3")}</span></div>
    </section>`;
  }

  function stepView() {
    const s = state.step;
    const progress = `<div class="progress" aria-hidden="true">${[1, 2, 3].map((i) => `<span class="${i <= s ? "on" : ""}"></span>`).join("")}</div>
      <span class="step-label">${tx("s.question", { n: s })}</span>`;
    let body = "", ready = false;
    if (s === 1) {
      body = `<h2>${tx("s1.h")}</h2>
        <div class="q"><div class="title">${tx("s1.district")}</div>${choiceGrid("district", DISTRICTS.map((d) => [d, dist(d)]))}</div>
        <div class="q"><div class="title">${tx("s1.size")}</div><div class="hint">${tx("s1.hint")}</div>
          <div class="size">${stepper("acres", t("s1.acres"), 0, 500)}${stepper("guntas", t("s1.guntas"), 0, 39)}</div>
          <span class="area-say">${tx("s1.thatIs", { a: acresText(area()) })}</span></div>`;
      ready = state.district && area() > 0;
    } else if (s === 2) {
      const soils = ["deep_black", "medium_black", "shallow_black", "red", "unknown"].map((k) => [k, t("soil." + k), t("soil." + k + ".s"), SOIL_SWATCH[k]]);
      const drains = ["drains_well", "waterlogs", "unknown"].map((k) => [k, t("drain." + k), k === "unknown" ? "" : t("drain." + k + ".s")]);
      const waters = ["rainfed", "protective", "assured"].map((k) => [k, t("water." + k), t("water." + k + ".s"), WATER_ICON[k]]);
      body = `<h2>${tx("s2.h")}</h2>
        <div class="q"><div class="title">${tx("s2.soil")}</div>${choiceGrid("soil", soils, true)}</div>
        <div class="q"><div class="title">${tx("s2.drain")}</div>${choiceGrid("drainage", drains)}</div>
        <div class="q"><div class="title">${tx("s2.water")}</div>${choiceGrid("water", waters, true)}</div>`;
      ready = state.soil && state.drainage && state.water;
    } else {
      const prev = [["none", t("prev.none")], ...E.CROPS.map((c) => [c, cropName(c)]), ["other", t("prev.other")]];
      const risks = ["cautious", "balanced", "growth"].map((k) => [k, t("risk." + k), t("risk." + k + ".s"), RISK_ICON[k]]);
      body = `<h2>${tx("s3.h")}</h2>
        <div class="q"><div class="title">${tx("s3.prev")}</div>${choiceGrid("previous_crop", prev)}</div>
        <div class="q"><div class="title">${tx("s3.risk")}</div>${choiceGrid("risk", risks, true)}</div>
        <div class="q"><div class="title">${tx("s3.late")}</div>
          <div class="choices" role="group">
            <button type="button" class="choice" data-late="0" aria-pressed="${!state.late_sowing}"><b>${tx("s3.lateNo")}</b></button>
            <button type="button" class="choice" data-late="1" aria-pressed="${state.late_sowing}"><b>${tx("s3.lateYes")}</b></button>
          </div></div>`;
      ready = state.previous_crop && state.risk;
    }
    return `${progress}${body}
      <div class="nav"><button class="btn" id="back">${tx("s.back")}</button>
        <button class="btn primary" id="next" ${ready ? "" : "disabled"}>${tx(s === 3 ? "s.show" : "s.next")}</button></div>`;
  }

  function stepper(key, label, min, max) {
    return `<div class="stepper"><button type="button" data-step="${key}" data-d="-1" aria-label="${esc(t("s1.fewer", { u: label }))}">−</button>
      <input id="in-${key}" type="number" inputmode="numeric" min="${min}" max="${max}" value="${state[key]}" aria-label="${esc(label)}">
      <label for="in-${key}">${esc(label)}</label>
      <button type="button" data-step="${key}" data-d="1" aria-label="${esc(t("s1.more", { u: label }))}">+</button></div>`;
  }

  /* ---------- results ---------- */
  function reasons(c, ranked) {
    const out = [];
    if (ranked.length === 1) return [t("why.only")];
    const best = (f) => ranked.every((o) => f(c) >= f(o));
    if (best((o) => o.net_acre.p50)) out.push(t("why.typ"));
    if (best((o) => o.net_acre.p10)) out.push(t("why.bad"));
    if (best((o) => -o.loss_chance)) out.push(t("why.loss", { n: n100(c.loss_chance) }));
    if (best((o) => o.win_rate)) out.push(t("why.wins", { n: n100(c.win_rate) }));
    if (best((o) => -o.cost.base)) out.push(t("why.cost"));
    if (!out.length) {
      const top = ranked[0];
      out.push(t("why.topHigher", { crop: cropName(top.crop) }));
      if (c.loss_chance > top.loss_chance) out.push(t("why.higherLoss", { crop: cropName(top.crop), a: n100(c.loss_chance), b: n100(top.loss_chance) }));
    }
    return out.slice(0, 3);
  }

  function confidenceLine(c) {
    if (state.water === "assured") return t("c.assured");
    if (state.soil === "unknown" && state.drainage === "unknown") return t("c.unknown");
    const m = DATA.models[c.crop];
    return (m.yield_is_ml ? t("c.ml", { p: pct(m.yield_skill) }) : t("c.b1")) + " " + t("c.cov", { p: pct(m.yield_coverage) });
  }

  function drivers(crop, unit) {
    const d = DATA.drivers[crop];
    if (!d || !d.drivers) return [t("d.b1", { y: DATA.yield_draws[unitKey(unit, crop)].data_through })];
    return d.drivers.slice(0, 3).map((x) => t("d.driver", {
      f: t("f." + x.feature), dir: t(x.effect_p25_to_p75_kg_ha >= 0 ? "d.raises" : "d.lowers"), n: Math.abs(Math.round(x.effect_p25_to_p75_kg_ha)),
    }));
  }

  function detail(c, unit) {
    const pr = DATA.price[unitKey(unit, c.crop)], msp = DATA.msp[c.crop], cost = DATA.costs[c.crop], m = DATA.models[c.crop];
    const win = DATA.crops[c.crop].harvest_window;
    const priceSrc = c.price.overridden ? `${tx("a.yourPrice")} ${tag("you")}` :
      esc(t("a.priceSrc", { plain: t("pp." + pr.model), d: monthYear(pr.data_through) }) + (pr.borrowed_from_units ? t("a.borrowed") : ""));
    const tierLine = c.calibrated ? `${tx("a.calibrated")} ${tag("you")}`
      : esc(t("a.tier", { t: t("tier." + c.tier) }) + (c.multiplier < 1 ? t("a.reduced", { p: pct(1 - c.multiplier) }) : "") + ".");
    return `<div class="detail">
      <div><h4>${tx("d.perAcre")} ${tag("pred")}</h4><dl class="kv num">
        <dt>${tx("d.yield")}</dt><dd>${tx("d.yieldV", { lo: fmt(c.yield_q.p10), hi: fmt(c.yield_q.p90), mid: fmt(c.yield_q.p50), k: c.crop === "cotton" ? t("d.kapas") : "" })}</dd>
        <dt>${tx("d.price")}</dt><dd>${tx("d.priceV", { lo: inr(c.price.p10), hi: inr(c.price.p90), mid: inr(c.price.p50) })}</dd>
        <dt>${tx("d.cost")}</dt><dd>${inr(c.cost.base)} ${c.cost.overridden ? tag("you") : tag("assum")}</dd>
        <dt>${tx("d.breakeven")}</dt><dd>${tx("d.breakevenV", { p: inr(c.break_even_price), y: fmt(c.break_even_yield, 2) })}</dd>
        <dt>${tx("d.msp", { s: msp.season })}</dt><dd>${tx("d.mspV", { v: inr(msp.value) })} ${tag("data")} <span class="muted">${tx("d.mspNote")}</span></dd>
      </dl></div>
      <div><h4>${tx("d.drivers")} ${tag("pred")}</h4><ul>${drivers(c.crop, unit).map((s) => `<li>${esc(s)}</li>`).join("")}</ul></div>
      <div><h4>${tx("d.analog")} ${tag("data")}</h4><p class="small">${tx("d.analogV", { lo: c.analog_low.join(", "), hi: c.analog_high.join(", ") })}</p></div>
      <div><h4>${tx("d.risks")}</h4><ul>
        ${m.yield_is_ml ? `<li>${tx("d.dry", { p: pct(Math.abs(c.dry_sensitivity)), dir: t(c.dry_sensitivity <= 0 ? "d.lower" : "d.higher") })} ${tag("pred")}</li>` : `<li>${tx("d.noDry")}</li>`}
        ${pr.harvest_window_cv != null ? `<li>${tx("d.cv", { p: pct(pr.harvest_window_cv) })} ${tag("data")}</li>` : ""}
        ${c.flags.map((f) => `<li>${esc(flagText(f))}</li>`).join("")}
        <li>${tx("d.pest")}</li></ul></div>
      <div><h4>${tx("d.reliable")} ${tag("pred")}</h4><p class="small"><span class="pill ${c.confidence}">${tx("conf." + c.confidence)}</span> ${esc(confidenceLine(c))}</p></div>
      <div><h4>${tx("d.assumptions")} ${tag("assum")}</h4><ul class="small">
        <li>${tierLine}</li>
        <li>${t("a.price", { src: priceSrc })}</li>
        <li>${tx("a.sold", { m1: month(win[0]), m2: month(win[win.length - 1]) })}</li>
        <li>${tx("a.cost", { y: cost.cost_year })}</li>
        ${c.crop === "cotton" ? `<li>${tx("a.ginning")}</li>` : ""}
        ${state.water === "protective" ? `<li>${tx("a.protective")}</li>` : ""}
      </ul></div>
    </div>`;
  }

  function results() {
    let res;
    try { res = E.run(DATA, state); } catch (err) { return `<div class="notice">${esc(err.message)}</div>`; }
    const ranked = res.ranked, unit = res.unit, a = res.area_acres;
    const html = [];
    const chips = [
      [1, `${dist(state.district)} · ${acresText(a)}`], [2, t("soil.chip", { s: t("soil." + state.soil) })],
      [2, t("water.chip." + state.water)], [3, t("risk." + state.risk)],
    ];
    html.push(`<div class="answers"><span class="small muted">${tx("r.answers")}</span>${tag("you")}${chips.map(([st, s]) => `<button type="button" data-goto="${st}" title="${tx("r.change")}">${esc(s)} ✎</button>`).join("")}</div>`);
    if (res.notices.length) html.push(`<div class="notice">${tx("notice.assured")}</div>`);
    if (!ranked.length) {
      html.push(`<div class="notice">${tx("r.none")}</div>`);
      return html.join("");
    }
    const top = ranked[0];
    const lo = Math.min(0, top.net_field.p10), hi = Math.max(1, top.net_field.p90);
    const x = (v) => ((v - lo) / (hi - lo)) * 100;
    const bar = (k, v, typ) => {
      const a0 = x(Math.min(0, v)), w = Math.abs(x(v) - x(0));
      return `<div class="bar-row"><span class="k">${tx(k)}<span>${tx(k + ".s")}</span></span>
        <span class="track"><span class="fill ${v < 0 ? "neg" : typ ? "typ" : "pos"}" style="left:${a0}%;width:${w}%"></span><span class="zero" style="left:${x(0)}%"></span></span>
        <span class="v ${v < 0 ? "neg" : ""}">${inr(v)}</span></div>`;
    };
    const typ = top.net_field.p50;
    const say = esc(t("r.say", { crop: lang === "en" ? cropName(top.crop).toLowerCase() : cropName(top.crop), a: acresText(a), v: "\u0000" })).replace("\u0000", `<b>${inr(typ)}</b>`);
    html.push(`<section class="answer">
      <div class="answer-head">${ICON[top.crop]}<div><span class="eyebrow">${tx("r.first")}</span>
        <h2>${esc(cropFull(top.crop))}${lang === "en" ? ` <span class="kn" lang="kn">${esc(window.I18N.kn["crop." + top.crop])}</span>` : ""}</h2></div></div>
      <p class="say">${say} ${tag("pred")}</p>
      <div class="bars">${bar("r.bad", top.net_field.p10)}${bar("r.typ", typ, true)}${bar("r.good", top.net_field.p90)}</div>
      <div class="facts"><span class="fact">${tx("r.loses", { n: "\u0000" }).replace("\u0000", `<b>${n100(top.loss_chance)}</b>`)}</span>
        <span class="fact">${tx("r.costs", { v: "\u0000" }).replace("\u0000", `<b>${inr(top.cost.base * a)}</b>`)}</span>
        <span class="pill ${top.confidence}">${tx("conf." + top.confidence)}</span>${top.close_call ? `<span class="pill close">${tx("r.close", { crop: cropName(ranked[1].crop) })}</span>` : ""}</div>
      <ul class="why">${reasons(top, ranked).map((r) => `<li>${esc(r)}</li>`).join("")}</ul>
      <div><button class="link" data-open="${top.crop}">${tx(state.open === top.crop ? "r.hideDetails" : "r.see")}</button></div>
      ${state.open === top.crop ? detail(top, unit) : ""}
    </section>`);

    if (ranked.length > 1) {
      const maxTyp = Math.max(...ranked.map((c) => Math.abs(c.net_field.p50)), 1);
      html.push(`<section class="others"><h3>${tx("r.others")}</h3><p class="small muted">${tx("r.othersSub")} ${tag("pred")}</p>`);
      ranked.slice(1).forEach((c) => {
        const open = state.open === c.crop, v = c.net_field.p50;
        const line = tx("r.otherLine", { bad: "\u0000", n: n100(c.loss_chance) }).replace("\u0000", `<span class="num ${c.net_field.p10 < 0 ? "neg" : ""}">${inr(c.net_field.p10)}</span>`);
        html.push(`<div class="other"><button class="other-head" data-open="${c.crop}" aria-expanded="${open}">
            ${ICON[c.crop]}<span class="nm"><span class="rk">${c.rank}.</span>${esc(cropFull(c.crop))}${lang === "en" ? ` <span class="kn" lang="kn">${esc(window.I18N.kn["crop." + c.crop])}</span>` : ""}</span><span class="chev">${tx(open ? "r.hide" : "r.details")}</span>
            <span class="line"><span class="mini"><span class="track"><span class="fill ${v < 0 ? "neg" : "pos"}" style="left:0;width:${(Math.abs(v) / maxTyp) * 100}%"></span></span>
              <b class="num ${v < 0 ? "neg" : ""}">${inr(v)}</b></span>${line}${c.close_call ? " · " + tx("r.closeShort") : ""}</span>
          </button>${open ? detail(c, unit) : ""}</div>`);
      });
      html.push(`</section>`);
    }
    if (res.excluded.length) {
      html.push(`<section class="excluded muted"><b>${tx("r.notCompared")}</b> ${tag("data")}<ul>${res.excluded.map((c) => `<li>${esc(cropFull(c.crop))}: ${esc(excludedText(c))}.</li>`).join("")}</ul></section>`);
    }

    html.push(`<section class="panel" id="choice"><h3>${tx("ch.h")} ${tag("pred")}</h3>
      <p class="small muted">${tx("ch.sub")}</p>
      <div class="row">${ranked.map((c) => `<button type="button" class="choice" style="flex:1;min-width:120px" data-choose="${c.crop}" aria-pressed="${state.chosen === c.crop}"><b>${esc(cropName(c.crop))}</b></button>`).join("")}</div>
      ${state.chosen ? `<div class="field"><label for="reason">${tx("ch.why")}</label><input id="reason" type="text" value="${esc(state.reason)}" placeholder="${tx("ch.ph")}"></div>
        <div class="summary" id="summary-text">${esc(summaryText(res))}</div>
        <div class="row"><button class="btn" id="copy">${tx("ch.copy")}</button><span class="small muted">${tx("ch.share")}</span></div>` : ""}
    </section>`);

    html.push(`<details class="panel" id="own-panel" ${Object.keys(state.own_yield).length + Object.keys(state.own_cost).length + Object.keys(state.price_override).length ? "open" : ""}>
      <summary>${tx("own.h")}</summary>
      <p class="small muted">${tx("own.sub")}</p>
      <div class="own"><span></span><span class="small muted">${tx("own.y")}</span><span class="small muted">${tx("own.p")}</span><span class="small muted">${tx("own.c")}</span>
        ${ranked.map((c) => `<span>${esc(cropName(c.crop))}</span>
          <input id="oy-${c.crop}" type="number" min="0" step="0.1" value="${state.own_yield[c.crop] || ""}" aria-label="${esc(cropName(c.crop))} · ${tx("own.y")}">
          <input id="op-${c.crop}" type="number" min="0" step="50" value="${state.price_override[c.crop] || ""}" aria-label="${esc(cropName(c.crop))} · ${tx("own.p")}">
          <input id="oc-${c.crop}" type="number" min="0" step="500" value="${state.own_cost[c.crop] || ""}" aria-label="${esc(cropName(c.crop))} · ${tx("own.c")}">`).join("")}
      </div></details>`);

    html.push(`<details class="panel"><summary>${tx("tab.h")}</summary><div class="tablewrap"><table>
      <thead><tr><th>${tx("tab.crop")}</th><th class="n">${tx("tab.bad")}</th><th class="n">${tx("tab.typ")}</th><th class="n">${tx("tab.good")}</th><th class="n">${tx("tab.loss")}</th><th class="n">${tx("tab.cost")}</th></tr></thead>
      <tbody>${ranked.map((c) => `<tr><td>${c.rank}. ${esc(cropName(c.crop))}</td><td class="n ${c.net_field.p10 < 0 ? "neg" : ""}">${inr(c.net_field.p10)}</td><td class="n">${inr(c.net_field.p50)}</td><td class="n">${inr(c.net_field.p90)}</td><td class="n">${pct(c.loss_chance)}</td><td class="n">${inr(c.cost.base * a)}</td></tr>`).join("")}</tbody>
    </table></div><p class="small muted">${tx("tab.note")} ${tag("pred")} · ${tx("tab.cost")} ${tag("assum")}</p></details>`);
    return html.join("");
  }

  function summaryText(res) {
    const c = res.ranked.find((x) => x.crop === state.chosen);
    if (!c) return "";
    const top = res.ranked[0];
    return [
      t("sum.1", { d: dist(state.district), a: acresText(res.area_acres) }),
      t("sum.2", { c: cropFull(c.crop), r: state.reason ? ` (${state.reason})` : "" }),
      t("sum.3", { b: inr(c.net_field.p10), t: inr(c.net_field.p50), g: inr(c.net_field.p90) }),
      t("sum.4", { n: n100(c.loss_chance), conf: t("conf." + c.confidence) }),
      c.crop === top.crop ? t("sum.same") : t("sum.other", { t: cropName(top.crop), r: c.rank }),
      t("sum.end"),
    ].join("\n");
  }

  function about() {
    const yrows = E.CROPS.map((c) => { const m = DATA.models[c]; return `<tr><td>${esc(cropFull(c))}</td><td>${esc(modelName(m.yield_model))}</td><td class="n">${m.yield_skill >= 0 ? "+" : ""}${fmt(m.yield_skill, 2)}</td><td class="n">${pct(m.yield_coverage)}</td><td class="n">${m.yield_n_rows}</td></tr>`; }).join("");
    const prows = E.CROPS.map((c) => { const m = DATA.models[c]; return `<tr><td>${esc(cropFull(c))}</td><td>${esc(modelName(m.price_model))}</td><td class="n">${pct(m.price_mape)}</td><td class="n">${pct(m.price_coverage)}</td><td class="n">${m.price_n_rows}</td></tr>`; }).join("");
    return `<section class="about">
      <div><button class="link" id="back-results">${tx("ab.back")}</button></div>
      <h2>${tx("ab.h")}</h2>
      <p>${tx("ab.p1", { n: fmt(DATA.rules.adjustments.n_draws, 0) })} ${tag("assum")}</p>
      <p>${tx("ab.p2")}</p>
      <div class="panel"><h3>${tx("ab.yield")} ${tag("pred")}</h3><div class="tablewrap"><table>
        <thead><tr><th>${tx("ab.crop")}</th><th>${tx("ab.method")}</th><th class="n">${tx("ab.gain")}</th><th class="n">${tx("ab.held")}</th><th class="n">${tx("ab.tests")}</th></tr></thead><tbody>${yrows}</tbody></table></div>
        <p class="small muted">${tx("ab.yieldNote")}</p></div>
      <div class="panel"><h3>${tx("ab.price")} ${tag("pred")}</h3><div class="tablewrap"><table>
        <thead><tr><th>${tx("ab.crop")}</th><th>${tx("ab.method")}</th><th class="n">${tx("ab.err")}</th><th class="n">${tx("ab.held")}</th><th class="n">${tx("ab.tests")}</th></tr></thead><tbody>${prows}</tbody></table></div></div>
      <div class="panel"><h3>${tx("ab.limits")} ${tag("data")}</h3><ul class="small">${[1, 2, 3, 4, 5, 6].map((i) => `<li>${tx("ab.l" + i)}</li>`).join("")}</ul></div>
      <div class="panel"><h3>${tx("ab.sources")} ${tag("data")}</h3><ul class="small">${DATA.meta.sources.map((s) => `<li>${esc(s.id)} (${tx("ab.downloaded", { d: s.downloaded })}): <span lang="en">${esc(s.coverage)}</span></li>`).join("")}</ul></div>
      <p class="small muted">${tx("ab.built", { d: DATA.meta.built, r: DATA.rules.review_status })} ${tag("data")}</p>
    </section>`;
  }

  /* ---------- page chrome, render and events ---------- */
  function chrome() {
    document.documentElement.lang = lang;
    document.getElementById("season").textContent = t("head.season");
    document.getElementById("about-link").textContent = t("head.about");
    document.getElementById("foot-text").textContent = t("foot");
    const btn = document.getElementById("lang-toggle");
    btn.textContent = t("lang.toggle");
    btn.setAttribute("aria-label", t("lang.toggleLabel"));
    btn.lang = lang === "en" ? "kn" : "en";
    const draft = document.getElementById("lang-draft");
    draft.textContent = t("lang.draft");
    draft.hidden = !t("lang.draft");
  }

  function render() {
    chrome();
    let html;
    if (state.view === "about") html = about();
    else if (state.view === "welcome") html = welcome();
    else if (state.view === "steps") html = stepView();
    else html = results();
    app.innerHTML = html;
    bind();
  }

  function go(view, step) {
    state.view = view; if (step) state.step = step;
    render(); window.scrollTo(0, 0);
  }

  function bind() {
    const on = (id, ev, fn) => { const el = document.getElementById(id); if (el) el.addEventListener(ev, fn); };
    on("start", "click", () => go("steps", 1));
    on("back", "click", () => (state.step > 1 ? go("steps", state.step - 1) : go("welcome")));
    on("next", "click", () => (state.step < 3 ? go("steps", state.step + 1) : go("results")));
    app.querySelectorAll("[data-goto]").forEach((b) => b.addEventListener("click", () => go("steps", Number(b.dataset.goto))));
    on("back-results", "click", () => { history.replaceState(null, "", location.pathname); go(state.risk ? "results" : "welcome"); });
    app.querySelectorAll(".choice[data-key]").forEach((b) => b.addEventListener("click", () => { state[b.dataset.key] = b.dataset.v; render(); }));
    app.querySelectorAll(".choice[data-late]").forEach((b) => b.addEventListener("click", () => { state.late_sowing = b.dataset.late === "1"; render(); }));
    app.querySelectorAll("[data-step]").forEach((b) => b.addEventListener("click", () => {
      const k = b.dataset.step, max = k === "guntas" ? 39 : 500;
      state[k] = Math.min(max, Math.max(0, (Number(state[k]) || 0) + Number(b.dataset.d))); render();
    }));
    ["acres", "guntas"].forEach((k) => on("in-" + k, "change", (e) => { state[k] = Math.max(0, Number(e.target.value) || 0); render(); }));
    app.querySelectorAll("[data-open]").forEach((b) => b.addEventListener("click", () => { state.open = state.open === b.dataset.open ? null : b.dataset.open; render(); }));
    app.querySelectorAll("[data-choose]").forEach((b) => b.addEventListener("click", () => { state.chosen = b.dataset.choose; render(); }));
    on("reason", "input", (e) => { state.reason = e.target.value; document.getElementById("summary-text").textContent = summaryText(E.run(DATA, state)); });
    on("copy", "click", () => {
      const btn = document.getElementById("copy"), text = document.getElementById("summary-text").textContent;
      const selectIt = () => { const r = document.createRange(); r.selectNodeContents(document.getElementById("summary-text")); const s = getSelection(); s.removeAllRanges(); s.addRange(r); btn.textContent = t("ch.selected"); };
      try { navigator.clipboard.writeText(text).then(() => { btn.textContent = t("ch.copied"); }, selectIt); } catch (err) { selectIt(); }
    });
    E.CROPS.forEach((c) => [["oy", "own_yield"], ["op", "price_override"], ["oc", "own_cost"]].forEach(([p, key]) =>
      on(`${p}-${c}`, "change", (e) => { const v = Number(e.target.value); if (v > 0) state[key][c] = v; else delete state[key][c]; render(); })));
  }

  document.getElementById("home-link").insertAdjacentHTML("afterbegin", ICON.logo);
  document.getElementById("home-link").addEventListener("click", (e) => { e.preventDefault(); go("welcome"); });
  document.getElementById("about-link").addEventListener("click", (e) => { e.preventDefault(); go("about"); });
  document.getElementById("lang-toggle").addEventListener("click", () => {
    lang = lang === "en" ? "kn" : "en";
    try { localStorage.setItem("croppilot.lang", lang); } catch (err) { /* storage unavailable */ }
    if (DATA) render(); else chrome();
  });
  chrome();

  /* Test hook for tests/ui_audit.js (tasks 4.14-4.17): show the results for a profile, in a language,
     with one crop's details open. Not used by the page itself. */
  window.CropPilotTest = {
    show(profile, language, openCrop, chosen) {
      Object.assign(state, { own_yield: {}, own_cost: {}, price_override: {}, reason: "" }, profile,
        { view: "results", open: openCrop || null, chosen: chosen || null });
      lang = language;
      render();
      return E.run(DATA, state);
    },
    about(language) { lang = language; state.view = "about"; render(); },
    ready: () => DATA !== null,
  };

  fetch("data/engine_data.json")
    .then((r) => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then((d) => { DATA = d; state.view = location.hash === "#about" ? "about" : "welcome"; render(); })
    .catch((err) => { app.innerHTML = `<div class="notice">${tx("load.error", { err: err.message })}</div>`; });
})();
