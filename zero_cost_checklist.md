# Polaris CropPilot: Zero-Cost Checklist (NFR-01, AC-13)

Tick each item, with the date and who checked. Re-check everything at task 6.10.

| # | Check | Phase | Checked (date, who) | Result |
|---|---|---|---|---|
| Z-01 | Usage credits beyond the Claude Pro plan are **disabled** (task 0.03) | 0 | 2026-10-19, user | ✅ Off |
| Z-02 | Code execution and file creation are on, and are part of the Pro plan (task 0.01) | 0 | 2026-10-20, Claude | N/A: work moved to local Claude Code (D-03) |
| Z-03 | No paid API keys are used (data.gov.in key is free; NASA POWER needs none) | 1 | 2026-10-20, Claude | ✅ No API keys anywhere in the pipeline or app |
| Z-04 | No paid data downloads or subscriptions | 1 | 2026-10-20, Claude | ✅ All 18 raw files are free public downloads (`raw/raw_sources_log.csv`) |
| Z-05 | No paid hosting (D-22: static site on the owner's cloud instead of a Claude artifact) | 5 | | **Owner to confirm:** use a free static-hosting tier; `web/` is 140 KB with no server code |
| Z-06 | The dashboard's core flow makes no AI calls (viewers' limits are never used) | 5 | 2026-10-20, Claude | ✅ The app's only network request is its own `data/engine_data.json` (plus Google Fonts) |
| Z-07 | Any local software used is free and allowed by decision Q-04 (`decisions_log.md`) | 0–6 | 2026-10-20, Claude | ✅ Python, numpy, scikit-learn, PyMuPDF, Node.js, jsdom (test only): all free / open source (D-03) |
| Z-08 | Usage credits still disabled on the demo day | 6 | | |
