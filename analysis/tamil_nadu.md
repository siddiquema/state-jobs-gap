# Tamil Nadu through the same analysis

Run 2026-11-05. Code: `analysis/build_state_summary.py`, `scripts/extract_plfs_city_rows.py`. Data: `data/tamil_nadu_summary.csv`, `data/tamil_nadu_cities.csv`.
Method, sources and caveats as in `west_bengal_summary.md` and `pressure_test.md`. West Bengal is shown alongside for comparison.

## Formal entrants (EPFO net payroll 18-25) per undergraduate pass-out, 2019-20 to 2023-24

| | West Bengal | Tamil Nadu |
|---|---|---|
| UG pass-outs, five years | 1,885,522 | 3,178,889 |
| EPFO net payroll 18-25, five years | 890,027 | 3,049,437 |
| A. Baseline ratio | 0.47 | **0.96** |
| B. Ages 22-25 only | 0.26 | **0.44** |
| C. One-year lag | 0.51 | **1.01** |
| D. Pass-outs in the labour force | 0.76 | **1.51** |
| UG pass-outs per 100 youth (2023-24) | 3.5 | 9.1 |
| Formal entrants per 100 youth (2023-24) | 2.1 | 9.7 |
| Women's share of UG pass-outs | 52% | 55% |
| Graduate labour-force participation, men / women (%) | 85.7 / 40.2 | 87.9 / 44.5 |
| Graduate unemployment (%) | 11.4 | 11.2 |
| All-adult unemployment (%) | 2.8 | 3.4 |
| NEET 15-29 (%) | 29.9 | 23.1 |

Tamil Nadu's year-by-year baseline ratio: 0.84, 0.67, 1.01, 1.21, 1.07 (2019-20 to 2023-24; `data/peer_ratio.csv`).

## Cities (PLFS Million-plus Cities report, persons)

| Indicator | Kolkata | Chennai | Coimbatore | Madurai | All million-plus | Urban India |
|---|---|---|---|---|---|---|
| Labour force participation % | 55.4 | 51.4 | 56.0 | 58.9 | 52.4 | 52.2 |
| Worker population ratio % | 54.3 | 49.1 | 54.7 | 52.1 | 49.8 | 49.7 |
| Unemployment % | 1.9 | 4.4 | 2.3* | 11.6 | 4.9 | 4.8 |
| Average regular wage or salary, Rs a month | 19,093 | 28,955 | 29,537 | 20,580 | 28,808 | 26,258 |
| NEET 15-24 % | 17.4 | 17.1 | 2.2 | 25.5 | 16.4 | 18.9 |
| NEET 15-29 % | 21.9 | 22.4 | 8.2 | 28.5 | 22.2 | 25.0 |

(* high sampling error in the source. Kolkata's figures match those already used in the West Bengal summary.)

## What the comparison shows
- **Tamil Nadu's formal entry is about twice West Bengal's per pass-out** (0.96 against 0.47), and about **four and a half times per young person** (9.7 against 2.1 per 100). Its graduate output per young person is also about 2.6 times West Bengal's (9.1 against 3.5), so both parts of the ratio differ.
- **The pressure-test scenarios do not change the order.** Even on the strictest reading (22-25 only) Tamil Nadu (0.44) is above West Bengal (0.26), and Tamil Nadu goes above one under the lag and participation-adjusted readings.
- **Graduate unemployment is the same (11.2% against 11.4%).** Tamil Nadu registers far more formal entry per graduate yet its graduates are not less likely to be unemployed. Possible reasons, all inferences: much of the formal entry is non-graduates or people from other states; graduates queue for better jobs; or the survey error (about 2 points) hides a small difference.
- **Tamil Nadu is not uniform.** Madurai has unemployment of 11.6% and an average regular wage near Kolkata's (Rs 20,580 against 19,093), while Chennai and Coimbatore pay about Rs 29,000, near the average of all million-plus cities. Kolkata's low pay is shared with a weaker Tamil Nadu city, not unique to the east.
- **Youth not working or studying is lower in Tamil Nadu (23.1% against 29.9%)**, and Coimbatore's rate is very low (8.2%).

## Cautions
- Tamil Nadu's ratio above one includes in-migration (workers from other states) and non-graduates in the 18-25 band; neither can be separated here.
- EPFO's state attribution (employer's state, unconfirmed) matters more where employers operate across states.
- Tamil Nadu's pass-outs per 100 youth (9.1) partly reflect students from other states studying there.
- Different age bands (EPFO 18-25, population 18-23) and year definitions (financial and academic), as before.
