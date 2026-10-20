# Polaris CropPilot

Compares four Kharif crops (tur, maize, soybean, cotton) for a farm in Kalyana-Karnataka (Kalaburagi, Yadgir, Bidar, Raichur, Koppal, Ballari, Vijayanagara) and shows estimated profit in a bad, typical and good year, from district yields, market prices, costs and past weather. English and Kannada (draft). The farmer makes the choice.

Specification: `polaris-croppilot-prd.md` · tasks: `tasks.md` · decisions: `decisions_log.md` · status: `acceptance_report.md`.

## Run the web app locally

```
python3 scripts/p5_serve.py        # then open http://localhost:8000
```

The app is a static site in `web/` (no server code). To deploy, upload the `web/` folder to any static host; see `web/README.md`.

## Rebuild data, models and tests

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
(cd tools && npm install)          # test-only: jsdom for the UI audit
```

Then follow `refresh_checklist.md` (data → models → engine → audits → web build).

## Layout

| Folder | Contents |
|---|---|
| `raw/` | Downloaded source files, logged in `raw/raw_sources_log.csv` (the 54 MB CACP PDF is not in git; re-download it from the logged URL) |
| `data/` | Cleaned and derived data, backtests, exports, `engine_data.json` |
| `scripts/` | Pipeline: `p1_*` data, `p2_*` models and backtests, `p3_*` engine, `p5_*` web build and server |
| `config/` | `rules.json` (unreviewed rules), `banned_words.json` |
| `contract/` | Engine data JSON Schema and mock |
| `web/` | The web app (HTML, CSS, JS, data copy) |
| `tests/` | Python and JS tests, test farms, UI audit |

## Data licences

Licence terms for the data sources (CEDA, ICRISAT, NASA POWER, CACP, DES) are not yet recorded (`data_availability_checklist.md` §5, task 0.25). Check them before making this repository or the app public.
