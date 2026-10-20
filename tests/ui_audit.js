// Tasks 4.14, 4.15, 4.17 (AC-08, AC-09): render the real web app in Node (jsdom) for the 10 test
// farms in English and Kannada, open every crop's details, then check
//   1. label audit: every piece of visible text containing a digit or ₹ sits in a block that carries a
//      Data / Prediction / Assumption / Your-number tag (FR-14, NFR-06)
//   2. wording audit: no banned word from config/banned_words.json in the rendered text (FR-19)
// and write explanations_test_farms.md (English) and explanations_test_farms_kn.md (Kannada) for review.
// Run: (cd tools && npm run audit)    Exit code 1 on any failure.
"use strict";
const fs = require("fs");
const path = require("path");
const { JSDOM } = require(path.join(__dirname, "..", "tools", "node_modules", "jsdom"));

const ROOT = path.join(__dirname, "..");
const WEB = path.join(ROOT, "web");
const read = (p) => fs.readFileSync(p, "utf8");
const DATA = JSON.parse(read(path.join(ROOT, "data", "engine_data.json")));
const FARMS = JSON.parse(read(path.join(ROOT, "tests", "test_farms.json"))).farms;
const BANNED = JSON.parse(read(path.join(ROOT, "config", "banned_words.json")));
// Blocks that carry one label for all the numbers inside them (most specific first).
const BLOCKS = ".detail > div, .answer, .others, .excluded, .answers, #choice, details.panel, .about .panel, .about > p";
const EXEMPT = ".rk, .step-label, .progress, h2";   // rank numbers and headings with the farm's own name

function makeApp() {
  const html = read(path.join(WEB, "index.html")).replace(/<link[^>]+>/g, "").replace(/<script[^>]*><\/script>/g, "");
  const dom = new JSDOM(html, { runScripts: "outside-only", url: "http://localhost/" });
  const w = dom.window;
  w.fetch = () => Promise.resolve({ ok: true, json: () => Promise.resolve(JSON.parse(JSON.stringify(DATA))) });
  w.scrollTo = () => {};
  for (const f of ["i18n.js", "engine.js", "app.js"]) w.eval(read(path.join(WEB, "js", f)));
  return w;
}

function labelAudit(w, where) {
  const fails = [];
  const walker = w.document.createTreeWalker(w.document.getElementById("app"), w.NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const text = n.textContent.trim();
    if (!/[0-9]/.test(text)) continue;   // a ₹ sign alone (e.g. in a column heading) is a unit, not a number
    const el = n.parentElement;
    if (el.closest(EXEMPT) || el.closest("[hidden]")) continue;
    const block = el.closest(BLOCKS);
    if (!block || !block.querySelector(".tag")) fails.push(`${where}: unlabelled number "${text.slice(0, 60)}"`);
  }
  return fails;
}

function wordAudit(text, where) {
  let low = text.toLowerCase();
  for (const p of BANNED.allowed_phrases) low = low.split(p.toLowerCase()).join(" ");
  const fails = [];
  for (const word of BANNED.banned) {
    const re = /^[\x00-\x7f]+$/.test(word) ? new RegExp(`(?<![\\w-])${word.replace(/[-]/g, "\\-")}(?![\\w-])`, "i") : new RegExp(word);
    if (re.test(low)) fails.push(`${where}: banned word "${word}"`);
  }
  return fails;
}

// Readable text: one line per block element, labels shown as [Label], "Hide details" links dropped.
const BLOCK_TAGS = new Set(["DIV", "P", "LI", "H2", "H3", "H4", "SECTION", "UL", "DL", "TR", "DT", "SUMMARY", "BUTTON"]);
function visibleText(el) {
  const out = [];
  (function walk(n) {
    if (n.nodeType === 3) { out.push(n.textContent.replace(/\s+/g, " ")); return; }
    if (n.nodeType !== 1 || n.hidden || n.matches("button.link, .chev, svg")) return;
    if (n.matches(".tag")) { out.push(` [${n.textContent}]`); return; }
    if (BLOCK_TAGS.has(n.tagName) || n.matches(".fact, .pill")) out.push("\n");
    if (n.matches(".bar-row .k span")) { out.push(" ("); n.childNodes.forEach(walk); out.push(")"); return; }
    if (n.tagName === "LI") out.push("- ");
    n.childNodes.forEach(walk);
    if (n.tagName === "DT" || n.matches(".k")) out.push(": ");
    if (n.matches(".rk")) out.push(" ");
  })(el);
  return out.join("").split("\n").map((l) => l.replace(/\s+/g, " ").trim()).filter(Boolean).join("\n");
}

async function main() {
  const w = makeApp();
  for (let i = 0; i < 50 && !w.CropPilotTest.ready(); i++) await new Promise((r) => setTimeout(r, 20));
  const app = w.document.getElementById("app");
  const fails = [];
  const docs = { en: [], kn: [] };
  let checkedBlocks = 0;
  for (const lang of ["en", "kn"]) {
    const md = docs[lang];
    for (const farm of FARMS) {
      const res = w.CropPilotTest.show(farm, lang, null, null);
      const crops = res.ranked.map((c) => c.crop);
      const chosen = crops[crops.length - 1];
      md.push(`## ${farm.id}: ${farm.district}, ${farm.acres} acres ${farm.guntas} guntas, ${farm.soil} soil, drainage ${farm.drainage}, ${farm.water}, last crop ${farm.previous_crop}, ${farm.risk}${farm.late_sowing ? ", late sowing" : ""}${farm.own_yield || farm.own_cost || farm.price_override ? ", own numbers entered" : ""}`, "");
      for (const crop of crops.length ? crops : [null]) {
        w.CropPilotTest.show(farm, lang, crop, chosen);
        const where = `${lang}/${farm.id}/${crop}`;
        fails.push(...labelAudit(w, where), ...wordAudit(visibleText(app), where));
        checkedBlocks++;
        if (crop === crops[0] || crop === null) {
          const summary = app.querySelector(".answer") || app;
          md.push("```", visibleText(summary).replace(/\s*✎/g, ""), "```", "");
          const sum = w.document.getElementById("summary-text");
          if (sum) md.push(`Choice summary (choosing the last-ranked crop):`, "", "```", sum.textContent, "```", "");
        }
      }
      const others = app.querySelector(".others"), excl = app.querySelector(".excluded");
      if (others) md.push("Other crops:", "", "```", visibleText(others).replace(/(Details|Hide|ವಿವರ|ಮರೆಮಾಡಿ)/g, ""), "```", "");
      if (excl) md.push("```", visibleText(excl), "```", "");
    }
    w.CropPilotTest.about(lang);
    fails.push(...labelAudit(w, `${lang}/about`), ...wordAudit(visibleText(app), `${lang}/about`));
  }
  const head = (lang) => [
    `# Polaris CropPilot: Explanations for the 10 Test Farms${lang === "kn" ? " (Kannada draft)" : ""} (task 4.15)`, "",
    `Generated ${new Date().toISOString().slice(0, 10)} by \`tests/ui_audit.js\` from the live web app and \`data/engine_data.json\`. ` +
      `For the plain-language review (task 4.16)${lang === "kn" ? " and the native-speaker check (risk R17)" : ""}. ` +
      "Test farms are invented profiles (`tests/test_farms.json`). All amounts are `[Prediction]` district-average estimates unless labelled otherwise.", ""];
  fs.writeFileSync(path.join(ROOT, "explanations_test_farms.md"), head("en").concat(docs.en).join("\n") + "\n");
  fs.writeFileSync(path.join(ROOT, "explanations_test_farms_kn.md"), head("kn").concat(docs.kn).join("\n") + "\n");
  console.log(`Rendered ${checkedBlocks} result views (10 farms x every ranked crop's details x 2 languages) + About x 2.`);
  if (fails.length) { console.log(`FAIL: ${fails.length} problems\n  ` + fails.slice(0, 40).join("\n  ")); process.exit(1); }
  console.log("PASS: every number is labelled (AC-08); no banned words (AC-09).");
}
main().catch((e) => { console.error(e); process.exit(1); });
