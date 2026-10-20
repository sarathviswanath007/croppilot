# Polaris CropPilot: JS / Python Parity Test Log (tasks 3.35, 3.36)

**Run:** 20 October 2026 · engine_data.json v0.2 · 10 farms in `tests/test_farms.json` · 2,000 draws per crop

| Farm | District | Risk | Python ranking | JS ranking | Excluded | Result |
|---|---|---|---|---|---|---|
| F01 | Kalaburagi | balanced | cotton > tur > soybean > maize | cotton > tur > soybean > maize | — | PASS |
| F02 | Yadgir | cautious | tur > cotton > soybean > maize | tur > cotton > soybean > maize | — | PASS |
| F03 | Bidar | growth | tur > cotton > soybean > maize | tur > cotton > soybean > maize | — | PASS |
| F04 | Raichur | balanced | cotton > maize > tur | cotton > maize > tur | soybean | PASS |
| F05 | Koppal | cautious | tur > maize > cotton | tur > maize > cotton | soybean | PASS |
| F06 | Ballari | growth | cotton > tur > maize | cotton > tur > maize | soybean | PASS |
| F07 | Vijayanagara | balanced | cotton > tur > maize | cotton > tur > maize | soybean | PASS |
| F08 | Bidar | balanced | tur > cotton > maize | tur > cotton > maize | soybean | PASS |
| F09 | Kalaburagi | cautious | tur > soybean > cotton > maize | tur > soybean > cotton > maize | — | PASS |
| F10 | Raichur | growth | maize > cotton > tur | maize > cotton > tur | soybean | PASS |

**AC-06:** PASS: 10 of 10 farms match. Largest relative difference on any compared value: 3.10e-15 (limit 1%).

**NFR-03 timing (Node, this machine):** 12.1 ms per farm (4 crops × 2,000 draws), 121 ms for all 10. Limit 2 s.
