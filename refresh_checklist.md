# Polaris CropPilot: Refresh Checklist (task 6.11, NFR-10)

Run once a year before Kharif decisions (April–May), and after any expert change. All commands run from the project folder. Every step keeps the rules in `project_instructions.md`: never invent data, log every raw file, label every number.

## 1. New data (April–May each year)

| What | Source | Steps |
|---|---|---|
| District yields | ICRISAT DLD, or India Data Portal / DES for seasons after 2019-20 (gap G3) | Download to `raw/` with a dated name; log in `raw/raw_sources_log.csv`; extend `scripts/p1_build_panel_yield.py` if the format differs |
| Market prices and arrivals | CEDA Agri Market Data | `python3 scripts/p1_download_ceda_prices.py`, then `python3 scripts/p1_build_prices.py` |
| Weather | NASA POWER | `python3 scripts/p1_download_nasa_power.py`, then `python3 scripts/p1_build_weather_features.py` |
| Costs | Latest CACP "Price Policy for Kharif Crops" | Transcribe Karnataka rows into `data/cacp_karnataka_cost_breakup_transcribed.csv`; `python3 scripts/p1_build_cacp_costs.py`; `python3 scripts/p1_build_costs.py`. Replace the flat 3% with CPI-AL when available (D-09) |
| MSP | PIB / CACP release for the new season | Add rows to `data/msp.csv`, **with the announcement date** (leakage rule, D-08) |

Then update `data_quality_report.md` and `data_gap_register.md`.

## 2. Models (after new data)

```
.venv/bin/python scripts/p2_build_features_yield.py
.venv/bin/python scripts/p2_build_features_price.py
.venv/bin/python scripts/p2_run_yield_backtest.py      # ~10 minutes
.venv/bin/python scripts/p2_run_price_backtest.py
.venv/bin/python scripts/p2_select_models.py           # applies selection_rules.md as frozen
.venv/bin/python scripts/p2_export.py
```

- Move the target season forward: `TARGET_SEASON` and `PRICE_ASOF_SEASON` in `scripts/p2_export.py`; check D-14/D-17/D-18 still make sense.
- **Do not edit `selection_rules.md`** to get a better result. A change needs a dated change-log row saying whether test results were seen.
- Update `model_card_yield.md` and `model_card_price.md` with the new metrics, including crops where the model loses.

## 3. Engine, app and tests

```
.venv/bin/python scripts/p3_build_engine_data.py       # validates against the contract
.venv/bin/python -m unittest discover -s tests
node --test tests/engine.test.js
.venv/bin/python scripts/p3_parity_test.py             # AC-06
.venv/bin/python scripts/p3_decision_backtest.py       # optional, ~1 minute
(cd tools && npm run audit)                            # AC-08, AC-09; regenerates explanations
.venv/bin/python scripts/p5_build_web.py               # copies data into web/, wording scan
```

All must pass before deploying. Then check the app locally (`python3 scripts/p5_serve.py`) in English and Kannada.

## 4. Text and rules

- Update season wording ("Kharif 2027", "Prices run to May 2025" …) in `web/js/i18n.js` (both languages) and the dates in the About page.
- Any rule change in `config/rules.json` needs the expert's name and date, and an entry in `decisions_log.md`.
- New or changed Kannada text needs a native-speaker check (R17).

## 5. Deploy and verify

- Upload the `web/` folder to the static host (see `web/README.md`).
- Open the live link in a private window: run the core flow (AC-14) and select a non-top crop (AC-15).
- Re-check `zero_cost_checklist.md`.
