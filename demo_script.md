# Polaris CropPilot: Demo Script (task 6.13)

**Length:** about 8 minutes. **Setup:** the deployed link open in a browser, English first, on the welcome page. Numbers quoted below come from the current build (20 Oct 2026); re-check them after any data refresh.

## 1. The problem (30 s)

"In Kalyana-Karnataka, a rain-fed farmer must choose a Kharif crop in late May without knowing the rain or the harvest price. CropPilot puts four common crops (tur, maize, soybean and cotton) side by side and shows what each could earn in a bad, typical and good year. It never makes the choice for the farmer."

## 2. One farm end to end (2 min)

Tap **Start**. Enter: **Kalaburagi · 2 acres · medium black · drains well · rain only · last crop none · Middle path · not late**.

- Results open with one sentence: in a typical year, cotton could leave about ₹36,000 after costs on 2 acres. Read the bad / typical / good bars aloud.
- Point at the **labels**: every amount is marked Prediction, Data, Assumption or Your number.
- Open **See yield, price and cost details**: price assumption (last season's harvest price), MSP shown for reference only, the past seasons behind the bad and good cases.

## 3. Risk preference changes the ranking (1 min)

Tap the **Middle path ✎** chip and choose **Play safe**. Tur now ranks first: it has a smaller loss in a bad year (about −₹1,600 vs −₹3,400 per acre). "Same data, different priorities: the farmer's own risk tolerance changes the answer."

## 4. A close call (45 s)

Change soil to **Red** (tap the soil chip). Cotton and tur both show **Close call**: they come out on top in similar shares of past-weather seasons. "When it is close, we say so rather than pretend."

## 5. Kannada (30 s)

Tap **ಕನ್ನಡ** in the header. The whole flow switches, with answers kept. "Draft translation, pending a native-speaker check."

## 6. How good are the models? Including where they lose (2 min)

Open **About the data**:

- **Yield:** only tur's machine-learning model beat the simple 5-season average (by 10%, and that gain is uncertain). For maize, soybean and cotton, the app uses the simple average, because the rule fixed before testing said so.
- **Price:** only soybean's model passed the rule; the other crops use simple rules (last season's harvest price, or the May price).
- **Decision backtest 2012–2019** (`decision_backtest.md`): CropPilot's pick beat "always grow tur" (picked the best crop in 78% of district-seasons vs 43%), but was only level with "grow last season's most profitable crop" (76%).

"We report every crop, including where the baseline won."

## 7. Expert adjustment (45 s)

Show `expert_pack.md` / the signed review note: which rules the expert changed (soil tiers, sowing windows, protective-irrigation effect), and that `config/rules.json` now says "expert-reviewed (name, date)". *(Fill in after the Phase 6 session.)*

## 8. Close (15 s)

Back on the results, choose a crop that is **not** first under **Your choice**: the summary says the decision is the farmer's and suggests discussing it with the RSK or KVK.
