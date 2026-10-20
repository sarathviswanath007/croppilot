# Polaris CropPilot: Data Quality Report (Phase 1, task 1.52)

**Built:** 19 October 2026 · **Crops:** tur, maize, soybean, cotton (D-05) · **Region:** 7 districts in 5 model units (D-07)
Every number here is reproducible from `raw/` with the scripts in `scripts/`. Tests: `python3 -m unittest discover -s tests` (18 pass).

---

## 1. Sources used

| Input | Source | Coverage | Output file | Script |
|---|---|---|---|---|
| Yields | ICRISAT DLD, unapportioned (D-04) | 1990-91 to 2019-20 | `data/panel_yield.csv` | `p1_build_panel_yield.py` |
| Weather | NASA POWER daily, 6 district points | 1981–2025 | `data/weather_features.csv` | `p1_download_nasa_power.py`, `p1_build_weather_features.py` |
| Prices and arrivals | CEDA Agri Market Data (monthly, Census 2011 districts) | Feb 2002 – Oct 2025 (maize to May 2025) | `data/prices_monthly.csv` | `p1_download_ceda_prices.py`, `p1_build_prices.py` |
| Harvest windows | Derived from CEDA arrival peaks | — | `data/harvest_windows.csv` | `p1_build_prices.py` |
| Costs | CACP Price Policy for Kharif Crops 2026-27, Annex 5.5 and 5.6 (hand-transcribed) | Karnataka, 2022-23 to 2024-25 | `data/costs.csv` | `p1_build_cacp_costs.py`, `p1_build_costs.py` |
| MSP | DES official series (RTI reply, May 2026); 2026-27 from news reports | 1995-96 to 2026-27 | `data/msp.csv` | transcribed |

All 18 raw files are logged with URL, download date and coverage in `raw/raw_sources_log.csv`.

## 2. Coverage grid: yields

Seasons with ≥ 500 ha of the crop (PRD §5.5 sufficiency rule: ≥ 10 needed). From `data/panel_yield_coverage.csv`.

| Model unit | Tur | Maize | Soybean | Cotton |
|---|---|---|---|---|
| Kalaburagi + Yadgir | 30 ✅ | 30 ✅ | 13 ✅ | 30 ✅ |
| Bidar | 30 ✅ | 15 ✅ | 17 ✅ | 24 ✅ |
| Raichur | 30 ✅ | 21 ✅ | 0 ❌ | 30 ✅ |
| Koppal | 22 ✅ | 22 ✅ | 0 ❌ | 22 ✅ |
| Ballari + Vijayanagara | 30 ✅ | 30 ✅ | 0 ❌ | 30 ✅ |

**17 of 20 unit × crop cells pass** (corrected 2026-10-20 from "18": 5 + 5 + 2 + 5). Soybean shows "not enough local data" in Raichur, Koppal and Ballari (as the PRD expected, G2).

## 3. Coverage grid: harvest-window prices

Kharif seasons with at least one harvest-window month of prices / with every window month present.

| Model unit | Tur (Jan–Feb) | Maize (Oct–Jan) | Soybean (Oct–Nov) | Cotton (Nov–Mar) |
|---|---|---|---|---|
| Kalaburagi + Yadgir | 15 / 14 | 11 / 4 | 11 / 11 | 18 / 8 |
| Bidar | 15 / 15 | 18 / 2 | 23 / 23 | 7 / 0 |
| Raichur | 24 / 23 | 22 / 8 | — | 24 / 23 |
| Koppal | 14 / 14 | 23 / 21 | — | 18 / 3 |
| Ballari + Vijayanagara | 14 / 14 | 23 / 23 | 1 / 0 | 23 / 23 |

Every crop has ≥ 10 marketing seasons of prices in each unit where it passes the yield rule, except cotton in Bidar (7). Bidar cotton can borrow the pooled price series (price model is pooled across districts, PRD §4.3).

## 4. Cleaning and checks

### Yields
- 206 source values dropped and logged (`data/panel_yield_dropped.csv`): 120 missing (`-1`), 84 not grown (area 0), 2 with area but zero yield.
- Districts harmonised by summing area; yield is the area-weighted mean of ICRISAT's reported yields (cotton area and production are rounded to whole thousands in the source).
- **Units:** yield kg/ha → q/acre (÷ 100 ÷ 2.471), tested. Cotton is **lint** in ICRISAT (yield ≈ 430–680 kg/ha), converted to kapas later with the ginning outturn.
- **Sanity ranges:** 3 rows outside, all kept and flagged (G19): Kalaburagi tur 1992-93 (23 kg/ha), Bidar tur 1997-98 (72 kg/ha), Kalaburagi soybean 2009-10 (103 kg/ha). Production matches yield in the source, so they look like real crop failures.
- **Year alignment (G20, closed):** yield anomalies correlate with same-year weather (tur: r = +0.25 with Jun–Sep rain, −0.30 with Jul–Aug dry spell) and not with ±1 year. Alignment check only; not used for feature or model choice.
- Flags carried in the panel: `includes_koppal` (Raichur before 1998), `yadgir_inside_kalaburagi` (before 2010), `all_seasons_not_kharif_only` (maize, G15), `below_500ha`.

### Weather
- No missing days in 1981–2025 for any point.
- Units with two districts use the day-by-day average of both points, then features are computed.
- Mean Jun–Sep rain: Bidar 724 mm, Kalaburagi+Yadgir 589, Raichur 471, Koppal 373, Ballari 349.
- **Heavy-rain days (≥ 64.5 mm, Sep–Oct) are almost always 0** in NASA POWER (G10). The coarse grid smooths out downpours, so this feature carries no signal and should be left out of Phase 2 models unless IMD gridded rain is added.

### Prices
- 24 of 3,134 district-months dropped (0.8%), all logged in `data/prices_dropped.csv` (D-06): 12 spikes vs neighbouring months, 11 outliers vs other districts in the same month, 1 blank.
- 15 kept but flagged: modal price outside that month's min–max (the min/max fields are what is broken in the cases checked).
- **Change from the PRD:** no 1st/99th-percentile cap, because prices are nominal and roughly tripled over 2002–2025. No trading-day rule (CEDA has no day counts).
- Two-district units use arrivals-weighted means. CEDA's sparse "Red Gram" entry (id 7) is not used; "Arhar (Tur/Red Gram)(Whole)" (id 49) is.
- **Assumption:** CEDA quantities are tonnes.

### Harvest windows (pending expert check)

| Crop | Derived window | Share of arrivals | PRD starting guess |
|---|---|---|---|
| Tur | Jan–Feb | 49% | Dec–Feb (Dec just below the cut-off) |
| Soybean | Oct–Nov | 57% | Oct–Nov |
| Cotton | Nov–Mar | 69% | Nov–Jan |
| Maize | Oct–Jan | 68% | — |

### Costs
- 12 crop-years transcribed from the scanned CACP report. **Every printed subtotal re-adds within ₹2** (`p1_build_cacp_costs.py`), so misread digits would be caught. Yields on those pages are not covered by that check.
- A2+FL and C2 are derived from line items with the standard CACP definitions. A2+FL/C2 ratios are within 2.5 points of CACP's own 2026-27 projections for all crops.
- Inflated to Kharif 2027 at a flat 3% a year (D-09, placeholder for CPI-AL):

| Crop | A2+FL per acre, 2024-25 | Kharif 2027 (× 1.0927) |
|---|---|---|
| Tur | ₹18,341 | ₹20,042 |
| Maize | ₹24,028 | ₹26,256 |
| Soybean | ₹22,775 | ₹24,887 |
| Cotton | ₹28,917 | ₹31,599 |

### MSP
- DES official series, cross-checked against two other DES statements (agree). No year-on-year decreases in any crop, a basic transcription check.
- Bonuses are included where DES includes them and noted per row; the 2002-03 drought-relief add-on and the 2010–12 tur procurement incentive are noted, not included.
- 2026-27 values are from news reports and match the reported increases exactly; verify against the PIB release.
- Leakage rule (D-08): the price model uses the previous season's MSP.

## 5. Cross-source comparisons not yet done

| PRD item | Status | Why |
|---|---|---|
| DES vs ICRISAT yields, overlapping years | Not done | DES needs a login (D-04) |
| NASA POWER vs ICRISAT/IMD rainfall | Not done (P1) | Needs ICRISAT rainfall or IMD files; schedule before Phase 2 tuning if time allows |
| Recent prices vs Agmarknet daily data | Not done (P1) | Optional spot check |

## 6. Known limitations going into Phase 2

1. **Yields end in 2019-20** (G3). Six seasons (2020–2025) are missing, so the model's trend term is extrapolated 7+ years to Kharif 2027.
2. **Maize yields mix Kharif and Rabi** (G15).
3. **Soybean has short series** (13 and 17 seasons) in only two units: ML is unlikely to beat the baseline there, and the backtest will have very few test seasons.
4. **No heavy-rain signal** in the weather features (G10).
5. **Costs are state averages** inflated by an assumed 3% (G4, D-09).

## 7. Gate 1 check

| Criterion | Result | Evidence |
|---|---|---|
| **AC-01** ≥ 3 of 4 crops pass sufficiency in ≥ 3 of 5 units | ✅ Tur, maize and cotton pass in 5 of 5; soybean in 2 | Section 2 |
| **AC-01** ≥ 10 marketing seasons of prices per crop | ✅ Tur 24, maize 23, soybean 23, cotton 24 (across units) | Section 3 |
| **AC-01** dated Karnataka cost estimate per crop | ✅ CACP, cost year 2024-25, all four crops | `data/costs.csv` |
| **AC-02** every source has status, coverage, download date, known issues; gap register current | ✅ | `raw/raw_sources_log.csv`, `data_gap_register.md` |

**Recommendation: pass Gate 1**, with the limitations in section 6 carried into the Phase 2 model cards.
