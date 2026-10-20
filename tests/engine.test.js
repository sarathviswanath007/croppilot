// Task 3.34: JS engine tests for the PRD 6.9 dummy cases (AC-07). Run: node --test tests/
"use strict";
const test = require("node:test");
const assert = require("node:assert");
const E = require("../web/js/engine.js");
const DATA = require("../data/engine_data.json");

const close = (a, b) => assert.ok(Math.abs(a - b) < 1e-9, `${a} != ${b}`);

test("PRD 6.9 scores", () => {
  const a = { p10: -4000, p50: 10000 }, b = { p10: 2000, p50: 8000 };
  [[0.7, 200, 3800], [0.4, 4400, 5600], [0.1, 8600, 7400]].forEach(([lam, sa, sb]) => {
    close(E.score(a, lam), sa);
    close(E.score(b, lam), sb);
  });
});

test("PRD 6.9 rank flips with risk preference", () => {
  const expected = { cautious: ["B", "A"], balanced: ["B", "A"], growth: ["A", "B"] };
  for (const [risk, order] of Object.entries(expected)) {
    const lam = DATA.rules.ranking.lambda[risk];
    const crops = [
      { crop: "A", net_acre: { p10: -4000, p50: 10000 }, loss_chance: 0.1, win_rate: 0.3, confidence: "Medium" },
      { crop: "B", net_acre: { p10: 2000, p50: 8000 }, loss_chance: 0.1, win_rate: 0.7, confidence: "Medium" },
    ];
    crops.forEach((c) => { c.score = E.score(c.net_acre, lam); });
    assert.deepStrictEqual(E.rankCrops(crops, DATA.rules.ranking).map((c) => c.crop), order, risk);
  }
});

test("PRD 6.9 break-even and whole field", () => {
  const d = JSON.parse(JSON.stringify(DATA));
  const key = "kalaburagi_yadgir|tur";
  d.rules.adjustments.cost_band = [0, 0];
  d.yield_draws[key].q_per_acre = d.yield_draws[key].weather_seasons.map(() => 5.0);
  d.yield_draws[key].rel_errors = [0];
  Object.assign(d.price[key], { forecast: 6000, log_errors: [0], error_seasons: [2000] });
  d.costs.tur.a2fl_per_acre = 20000;
  const res = E.run(d, { district: "Kalaburagi", acres: 2, guntas: 20, soil: "deep_black", drainage: "drains_well", water: "rainfed" });
  const tur = res.ranked.find((c) => c.crop === "tur");
  close(tur.break_even_price, 4000);
  close(tur.break_even_yield, 20000 / 6000);
  close(tur.net_field.p50, 25000);
});

test("PRNG known sequence matches Python", () => {
  const r = E.mulberry32(20261020);
  assert.deepStrictEqual([r(), r(), r()], [0.264247833751142, 0.23858783044852316, 0.8627477055415511]);
});
