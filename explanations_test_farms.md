# Polaris CropPilot: Explanations for the 10 Test Farms (task 4.15)

Generated 2026-10-20 by `tests/ui_audit.js` from the live web app and `data/engine_data.json`. For the plain-language review (task 4.16). Test farms are invented profiles (`tests/test_farms.json`). All amounts are `[Prediction]` district-average estimates unless labelled otherwise.

## F01: Kalaburagi, 2 acres 20 guntas, medium_black soil, drainage drains_well, rainfed, last crop none, balanced

```
Ranks first for your farm
Cotton (kapas) ಹತ್ತಿ
In a typical year, cotton could leave you about ₹45,052 after costs on your 2.50 acres [Prediction]
Bad year (1 in 10 is worse): −₹8,454
Typical year (the middle): ₹45,052
Good year (1 in 10 is better): ₹1,41,082
Loses money in 15 of 100 seasons
Costs about ₹78,998 to grow
Medium confidence
- It earns the most in a typical year.
- It came out on top in the most past-weather seasons (49 in 100).
Per acre [Prediction]
Yield: 4.5–11.6 quintals kapas (typical 6.8)
Price: ₹5,648–₹8,695 per quintal (typical ₹7,451)
Cost: ₹31,599 [Assumption]
Break-even: ₹4,649 per quintal, or 4.24 quintals
MSP 2026-27: ₹8,267 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The yield estimate is the average of the last five published seasons in your district (to 2019-20), widened by how far that average has missed before.
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2011, 2017, 2004. Good-year cases: 2010, 2021, 1991.
Risks
- This yield estimate does not change with rainfall, so dry-year risk shows only in the bad-year figure.
- Harvest-time prices have swung by about 8% from season to season. [Data]
- Holds the field into winter: little room for a Rabi crop
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
Medium confidence Based on the 5-season district average, the method that tested best for this crop. In tests, the bad-to-good range held the actual yield 79% of the time.
Assumptions [Assumption]
- Good fit for your soil.
- Price: Expected harvest price = last season's harvest-time price, using market prices up to May 2025 (borrowed from nearby districts, as local prices were missing).
- Sold in Nov–Mar, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
- Cotton yield converted from lint to kapas at 34% ginning.
```

Choice summary (choosing the last-ranked crop):

```
CropPilot · Kharif 2027 · Kalaburagi · 2.50 acres
My choice: Maize
Estimated profit for the field: bad year −₹33,488, typical −₹1,505, good year ₹30,349.
Chance of losing money: 52 in 100 seasons. Low confidence.
CropPilot ranked Cotton first; this crop ranked 4.
These are district-average estimates from past seasons. The decision is mine; I plan to discuss it with my RSK or KVK.
```

Other crops:

```
How the other crops compare
Typical-year profit for your field, after costs [Prediction]
2. Tur (red gram) ತೊಗರಿ ₹35,047Bad year −₹4,116 · loses money in 14 of 100 seasons
3. Soybean ಸೋಯಾಬೀನ್ ₹5,612Bad year −₹32,972 · loses money in 43 of 100 seasons
4. Maize ಮೆಕ್ಕೆಜೋಳ −₹1,505Bad year −₹33,488 · loses money in 52 of 100 seasons
Per acre [Prediction]
Yield: 6.0–15.9 quintals (typical 10.7)
Price: ₹1,962–₹2,810 per quintal (typical ₹2,293)
Cost: ₹26,256 [Assumption]
Break-even: ₹2,465 per quintal, or 11.45 quintals
MSP 2026-27: ₹2,410 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The yield estimate is the average of the last five published seasons in your district (to 2019-20), widened by how far that average has missed before.
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2017, 2016, 1991. Good-year cases: 2018, 2012, 1998.
Risks
- This yield estimate does not change with rainfall, so dry-year risk shows only in the bad-year figure.
- Harvest-time prices have swung by about 22% from season to season. [Data]
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
Low confidence Based on the 5-season district average, the method that tested best for this crop. In tests, the bad-to-good range held the actual yield 47% of the time.
Assumptions [Assumption]
- Fair fit for your soil: yield reduced by 10%.
- Price: Expected harvest price = the May market price, using market prices up to May 2025 (borrowed from nearby districts, as local prices were missing).
- Sold in Oct–Jan, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
```

## F02: Yadgir, 5 acres 0 guntas, deep_black soil, drainage drains_well, protective, last crop tur, cautious

```
Ranks first for your farm
Tur (red gram) ತೊಗರಿ
In a typical year, tur could leave you about ₹76,263 after costs on your 5 acres [Prediction]
Bad year (1 in 10 is worse): −₹315
Typical year (the middle): ₹76,263
Good year (1 in 10 is better): ₹1,95,354
Loses money in 10 of 100 seasons
Costs about ₹1,00,210 to grow
High confidence
- It holds up best in a bad year.
- It has the lowest chance of losing money (10 in 100 seasons).
- It costs the least to grow.
Per acre [Prediction]
Yield: 3.0–7.0 quintals (typical 4.4)
Price: ₹5,669–₹9,996 per quintal (typical ₹7,865)
Cost: ₹20,042 [Assumption]
Break-even: ₹4,582 per quintal, or 2.55 quintals
MSP 2026-27: ₹8,450 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The long-run rise in yields (better seed and practice) raises the estimate (about 273 kg per hectare).
- June rain raises the estimate (about 23 kg per hectare).
- June–September rain raises the estimate (about 18 kg per hectare).
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2016, 2006, 2004. Good-year cases: 2020, 2025, 1995.
Risks
- In the driest third of past seasons, the typical yield is about 6% lower. [Prediction]
- Harvest-time prices have swung by about 29% from season to season. [Data]
- Same crop as last Kharif: pest and disease carry-over risk
- Holds the field into winter: little room for a Rabi crop
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
High confidence The yield model did 10% better than a simple 5-season average in tests, a small margin. In tests, the bad-to-good range held the actual yield 70% of the time.
Assumptions [Assumption]
- Good fit for your soil.
- Price: Expected harvest price = last season's harvest-time price, using market prices up to May 2025.
- Sold in Jan–Feb, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
- Saving irrigations lift the driest seasons halfway to a typical yield.
```

Choice summary (choosing the last-ranked crop):

```
CropPilot · Kharif 2027 · Yadgir · 5 acres
My choice: Maize
Estimated profit for the field: bad year −₹57,038, typical −₹1,575, good year ₹61,178.
Chance of losing money: 51 in 100 seasons. Low confidence.
CropPilot ranked Tur first; this crop ranked 4.
These are district-average estimates from past seasons. The decision is mine; I plan to discuss it with my RSK or KVK.
```

Other crops:

```
How the other crops compare
Typical-year profit for your field, after costs [Prediction]
2. Cotton (kapas) ಹತ್ತಿ ₹94,161Bad year −₹5,131 · loses money in 11 of 100 seasons
3. Soybean ಸೋಯಾಬೀನ್ ₹12,891Bad year −₹54,692 · loses money in 41 of 100 seasons
4. Maize ಮೆಕ್ಕೆಜೋಳ −₹1,575Bad year −₹57,038 · loses money in 51 of 100 seasons
Per acre [Prediction]
Yield: 7.2–15.9 quintals (typical 10.7)
Price: ₹1,962–₹2,810 per quintal (typical ₹2,293)
Cost: ₹26,256 [Assumption]
Break-even: ₹2,465 per quintal, or 11.45 quintals
MSP 2026-27: ₹2,410 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The yield estimate is the average of the last five published seasons in your district (to 2019-20), widened by how far that average has missed before.
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2017, 2005, 2016. Good-year cases: 2018, 2012, 1998.
Risks
- This yield estimate does not change with rainfall, so dry-year risk shows only in the bad-year figure.
- Harvest-time prices have swung by about 22% from season to season. [Data]
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
Low confidence Based on the 5-season district average, the method that tested best for this crop. In tests, the bad-to-good range held the actual yield 47% of the time.
Assumptions [Assumption]
- Fair fit for your soil: yield reduced by 10%.
- Price: Expected harvest price = the May market price, using market prices up to May 2025 (borrowed from nearby districts, as local prices were missing).
- Sold in Oct–Jan, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
- Saving irrigations lift the driest seasons halfway to a typical yield.
```

## F03: Bidar, 1 acres 10 guntas, red soil, drainage drains_well, rainfed, last crop soybean, growth

```
Ranks first for your farm
Tur (red gram) ತೊಗರಿ
In a typical year, tur could leave you about ₹16,682 after costs on your 1.25 acres [Prediction]
Bad year (1 in 10 is worse): −₹3,252
Typical year (the middle): ₹16,682
Good year (1 in 10 is better): ₹46,798
Loses money in 16 of 100 seasons
Costs about ₹25,053 to grow
High confidence
- It earns the most in a typical year.
- It holds up best in a bad year.
- It has the lowest chance of losing money (16 in 100 seasons).
Per acre [Prediction]
Yield: 2.6–7.1 quintals (typical 4.4)
Price: ₹5,438–₹9,831 per quintal (typical ₹7,675)
Cost: ₹20,042 [Assumption]
Break-even: ₹4,528 per quintal, or 2.61 quintals
MSP 2026-27: ₹8,450 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The long-run rise in yields (better seed and practice) raises the estimate (about 273 kg per hectare).
- June rain raises the estimate (about 23 kg per hectare).
- June–September rain raises the estimate (about 18 kg per hectare).
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2016, 2018, 1999. Good-year cases: 2020, 2025, 1996.
Risks
- In the driest third of past seasons, the typical yield is about 10% lower. [Prediction]
- Harvest-time prices have swung by about 28% from season to season. [Data]
- Holds the field into winter: little room for a Rabi crop
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
High confidence The yield model did 10% better than a simple 5-season average in tests, a small margin. In tests, the bad-to-good range held the actual yield 70% of the time.
Assumptions [Assumption]
- Fair fit for your soil: yield reduced by 10%.
- Price: Expected harvest price = last season's harvest-time price, using market prices up to May 2025.
- Sold in Jan–Feb, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
```

Choice summary (choosing the last-ranked crop):

```
CropPilot · Kharif 2027 · Bidar · 1.25 acres
My choice: Maize
Estimated profit for the field: bad year −₹20,504, typical −₹7,920, good year ₹4,642.
Chance of losing money: 79 in 100 seasons. Low confidence.
CropPilot ranked Tur first; this crop ranked 4.
These are district-average estimates from past seasons. The decision is mine; I plan to discuss it with my RSK or KVK.
```

Other crops:

```
How the other crops compare
Typical-year profit for your field, after costs [Prediction]
2. Cotton (kapas) ಹತ್ತಿ −₹1,939Bad year −₹18,563 · loses money in 56 of 100 seasons
3. Soybean ಸೋಯಾಬೀನ್ −₹6,242Bad year −₹20,772 · loses money in 68 of 100 seasons
4. Maize ಮೆಕ್ಕೆಜೋಳ −₹7,920Bad year −₹20,504 · loses money in 79 of 100 seasons
Per acre [Prediction]
Yield: 4.7–12.4 quintals (typical 8.3)
Price: ₹1,962–₹2,810 per quintal (typical ₹2,293)
Cost: ₹26,256 [Assumption]
Break-even: ₹3,155 per quintal, or 11.45 quintals
MSP 2026-27: ₹2,410 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The yield estimate is the average of the last five published seasons in your district (to 2019-20), widened by how far that average has missed before.
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2017, 2016, 1991. Good-year cases: 2018, 2012, 2023.
Risks
- This yield estimate does not change with rainfall, so dry-year risk shows only in the bad-year figure.
- Harvest-time prices have swung by about 15% from season to season. [Data]
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
Low confidence Based on the 5-season district average, the method that tested best for this crop. In tests, the bad-to-good range held the actual yield 47% of the time.
Assumptions [Assumption]
- Fair fit for your soil: yield reduced by 10%.
- Price: Expected harvest price = the May market price, using market prices up to May 2025 (borrowed from nearby districts, as local prices were missing).
- Sold in Oct–Jan, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
```

## F04: Raichur, 3 acres 0 guntas, shallow_black soil, drainage waterlogs, rainfed, last crop cotton, balanced

```
Ranks first for your farm
Cotton (kapas) ಹತ್ತಿ
In a typical year, cotton could leave you about ₹32,863 after costs on your 3 acres [Prediction]
Bad year (1 in 10 is worse): −₹21,481
Typical year (the middle): ₹32,863
Good year (1 in 10 is better): ₹1,33,285
Loses money in 23 of 100 seasons
Costs about ₹94,797 to grow
Medium confidence
- It earns the most in a typical year.
- It holds up best in a bad year.
- It has the lowest chance of losing money (23 in 100 seasons).
Per acre [Prediction]
Yield: 3.8–9.8 quintals kapas (typical 5.8)
Price: ₹5,872–₹8,832 per quintal (typical ₹7,509)
Cost: ₹31,599 [Assumption]
Break-even: ₹5,475 per quintal, or 4.21 quintals
MSP 2026-27: ₹8,267 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The yield estimate is the average of the last five published seasons in your district (to 2019-20), widened by how far that average has missed before.
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2011, 2004, 2017. Good-year cases: 2010, 2021, 2000.
Risks
- This yield estimate does not change with rainfall, so dry-year risk shows only in the bad-year figure.
- Harvest-time prices have swung by about 26% from season to season. [Data]
- Cotton after cotton: stronger pest and disease carry-over risk
- Holds the field into winter: little room for a Rabi crop
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
Medium confidence Based on the 5-season district average, the method that tested best for this crop. In tests, the bad-to-good range held the actual yield 79% of the time.
Assumptions [Assumption]
- Fair fit for your soil: yield reduced by 10%.
- Price: Expected harvest price = last season's harvest-time price, using market prices up to May 2025.
- Sold in Nov–Mar, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
- Cotton yield converted from lint to kapas at 34% ginning.
```

Choice summary (choosing the last-ranked crop):

```
CropPilot · Kharif 2027 · Raichur · 3 acres
My choice: Tur (red gram)
Estimated profit for the field: bad year −₹23,739, typical ₹5,419, good year ₹52,817.
Chance of losing money: 42 in 100 seasons. High confidence.
CropPilot ranked Cotton first; this crop ranked 3.
These are district-average estimates from past seasons. The decision is mine; I plan to discuss it with my RSK or KVK.
```

Other crops:

```
How the other crops compare
Typical-year profit for your field, after costs [Prediction]
2. Maize ಮೆಕ್ಕೆಜೋಳ ₹21,229Bad year −₹27,117 · loses money in 29 of 100 seasons
3. Tur (red gram) ತೊಗರಿ ₹5,419Bad year −₹23,739 · loses money in 42 of 100 seasons
Per acre [Prediction]
Yield: 1.7–4.5 quintals (typical 2.8)
Price: ₹6,462–₹10,098 per quintal (typical ₹8,363)
Cost: ₹20,042 [Assumption]
Break-even: ₹7,149 per quintal, or 2.40 quintals
MSP 2026-27: ₹8,450 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The long-run rise in yields (better seed and practice) raises the estimate (about 273 kg per hectare).
- June rain raises the estimate (about 23 kg per hectare).
- June–September rain raises the estimate (about 18 kg per hectare).
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2016, 2011, 2004. Good-year cases: 2008, 2020, 2014.
Risks
- In the driest third of past seasons, the typical yield is about 12% lower. [Prediction]
- Harvest-time prices have swung by about 29% from season to season. [Data]
- Holds the field into winter: little room for a Rabi crop
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
High confidence The yield model did 10% better than a simple 5-season average in tests, a small margin. In tests, the bad-to-good range held the actual yield 70% of the time.
Assumptions [Assumption]
- Marginal fit for your soil: yield reduced by 25%.
- Price: Expected harvest price = last season's harvest-time price, using market prices up to May 2025.
- Sold in Jan–Feb, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
```

```
Not compared: [Data]
- Soybean: Not enough local data: 0 seasons with at least 500 ha (needs 10).
```

## F05: Koppal, 0 acres 30 guntas, unknown soil, drainage unknown, rainfed, last crop maize, cautious

```
Ranks first for your farm
Tur (red gram) ತೊಗರಿ
In a typical year, tur could leave you about −₹751 after costs on your 0.75 acres [Prediction]
Bad year (1 in 10 is worse): −₹7,783
Typical year (the middle): −₹751
Good year (1 in 10 is better): ₹11,674
Loses money in 54 of 100 seasons
Costs about ₹15,032 to grow
Low confidence
- It earns the most in a typical year.
- It holds up best in a bad year.
- It has the lowest chance of losing money (54 in 100 seasons).
Per acre [Prediction]
Yield: 1.4–4.2 quintals (typical 2.5)
Price: ₹6,484–₹10,114 per quintal (typical ₹7,761)
Cost: ₹20,042 [Assumption]
Break-even: ₹8,157 per quintal, or 2.58 quintals
MSP 2026-27: ₹8,450 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The long-run rise in yields (better seed and practice) raises the estimate (about 273 kg per hectare).
- June rain raises the estimate (about 23 kg per hectare).
- June–September rain raises the estimate (about 18 kg per hectare).
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2016, 2018, 2019. Good-year cases: 2020, 2007, 2022.
Risks
- In the driest third of past seasons, the typical yield is about 8% lower. [Prediction]
- Harvest-time prices have swung by about 31% from season to season. [Data]
- Holds the field into winter: little room for a Rabi crop
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
Low confidence Low, because soil and drainage are both unknown.
Assumptions [Assumption]
- Fair fit for your soil: yield reduced by 10%.
- Price: Expected harvest price = last season's harvest-time price, using market prices up to May 2025.
- Sold in Jan–Feb, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
```

Choice summary (choosing the last-ranked crop):

```
CropPilot · Kharif 2027 · Koppal · 0.75 acres
My choice: Cotton (kapas)
Estimated profit for the field: bad year −₹14,634, typical −₹7,118, good year ₹5,672.
Chance of losing money: 80 in 100 seasons. Low confidence.
CropPilot ranked Tur first; this crop ranked 3.
These are district-average estimates from past seasons. The decision is mine; I plan to discuss it with my RSK or KVK.
```

Other crops:

```
How the other crops compare
Typical-year profit for your field, after costs [Prediction]
2. Maize ಮೆಕ್ಕೆಜೋಳ −₹6,672Bad year −₹13,405 · loses money in 90 of 100 seasons
3. Cotton (kapas) ಹತ್ತಿ −₹7,118Bad year −₹14,634 · loses money in 80 of 100 seasons
Per acre [Prediction]
Yield: 2.1–5.3 quintals kapas (typical 3.1)
Price: ₹5,547–₹8,541 per quintal (typical ₹7,319)
Cost: ₹31,599 [Assumption]
Break-even: ₹10,137 per quintal, or 4.32 quintals
MSP 2026-27: ₹8,267 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The yield estimate is the average of the last five published seasons in your district (to 2019-20), widened by how far that average has missed before.
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2004, 2011, 2017. Good-year cases: 2010, 2021, 2013.
Risks
- This yield estimate does not change with rainfall, so dry-year risk shows only in the bad-year figure.
- Harvest-time prices have swung by about 26% from season to season. [Data]
- Holds the field into winter: little room for a Rabi crop
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
Low confidence Low, because soil and drainage are both unknown.
Assumptions [Assumption]
- Fair fit for your soil: yield reduced by 10%.
- Price: Expected harvest price = last season's harvest-time price, using market prices up to May 2025.
- Sold in Nov–Mar, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
- Cotton yield converted from lint to kapas at 34% ginning.
```

```
Not compared: [Data]
- Soybean: Not enough local data: 0 seasons with at least 500 ha (needs 10).
```

## F06: Ballari, 4 acres 20 guntas, deep_black soil, drainage drains_well, assured, last crop other, growth

```
Ranks first for your farm
Cotton (kapas) ಹತ್ತಿ
In a typical year, cotton could leave you about ₹80,853 after costs on your 4.50 acres [Prediction]
Bad year (1 in 10 is worse): −₹15,337
Typical year (the middle): ₹80,853
Good year (1 in 10 is better): ₹2,53,540
Loses money in 15 of 100 seasons
Costs about ₹1,42,196 to grow
Low confidence
- It earns the most in a typical year.
- It holds up best in a bad year.
- It has the lowest chance of losing money (15 in 100 seasons).
Per acre [Prediction]
Yield: 4.5–11.6 quintals kapas (typical 6.8)
Price: ₹5,648–₹8,695 per quintal (typical ₹7,451)
Cost: ₹31,599 [Assumption]
Break-even: ₹4,654 per quintal, or 4.24 quintals
MSP 2026-27: ₹8,267 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The yield estimate is the average of the last five published seasons in your district (to 2019-20), widened by how far that average has missed before.
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2011, 2017, 2004. Good-year cases: 2010, 2021, 1991.
Risks
- This yield estimate does not change with rainfall, so dry-year risk shows only in the bad-year figure.
- Harvest-time prices have swung by about 21% from season to season. [Data]
- Holds the field into winter: little room for a Rabi crop
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
Low confidence Low, because the models describe rain-fed farming.
Assumptions [Assumption]
- Good fit for your soil.
- Price: Expected harvest price = last season's harvest-time price, using market prices up to May 2025 (borrowed from nearby districts, as local prices were missing).
- Sold in Nov–Mar, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
- Cotton yield converted from lint to kapas at 34% ginning.
```

Choice summary (choosing the last-ranked crop):

```
CropPilot · Kharif 2027 · Ballari · 4.50 acres
My choice: Maize
Estimated profit for the field: bad year −₹55,907, typical ₹9,181, good year ₹70,058.
Chance of losing money: 43 in 100 seasons. Low confidence.
CropPilot ranked Cotton first; this crop ranked 3.
These are district-average estimates from past seasons. The decision is mine; I plan to discuss it with my RSK or KVK.
```

Other crops:

```
How the other crops compare
Typical-year profit for your field, after costs [Prediction]
2. Tur (red gram) ತೊಗರಿ ₹33,420Bad year −₹23,223 · loses money in 25 of 100 seasons
3. Maize ಮೆಕ್ಕೆಜೋಳ ₹9,181Bad year −₹55,907 · loses money in 43 of 100 seasons
Per acre [Prediction]
Yield: 6.7–17.6 quintals (typical 11.8)
Price: ₹1,898–₹2,683 per quintal (typical ₹2,246)
Cost: ₹26,256 [Assumption]
Break-even: ₹2,225 per quintal, or 11.69 quintals
MSP 2026-27: ₹2,410 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The yield estimate is the average of the last five published seasons in your district (to 2019-20), widened by how far that average has missed before.
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2013, 2017, 1994. Good-year cases: 2018, 2012, 2015.
Risks
- This yield estimate does not change with rainfall, so dry-year risk shows only in the bad-year figure.
- Harvest-time prices have swung by about 18% from season to season. [Data]
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
Low confidence Low, because the models describe rain-fed farming.
Assumptions [Assumption]
- Fair fit for your soil: yield reduced by 10%.
- Price: Expected harvest price = the May market price, using market prices up to May 2025.
- Sold in Oct–Jan, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
```

```
Not compared: [Data]
- Soybean: Not enough local data: 0 seasons with at least 500 ha (needs 10).
```

## F07: Vijayanagara, 2 acres 0 guntas, red soil, drainage unknown, protective, last crop none, balanced

```
Ranks first for your farm
Cotton (kapas) ಹತ್ತಿ
In a typical year, cotton could leave you about ₹27,372 after costs on your 2 acres [Prediction]
Bad year (1 in 10 is worse): −₹8,510
Typical year (the middle): ₹27,372
Good year (1 in 10 is better): ₹94,642
Loses money in 17 of 100 seasons
Costs about ₹63,198 to grow
Medium confidence
- It earns the most in a typical year.
- It holds up best in a bad year.
- It has the lowest chance of losing money (17 in 100 seasons).
Per acre [Prediction]
Yield: 4.4–10.4 quintals kapas (typical 6.1)
Price: ₹5,648–₹8,695 per quintal (typical ₹7,451)
Cost: ₹31,599 [Assumption]
Break-even: ₹5,171 per quintal, or 4.24 quintals
MSP 2026-27: ₹8,267 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The yield estimate is the average of the last five published seasons in your district (to 2019-20), widened by how far that average has missed before.
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2004, 2017, 2008. Good-year cases: 2010, 2021, 1991.
Risks
- This yield estimate does not change with rainfall, so dry-year risk shows only in the bad-year figure.
- Harvest-time prices have swung by about 21% from season to season. [Data]
- Holds the field into winter: little room for a Rabi crop
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
Medium confidence Based on the 5-season district average, the method that tested best for this crop. In tests, the bad-to-good range held the actual yield 79% of the time.
Assumptions [Assumption]
- Fair fit for your soil: yield reduced by 10%.
- Price: Expected harvest price = last season's harvest-time price, using market prices up to May 2025 (borrowed from nearby districts, as local prices were missing).
- Sold in Nov–Mar, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
- Cotton yield converted from lint to kapas at 34% ginning.
- Saving irrigations lift the driest seasons halfway to a typical yield.
```

Choice summary (choosing the last-ranked crop):

```
CropPilot · Kharif 2027 · Vijayanagara · 2 acres
My choice: Maize
Estimated profit for the field: bad year −₹19,937, typical ₹4,696, good year ₹31,137.
Chance of losing money: 41 in 100 seasons. Low confidence.
CropPilot ranked Cotton first; this crop ranked 3.
These are district-average estimates from past seasons. The decision is mine; I plan to discuss it with my RSK or KVK.
```

Other crops:

```
How the other crops compare
Typical-year profit for your field, after costs [Prediction]
2. Tur (red gram) ತೊಗರಿ ₹10,985Bad year −₹11,661 · loses money in 28 of 100 seasons
3. Maize ಮೆಕ್ಕೆಜೋಳ ₹4,696Bad year −₹19,937 · loses money in 41 of 100 seasons
Per acre [Prediction]
Yield: 8.0–17.6 quintals (typical 11.8)
Price: ₹1,898–₹2,683 per quintal (typical ₹2,246)
Cost: ₹26,256 [Assumption]
Break-even: ₹2,225 per quintal, or 11.69 quintals
MSP 2026-27: ₹2,410 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The yield estimate is the average of the last five published seasons in your district (to 2019-20), widened by how far that average has missed before.
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 1995, 2013, 2017. Good-year cases: 2018, 2012, 2015.
Risks
- This yield estimate does not change with rainfall, so dry-year risk shows only in the bad-year figure.
- Harvest-time prices have swung by about 18% from season to season. [Data]
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
Low confidence Based on the 5-season district average, the method that tested best for this crop. In tests, the bad-to-good range held the actual yield 47% of the time.
Assumptions [Assumption]
- Fair fit for your soil: yield reduced by 10%.
- Price: Expected harvest price = the May market price, using market prices up to May 2025.
- Sold in Oct–Jan, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
- Saving irrigations lift the driest seasons halfway to a typical yield.
```

```
Not compared: [Data]
- Soybean: Not enough local data: 0 seasons with at least 500 ha (needs 10).
```

## F08: Bidar, 6 acres 0 guntas, medium_black soil, drainage drains_well, rainfed, last crop none, balanced, late sowing

```
Ranks first for your farm
Tur (red gram) ತೊಗರಿ
In a typical year, tur could leave you about ₹1,02,849 after costs on your 6 acres [Prediction]
Bad year (1 in 10 is worse): −₹3,360
Typical year (the middle): ₹1,02,849
Good year (1 in 10 is better): ₹2,63,259
Loses money in 11 of 100 seasons
Costs about ₹1,20,252 to grow
High confidence
- It earns the most in a typical year.
- It holds up best in a bad year.
- It has the lowest chance of losing money (11 in 100 seasons).
Per acre [Prediction]
Yield: 2.9–7.8 quintals (typical 4.9)
Price: ₹5,438–₹9,831 per quintal (typical ₹7,675)
Cost: ₹20,042 [Assumption]
Break-even: ₹4,075 per quintal, or 2.61 quintals
MSP 2026-27: ₹8,450 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The long-run rise in yields (better seed and practice) raises the estimate (about 273 kg per hectare).
- June rain raises the estimate (about 23 kg per hectare).
- June–September rain raises the estimate (about 18 kg per hectare).
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2016, 2018, 1999. Good-year cases: 2020, 2025, 1996.
Risks
- In the driest third of past seasons, the typical yield is about 10% lower. [Prediction]
- Harvest-time prices have swung by about 28% from season to season. [Data]
- Holds the field into winter: little room for a Rabi crop
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
High confidence The yield model did 10% better than a simple 5-season average in tests, a small margin. In tests, the bad-to-good range held the actual yield 70% of the time.
Assumptions [Assumption]
- Good fit for your soil.
- Price: Expected harvest price = last season's harvest-time price, using market prices up to May 2025.
- Sold in Jan–Feb, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
```

Choice summary (choosing the last-ranked crop):

```
CropPilot · Kharif 2027 · Bidar · 6 acres
My choice: Maize
Estimated profit for the field: bad year −₹98,419, typical −₹38,014, good year ₹22,281.
Chance of losing money: 79 in 100 seasons. Low confidence.
CropPilot ranked Tur first; this crop ranked 3.
These are district-average estimates from past seasons. The decision is mine; I plan to discuss it with my RSK or KVK.
```

Other crops:

```
How the other crops compare
Typical-year profit for your field, after costs [Prediction]
2. Cotton (kapas) ಹತ್ತಿ ₹10,506Bad year −₹77,391 · loses money in 45 of 100 seasons
3. Maize ಮೆಕ್ಕೆಜೋಳ −₹38,014Bad year −₹98,419 · loses money in 79 of 100 seasons
Per acre [Prediction]
Yield: 4.7–12.4 quintals (typical 8.3)
Price: ₹1,962–₹2,810 per quintal (typical ₹2,293)
Cost: ₹26,256 [Assumption]
Break-even: ₹3,155 per quintal, or 11.45 quintals
MSP 2026-27: ₹2,410 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The yield estimate is the average of the last five published seasons in your district (to 2019-20), widened by how far that average has missed before.
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2017, 2016, 1991. Good-year cases: 2018, 2012, 2023.
Risks
- This yield estimate does not change with rainfall, so dry-year risk shows only in the bad-year figure.
- Harvest-time prices have swung by about 15% from season to season. [Data]
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
Low confidence Based on the 5-season district average, the method that tested best for this crop. In tests, the bad-to-good range held the actual yield 47% of the time.
Assumptions [Assumption]
- Fair fit for your soil: yield reduced by 10%.
- Price: Expected harvest price = the May market price, using market prices up to May 2025 (borrowed from nearby districts, as local prices were missing).
- Sold in Oct–Jan, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
```

```
Not compared: [Data]
- Soybean: Late sowing (after mid-July) is outside the usual window for this crop.
```

## F09: Kalaburagi, 3 acres 15 guntas, deep_black soil, drainage drains_well, rainfed, last crop tur, cautious, own numbers entered

```
Ranks first for your farm
Tur (red gram) ತೊಗರಿ
In a typical year, tur could leave you about ₹1,02,015 after costs on your 3.38 acres [Prediction]
Bad year (1 in 10 is worse): ₹29,734
Typical year (the middle): ₹1,02,015
Good year (1 in 10 is better): ₹2,20,730
Loses money in 3 of 100 seasons
Costs about ₹60,750 to grow
High confidence
- It earns the most in a typical year.
- It holds up best in a bad year.
- It has the lowest chance of losing money (3 in 100 seasons).
Per acre [Prediction]
Yield: 3.7–9.9 quintals (typical 6.1)
Price: ₹5,669–₹9,996 per quintal (typical ₹7,865)
Cost: ₹18,000 [Your number]
Break-even: ₹2,939 per quintal, or 2.29 quintals
MSP 2026-27: ₹8,450 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The long-run rise in yields (better seed and practice) raises the estimate (about 273 kg per hectare).
- June rain raises the estimate (about 23 kg per hectare).
- June–September rain raises the estimate (about 18 kg per hectare).
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2016, 1992, 1999. Good-year cases: 2020, 2025, 1995.
Risks
- In the driest third of past seasons, the typical yield is about 13% lower. [Prediction]
- Harvest-time prices have swung by about 29% from season to season. [Data]
- Same crop as last Kharif: pest and disease carry-over risk
- Holds the field into winter: little room for a Rabi crop
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
High confidence The yield model did 10% better than a simple 5-season average in tests, a small margin. In tests, the bad-to-good range held the actual yield 70% of the time.
Assumptions [Assumption]
- Adjusted to your own yield (limited to 0.6–1.4 times the district average). [Your number]
- Price: Expected harvest price = last season's harvest-time price, using market prices up to May 2025.
- Sold in Jan–Feb, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
```

Choice summary (choosing the last-ranked crop):

```
CropPilot · Kharif 2027 · Kalaburagi · 3.38 acres
My choice: Maize
Estimated profit for the field: bad year −₹45,208, typical −₹2,032, good year ₹40,970.
Chance of losing money: 52 in 100 seasons. Low confidence.
CropPilot ranked Tur first; this crop ranked 3.
These are district-average estimates from past seasons. The decision is mine; I plan to discuss it with my RSK or KVK.
```

Other crops:

```
How the other crops compare
Typical-year profit for your field, after costs [Prediction]
2. Cotton (kapas) ಹತ್ತಿ ₹4,488Bad year −₹44,399 · loses money in 46 of 100 seasons
3. Maize ಮೆಕ್ಕೆಜೋಳ −₹2,032Bad year −₹45,208 · loses money in 52 of 100 seasons
Per acre [Prediction]
Yield: 6.0–15.9 quintals (typical 10.7)
Price: ₹1,962–₹2,810 per quintal (typical ₹2,293)
Cost: ₹26,256 [Assumption]
Break-even: ₹2,465 per quintal, or 11.45 quintals
MSP 2026-27: ₹2,410 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The yield estimate is the average of the last five published seasons in your district (to 2019-20), widened by how far that average has missed before.
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2017, 2016, 1991. Good-year cases: 2018, 2012, 1998.
Risks
- This yield estimate does not change with rainfall, so dry-year risk shows only in the bad-year figure.
- Harvest-time prices have swung by about 22% from season to season. [Data]
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
Low confidence Based on the 5-season district average, the method that tested best for this crop. In tests, the bad-to-good range held the actual yield 47% of the time.
Assumptions [Assumption]
- Fair fit for your soil: yield reduced by 10%.
- Price: Expected harvest price = the May market price, using market prices up to May 2025 (borrowed from nearby districts, as local prices were missing).
- Sold in Oct–Jan, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
```

```
Not compared: [Data]
- Soybean: Late sowing (after mid-July) is outside the usual window for this crop.
```

## F10: Raichur, 1 acres 0 guntas, medium_black soil, drainage drains_well, rainfed, last crop maize, growth, own numbers entered

```
Ranks first for your farm
Maize ಮೆಕ್ಕೆಜೋಳ
In a typical year, maize could leave you about ₹24,525 after costs on your 1 acre [Prediction]
Bad year (1 in 10 is worse): ₹362
Typical year (the middle): ₹24,525
Good year (1 in 10 is better): ₹48,358
Loses money in 10 of 100 seasons
Costs about ₹26,256 to grow
Low confidence
- It earns the most in a typical year.
- It holds up best in a bad year.
- It has the lowest chance of losing money (10 in 100 seasons).
Per acre [Prediction]
Yield: 9.5–25.1 quintals (typical 16.8)
Price: ₹2,513–₹3,515 per quintal (typical ₹2,731)
Cost: ₹26,256 [Assumption]
Break-even: ₹1,559 per quintal, or 9.61 quintals
MSP 2026-27: ₹2,410 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The yield estimate is the average of the last five published seasons in your district (to 2019-20), widened by how far that average has missed before.
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 1995, 1997, 1994. Good-year cases: 2018, 1998, 2013.
Risks
- This yield estimate does not change with rainfall, so dry-year risk shows only in the bad-year figure.
- Harvest-time prices have swung by about 26% from season to season. [Data]
- Same crop as last Kharif: pest and disease carry-over risk
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
Low confidence Based on the 5-season district average, the method that tested best for this crop. In tests, the bad-to-good range held the actual yield 47% of the time.
Assumptions [Assumption]
- Fair fit for your soil: yield reduced by 10%.
- Price: your price [Your number].
- Sold in Oct–Jan, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
```

Choice summary (choosing the last-ranked crop):

```
CropPilot · Kharif 2027 · Raichur · 1 acre
My choice: Tur (red gram)
Estimated profit for the field: bad year −₹3,689, typical ₹9,173, good year ₹30,482.
Chance of losing money: 20 in 100 seasons. High confidence.
CropPilot ranked Maize first; this crop ranked 3.
These are district-average estimates from past seasons. The decision is mine; I plan to discuss it with my RSK or KVK.
```

Other crops:

```
How the other crops compare
Typical-year profit for your field, after costs [Prediction]
2. Cotton (kapas) ಹತ್ತಿ ₹12,049Bad year −₹6,608 · loses money in 21 of 100 seasons
3. Tur (red gram) ತೊಗರಿ ₹9,173Bad year −₹3,689 · loses money in 20 of 100 seasons
Per acre [Prediction]
Yield: 2.2–5.9 quintals (typical 3.7)
Price: ₹6,462–₹10,098 per quintal (typical ₹8,363)
Cost: ₹20,042 [Assumption]
Break-even: ₹5,362 per quintal, or 2.40 quintals
MSP 2026-27: ₹8,450 per quintal [Data] for reference, not a floor
What moves the yield [Prediction]
- The long-run rise in yields (better seed and practice) raises the estimate (about 273 kg per hectare).
- June rain raises the estimate (about 23 kg per hectare).
- June–September rain raises the estimate (about 18 kg per hectare).
Past seasons behind the numbers [Data]
Bad-year cases mostly use the weather of 2016, 2011, 2004. Good-year cases: 2008, 2014, 2020.
Risks
- In the driest third of past seasons, the typical yield is about 12% lower. [Prediction]
- Harvest-time prices have swung by about 29% from season to season. [Data]
- Holds the field into winter: little room for a Rabi crop
- Pest and disease notes are awaiting expert review.
How reliable [Prediction]
High confidence The yield model did 10% better than a simple 5-season average in tests, a small margin. In tests, the bad-to-good range held the actual yield 70% of the time.
Assumptions [Assumption]
- Good fit for your soil.
- Price: Expected harvest price = last season's harvest-time price, using market prices up to May 2025.
- Sold in Jan–Feb, when most of it reaches the market.
- Cost: Karnataka average 2024-25 (CACP), raised 3% a year.
```

```
Not compared: [Data]
- Soybean: Not enough local data: 0 seasons with at least 500 ha (needs 10).
```

