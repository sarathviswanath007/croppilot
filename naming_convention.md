# Polaris CropPilot: File-Naming Convention (task 0.06)

Claude Project files are stored flat, so every file name must be unique on its own, without its folder. The local folders below are only for tidiness.

## General rules

- Lowercase `snake_case`, ASCII only, no spaces.
- Dates as `YYYYMMDD`.
- Crop keys: `tur`, `maize`, `soybean`, `cotton` (green gram swapped for maize, decision D-05).
- Model-unit keys: `kalaburagi_yadgir`, `ballari_vijayanagara`, `raichur`, `koppal`, `bidar`.
- Composite keys inside data: `<unit>|<crop>`, for example `bidar|tur`.
- Never overwrite a raw file. A new download gets a new date.

## File types

| Kind | Folder (local) | Pattern | Example |
|---|---|---|---|
| Raw download | `raw/` | `raw_<source>_<content>_<scope>_<YYYYMMDD>.<ext>` | `raw_ceda_prices_kk_20261021.csv` |
| Derived dataset | `data/` | `<content>.csv` (names fixed by the PRD) | `panel_yield.csv`, `weather_features.csv` |
| Mapping table | `data/` | `map_<what>.csv` | `map_crop_names.csv` |
| Config | `config/` | `<what>.json` | `rules.json`, `config_constants.json` |
| Contract | `contract/` | `engine_data.<variant>.json` | `engine_data.schema.json`, `engine_data.mock.json` |
| Script | `scripts/` | `p<phase>_<verb>_<object>.py` | `p1_build_panel_yield.py` |
| Report or log | root | `<what>.md` | `data_quality_report.md`, `model_card_yield.md` |
| Export for the engine | `data/` | `export_<what>.json` | `export_yield_draws.json` |

## Source codes (for raw files)

`des`, `idp` (India Data Portal), `icrisat`, `ceda`, `agmarknet`, `datagov`, `pib`, `cacp`, `descoc` (DES cost of cultivation), `nasapower`, `imd`, `uasr` (UAS Raichur), `ecocrop`, `cpial`, `soilgrids`.

Scope codes: `kk` (all seven Kalyana-Karnataka districts), `ka` (Karnataka), or a district key such as `kalaburagi`.

## Provenance

Every raw file gets a row in `raw_sources_log.csv`. Every derived file names its input files and its script, either in a header comment or in a sidecar `<name>.provenance.md`.
