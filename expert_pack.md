# Polaris CropPilot: Expert Review Pack (task 6.01)

**For:** an agronomy or extension expert (KVK, UAS Raichur, RSK, or agri-economics faculty). **Time needed:** about 60–90 minutes.
**Purpose:** confirm or correct every rule the app uses that is not backed by data (AC-12). Each item below is currently `[Assumption — unreviewed]`.
**How to answer:** for each item tick ✅ keep, ✏️ change (write the new value), or ❓ unsure. Sign the review note at the end.

The app compares **tur, maize, soybean and cotton** for **Kharif 2027** in Kalaburagi, Yadgir, Bidar, Raichur, Koppal, Ballari and Vijayanagara districts. It estimates profit per acre in a bad, typical and good year from district yields (to 2019-20), APMC prices (to May 2025) and CACP costs (2024-25), then ranks the crops for the farmer's risk setting. The farmer makes the choice.

---

## 1. Soil and drainage suitability (PRD 6.2)

Each crop gets a tier from the farmer's soil and drainage. The tier multiplies the district-average yield.

| Soil and drainage | Tur | Maize | Soybean | Cotton | Your changes |
|---|---|---|---|---|---|
| Deep black, drains well | Good | Fair | Good | Good | |
| Medium black, drains well | Good | Fair | Good | Good | |
| Shallow black | Fair | Fair | Fair | Marginal | |
| Red | Fair | Fair | Fair | Fair | |
| Waterlogs after heavy rain | Marginal | Marginal | Marginal | Fair | |
| Mixed or don't know | Fair | Fair | Fair | Fair | |

The maize column is a placeholder: the PRD row was for green gram, which was swapped for maize (D-05).

| Tier | Yield multiplier | Your changes |
|---|---|---|
| Good | 1.00 | |
| Fair | 0.90 | |
| Marginal | 0.75 | |
| Not suitable | crop excluded | Should any cell above be "Not suitable"? |

## 2. Sowing windows and late sowing

| Crop | Latest usual sowing (used for the late-sowing rule) | Excluded if sown after mid-July? | Your changes |
|---|---|---|---|
| Tur | mid-August | No | |
| Maize | **to confirm** | No (until you confirm) | |
| Soybean | mid-July | **Yes** | |
| Cotton | mid-August | No | |

## 3. Harvest-marketing windows (from APMC arrival peaks, gap G5)

The app uses the average market price over these months as the "harvest price".

| Crop | Window used | Share of yearly arrivals in it | Your changes |
|---|---|---|---|
| Tur | Jan–Feb | 49% (December just below the cut-off) | |
| Maize | Oct–Jan | 68% | |
| Soybean | Oct–Nov | 57% | |
| Cotton (kapas) | Nov–Mar | 69% | |

## 4. Farm adjustments

| Rule | Current value | Question | Your answer |
|---|---|---|---|
| Protective irrigation (1–2 life-saving irrigations) | In the driest third of past seasons, a below-typical yield moves **halfway** (α = 0.5) toward the typical yield (D-21) | Is "halfway" reasonable for one or two irrigations? Should it differ by crop? | |
| Farmer's own yield | Replaces the soil multiplier; limited to **0.6–1.4 ×** the district five-season average | Is the range sensible? | |
| Assured irrigation | Shown with a notice; all results Low confidence | Agree? | |
| Cotton lint → kapas | Ginning outturn **0.34** (task 1.23 open) | Typical local outturn? | |
| Field occupancy flag | Tur and cotton "hold the field into winter: little room for a Rabi crop" | Agree? Should maize or soybean get a "leaves room for Rabi" note? | |
| Rotation flags | Same crop as last Kharif → carry-over warning; cotton after cotton → stronger warning | Any other rotation warnings? | |

## 5. Costs and prices

| Crop | Cost used (₹/acre, A2+FL, CACP Karnataka 2024-25 × 1.0927 for 3 years at 3%) | Your view for Kalyana-Karnataka 2027 |
|---|---|---|
| Tur | ₹20,042 | |
| Maize | ₹26,256 | |
| Soybean | ₹24,887 | |
| Cotton | ₹31,599 | |

Cost range in the simulations: −10% to +15% around these. **MSP 2026-27** (tur ₹8,450, maize ₹2,410, soybean ₹5,708, cotton ₹8,267 per quintal) is shown **for reference only, not as a price floor**, because procurement does not reach every farmer (G11). Agree?

## 6. Values the app needs from you (empty today)

- **Soil Health Card ranges** that should trigger a warning per crop (pH, EC, organic carbon, N, P, K).
- **Pest and disease notes** per crop for the region (one or two lines each); the app currently says "awaiting expert review".

## 7. Sample outputs to review (at least five)

Open `explanations_test_farms.md` (generated from the live app; Kannada version in `explanations_test_farms_kn.md`). Please review farms **F01, F02, F04, F05 and F09** at least, and note anything that looks wrong for a farmer in that district.

| Farm | Looks reasonable? | What looks wrong |
|---|---|---|
| F01 Kalaburagi, medium black, rain-fed | | |
| F02 Yadgir, deep black, protective irrigation, after tur | | |
| F04 Raichur, shallow black, waterlogs, after cotton | | |
| F05 Koppal, soil and drainage unknown | | |
| F09 Kalaburagi, own yield and cost entered | | |

## 8. Review note (AC-12)

> I reviewed the rules and sample outputs above. Every issue is either fixed in the table above or listed here as a known limitation:
>
> ______________________________________________
>
> Name: ____________ Organisation: ____________ Date: ________ Signature: ____________

After the session: apply the changes to `config/rules.json` (task 6.05), mark it "expert-reviewed (name, date)", rebuild and re-test (task 6.07, see `refresh_checklist.md` §3).
