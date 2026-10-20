# Polaris CropPilot: Acceptance Report (task 6.12)

**Status as of 20 October 2026**, before deployment, UAT and the expert session. Prepared by Claude for the project owner; the owner signs off each gate.

## Acceptance criteria (PRD 8.2)

| ID | Criterion | Status | Evidence | Next action |
|---|---|---|---|---|
| AC-01 | ≥ 3 crops pass sufficiency in ≥ 3 units; ≥ 10 price seasons; dated cost per crop | ✅ Pass | `data_quality_report.md` §2, §7; Gate 1 (D-11) | — |
| AC-02 | Every source has status, coverage, date, issues; gap register current | ✅ Pass | `raw/raw_sources_log.csv`, `data_gap_register.md` (G1–G22) | Keep current at each refresh |
| AC-03 | Yield backtests vs B1 and B2 for every crop, with MAE, skill, coverage, n | ✅ Pass | `model_card_yield.md` §6 | — |
| AC-04 | Price backtests vs P1 and P2 | ✅ Pass | `model_card_price.md` §5 | — |
| AC-05 | ML used for ≥ 2 crops where it beats its baseline | ✅ Pass, with caveat | Tur yield (M2) and soybean price (ridge); both 90% CIs include 0 (Gate 2, D-19) | State the caveat in the demo |
| AC-06 | JS matches Python within ±1% on percentiles, exact ranks, 10 farms | ✅ Pass | `parity_test_log.md` (max difference 3×10⁻¹⁵) | Re-run after any engine change |
| AC-07 | PRD 6.9 dummy cases pass, including rank changes with risk preference | ✅ Pass | `tests/test_p3_engine.py`, `tests/engine.test.js` | — |
| AC-08 | 100% of displayed numbers carry a label and source or method | ✅ Pass (automated); manual review pending | `tests/ui_audit.js`: 63 result views + About, English and Kannada | Owner skims `explanations_test_farms.md` in UAT (task 4.16) |
| AC-09 | Banned-word scan finds no guarantee language | ✅ Pass | `scripts/p5_build_web.py` (source, English + Kannada) and `tests/ui_audit.js` (rendered text) | — |
| AC-10 | ≥ 4 of 5 first-time testers finish the journey in ≤ 5 min on a phone | ⏳ Pending | `usability_test_script.md` Task A | Run with testers after deployment (UAT) |
| AC-11 | ≥ 4 of 5 testers explain "low" and why the top crop ranked first | ⏳ Pending | `usability_test_script.md` Task B | Same sessions |
| AC-12 | Expert reviews rules and ≥ 5 sample outputs; every issue fixed or documented | ⏳ Pending | `expert_pack.md` ready | Book the reviewer (tasks 0.35, 0.36 still open) |
| AC-13 | Zero-cost checklist passes | ⏳ Partly | `zero_cost_checklist.md`: Z-01, Z-03, Z-04, Z-06, Z-07 ✅ | Owner: free hosting tier (Z-05); credits still off on demo day (Z-08) |
| AC-14 | The published link opens and the core flow works without signing in | ⏳ Pending deployment | Works on http://localhost:8000 (checked in Chrome, English and Kannada) | Check the live URL in a private window |
| AC-15 | Any eligible crop can be selected; summary says the decision is theirs | ✅ Pass (automated); confirm in UAT | Audit selects the last-ranked crop for every farm; summary ends "The decision is mine…" | Confirm by hand in UAT |

## Task status by phase

| Phase | Done by Claude | Waiting for people |
|---|---|---|
| 0 | Contracts, rules frozen, checklists | 0.35–0.36 expert booking; Q-01 note |
| 1 | All data tasks | 1.23 ginning outturn (kept at 0.34 `[Assumption]`, in expert pack); 1.11 CPI-AL (flat 3%, D-09) |
| 2 | All P0/P1 tasks; Gate 2 passed (D-19) | — (P2 stretch tasks 2.13, 2.20 not built) |
| 3 | Engine, tests, parity, timing, decision backtest (3.37) | **Gate 3** sign-off |
| 4 | Templates in both languages, confidence logic, label + wording audits, explanations for 10 farms | 4.16 plain-language review; **Gate 4** sign-off |
| 5 | Web app (D-22, D-24), Kannada toggle (D-25), local server, About page, test script | Deployment (5.31), phone checks (5.29–5.30), user tests (5.34–5.37), **Gate 5** |
| 6 | Expert pack, refresh checklist, demo script, this report | Expert session and note (6.02–6.05), rebuild after changes (6.07), zero-cost sign-off (6.10), rehearsal (6.14), **Gate 6** |

## Known limitations to carry into UAT

1. District yields end in 2019-20; the 2027 estimate rests on older seasons (G3).
2. Only tur yield and soybean price use ML, and both gains are uncertain. Maize ranges are too narrow (47% coverage).
3. Prices run to May 2025 (soybean May 2024); 6 of 17 district-crop prices are borrowed from neighbours (D-17, D-18).
4. Costs are state averages inflated at an assumed 3% a year (D-09).
5. Rules, soil tiers, sowing windows and the Kannada text are unreviewed drafts.
6. The decision backtest shows CropPilot level with "last season's most profitable crop", not better.
