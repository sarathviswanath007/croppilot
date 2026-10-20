# Polaris CropPilot: Data Gap and Dependency Register

Starts from PRD §5.4 (G1–G14). Updated as data arrives (task 1.53). Status: Open / Mitigated / Closed.

| ID | Gap or dependency | Impact | Handling | Status (2026-10-19) |
|---|---|---|---|---|
| G1 | No farm-level yield data; models predict district averages | High | Labels; farmer calibration; wide ranges; expert review | Open |
| G2 | Soybean has short or patchy history in some districts | High | Sufficiency rule; pooled training | **Confirmed:** soybean ≥ 500 ha only in Kalaburagi+Yadgir (13 seasons) and Bidar (17). Shown as "not enough local data" elsewhere |
| G3 | Latest seasons of district yields unpublished | Medium | Train on what exists; show "data through" | **Larger than expected:** ICRISAT ends 2019. 2020–2025 missing for all crops. DES needs a login (D-04) |
| G4 | Costs are state averages with a lag | High | Inflation adjustment; user override; show cost year | Mitigated: Karnataka A2+FL 2024-25 from CACP, inflated to Kharif 2027 at a flat 3%/yr (D-09) as a placeholder for CPI-AL; `data/costs.csv` |
| G5 | Harvest-marketing windows not documented | Medium | Derive from arrival peaks; expert check | **Derived** (`data/harvest_windows.csv`, pending expert): tur Jan–Feb (49% of arrivals; Dec is just below the cut-off, PRD guessed Dec–Feb), soybean Oct–Nov (57%, matches PRD), cotton Nov–Mar (69%, PRD guessed Nov–Jan), maize Oct–Jan (68%) |
| G6 | Farmers may sell below APMC modal prices | Medium | State assumption; price override | Open |
| G7 | No irrigated yields at district level | Medium | Protective-irrigation adjustment is an assumption | Open |
| G8 | No parcel-level soil maps | Medium | Farmer inputs; Soil Health Card | Open |
| G9 | Pest and disease not integrated | Medium | Expert-curated notes | Open |
| G10 | NASA POWER is coarse | Medium | NASA POWER for MVP; IMD cross-check | **Confirmed:** downloaded 1981–2025 for 6 district points. Heavy-rain days (≥ 64.5 mm, Sep–Oct) are 0 in almost every season: the coarse grid smooths out downpours, so that feature carries no signal. Drop it from the models, or use IMD gridded rain (P1) |
| G11 | MSP procurement share not modelled | Medium | MSP shown as reference only | Open |
| G12 | Crop and market naming varies | Low | Mapping table with tests | **Seen:** CEDA has two tur entries ("Arhar (Tur/Red Gram)(Whole)" id 49, "Red Gram" id 7); ICRISAT uses "PIGEONPEA", "SOYABEAN", "Yadagiri", "Gulbarga", "Bellary" |
| G13 | Claude sandbox cannot reach government portals | High | — | **Closed:** working locally with Claude Code (D-03) |
| G14 | Agronomy expert access | High | Book in Phase 0 | Open |
| G15 | **New.** ICRISAT maize is all seasons combined, not Kharif-only | Medium | Check the Rabi share with DES or the expert; label maize yields accordingly | Open |
| G16 | **New.** CACP report is a scanned PDF with no text layer | Low | Transcribe the needed Karnataka rows by hand from Annex 5.5 and 5.6; double-check each value | **Mitigated:** 12 crop-years transcribed; every printed subtotal re-adds within ₹2 (`scripts/p1_build_cacp_costs.py`). Yields are not covered by that check. The cotton page's last column is mislabelled "% change" but holds rupee values; ignored |
| G17 | **New.** CEDA API returns intermittent HTTP 500 errors | Low | Retry in smaller date chunks; log failures | **Mitigated:** full download (tur, soybean, cotton, maize, plus green gram, now unused) completed with retries and no failures. Data run Feb 2002–Oct 2025; maize ends May 2025 |
| G18 | **New.** CEDA uses Census 2011 districts: Vijayanagara is inside Bellary | Low | Matches the Ballari+Vijayanagara model unit | Mitigated |
| G19 | **New.** Three very low yields in ICRISAT: Kalaburagi tur 1992-93 (23 kg/ha), Bidar tur 1997-98 (72 kg/ha), Kalaburagi soybean 2009-10 (103 kg/ha). Internally consistent (production matches yield) | Medium | Kept and flagged as possible crop failures: dropping them would understate downside risk. Cross-check with DES or the expert | Open |
| G20 | **New.** ICRISAT "Year" assumed to mean agricultural year Y to Y+1 (1990 → 1990-91) | Medium | Wrong by one year would misalign yields with weather | **Closed:** for tur, cotton and maize, yield anomalies correlate with same-year Jun–Sep rain (r = +0.25, +0.05, +0.11) and Jul–Aug dry spell (r = −0.30, −0.16, −0.30); offsets of ±1 year show no or reversed relation. An alignment check only, run on all seasons; not used for feature or model selection |
| G21 | **New.** Before 1998 the Raichur unit includes Koppal (Koppal missing in ICRISAT) | Low | Rows flagged `includes_koppal`; yields comparable, areas larger | Mitigated |
| G22 | **New.** CEDA monthly arrivals have reporting breaks (market coverage changes), e.g. Raichur cotton ~2,600 t/month (Jan 2022) → 24 t (Jan 2024) → 55,000 t (Nov 2024) | Low | Arrivals not used as a price-model feature (D-16); arrivals still used for harvest-window shares, pooled over many years | Mitigated |
