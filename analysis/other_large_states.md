# Other large states (Tamil Nadu, Andhra Pradesh, Telangana, Kerala, Karnataka, Maharashtra) through the same analysis

Run 2026-11-05. Code: `analysis/build_state_summary.py`, `scripts/extract_plfs_city_rows.py`. Data: `data/large_states_summary.csv`, `data/maharashtra_cities.csv`.
States: Tamil Nadu, Andhra Pradesh, Telangana, Kerala, Karnataka and Maharashtra, with West Bengal for comparison. Method and caveats as in `west_bengal_summary.md` and `pressure_test.md`.
Note: the 2025 PLFS district snapshot names Kerala "Keralam"; the script maps it.

## Formal entrants (EPFO net payroll 18-25) per undergraduate pass-out, 2019-20 to 2023-24

| State | A. Baseline | B. Ages 22-25 | C. Lag | D. In labour force | Pass-outs per 100 youth | Formal entrants per 100 youth |
|---|---|---|---|---|---|---|
| **West Bengal** | **0.47** | **0.26** | **0.51** | **0.76** | 3.5 | 2.1 |
| Andhra Pradesh | 0.33 | 0.17 | 0.34 | 0.50 | 6.5 | 2.3 |
| Kerala | 0.47 | 0.29 | 0.50 | 0.74 | 5.7 | 2.8 |
| Tamil Nadu | 0.96 | 0.44 | 1.01 | 1.51 | 9.1 | 9.7 |
| Telangana | 1.38 | 0.75 | 1.50 | 2.18 | 6.5 | 10.3 |
| Karnataka | 1.57 | 0.83 | 1.65 | 2.55 | 6.8 | 10.8 |
| Maharashtra | 1.60 | 0.86 | 1.69 | 2.47 | 5.5 | 11.1 |

## Graduates and young people (PLFS 2025)

| State | Women's share of UG pass-outs (2023-24) | Graduate participation men / women % | Graduate unemployment % | All-adult unemployment % | NEET 15-29 % |
|---|---|---|---|---|---|
| West Bengal | 52% | 85.7 / 40.2 | 11.4 | 2.8 | 29.9 |
| Andhra Pradesh | 51% | 88.3 / 44.1 | 21.6 | 4.2 | 26.6 |
| Kerala | 64% | 80.6 / 53.7 | 13.1 | 4.4 | 21.5 |
| Tamil Nadu | 55% | 87.9 / 44.5 | 11.2 | 3.4 | 23.1 |
| Telangana | 53% | 87.8 / 43.3 | 17.6 | 5.0 | 26.2 |
| Karnataka | 53% | 85.0 / 41.8 | 7.9 | 2.3 | 20.8 |
| Maharashtra | 47% | 87.3 / 38.8 | 6.8 | 2.4 | 21.9 |

## What the comparison shows
- **The states split into two groups, and West Bengal is in the low one.** Per 100 young people, West Bengal (2.1), Andhra Pradesh (2.3) and Kerala (2.8) register between a fifth and a quarter of the formal entry of Tamil Nadu, Karnataka, Telangana and Maharashtra (9.7 to 11.1). Kerala's ratio (0.47) equals West Bengal's. The pressure-test scenarios keep both groups apart.
- **West Bengal's result is therefore not a West Bengal peculiarity.** Two southern states look the same as it does. The contrast is between a few states with very high formal entry per young person and the rest.
- **Maharashtra is the extreme case:** the highest formal entry per young person (11.1 per 100) and the lowest graduate unemployment (6.8%), yet its graduate output per young person (5.5) is only the second lowest of the seven, above West Bengal's 3.5. Even on the strictest reading (22-25 only) its ratio is 0.86, close to one. Women are 47% of its pass-outs, the smallest share of the seven.
- **Graduate unemployment does not follow formal entry in a simple way.** Telangana pairs high formal entry (10.3 per 100) with high graduate unemployment (17.6%); Andhra Pradesh pairs low entry with the highest rate (21.6%); Maharashtra and Karnataka pair high entry with the two lowest rates (6.8% and 7.9%). Rates carry about 2 points of sampling error.
- **Kerala is different on women.** Women are 64% of its pass-outs and graduate women's participation (53.7%) is the highest of the seven states.
- **West Bengal's graduate unemployment (11.4%) is the fourth lowest of the seven**, behind Maharashtra (6.8%), Karnataka (7.9%) and Tamil Nadu (11.2%, within sampling error of it).

## Cities (PLFS Million-plus Cities report, persons)

| Indicator | Kolkata | Greater Mumbai | Pune | Nagpur | Thane | All million-plus | Urban India |
|---|---|---|---|---|---|---|---|
| Labour force participation % | 55.4 | 51.3 | 57.9 | 48.3 | 53.7 | 52.4 | 52.2 |
| Worker population ratio % | 54.3 | 49.5 | 53.4 | 46.6 | 51.5 | 49.8 | 49.7 |
| Unemployment % | 1.9 | 3.6 | 7.8* | 3.6 | 4.1 | 4.9 | 4.8 |
| Average regular wage or salary, Rs a month | 19,093 | 36,267 | 30,670 | 25,145 | 27,173 | 28,808 | 26,258 |
| NEET 15-29 % | 21.9 | 20.0 | 15.5 | 20.1 | 16.0 | 22.2 | 25.0 |

(* high sampling error in the source.) Greater Mumbai's average regular wage is about 1.9 times Kolkata's, and every Maharashtra city listed pays more than Kolkata.

## Inference, not finding
The high-entry states (Tamil Nadu, Karnataka, Telangana, Maharashtra) are likely to be the ones drawing workers from elsewhere, and the low-entry states (West Bengal, Andhra Pradesh, Kerala) the ones sending them. This data does not show it: it shows only the two groups. Migration data or graduate tracking is needed to test it.

## Cautions
- Many Maharashtra employers are headquartered in Mumbai, so if EPFO attributes workers to the registering establishment's state (unconfirmed), Maharashtra's formal entry could be inflated.
- Andhra Pradesh and Telangana were one state until 2014; where employers are registered (EPFO attributes workers by state, probably the employer's, unconfirmed) matters a lot for both.
- Students and workers cross state lines, which affects every ratio. Pass-outs by institution count students who come from other states.
- Different age bands (EPFO 18-25, population 18-23) and year definitions (financial and academic).
- Graduate unemployment is a sample estimate with about 2 points of error either side (my estimate; the report publishes none for this table).
