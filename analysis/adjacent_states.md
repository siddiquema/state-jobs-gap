# The same analysis for the states bordering West Bengal

Run 2026-11-05. Code: `analysis/build_adjacent_states.py`. Data: `data/adjacent_states_summary.csv`.
Bordering states: Odisha, Jharkhand, Bihar, Assam, Sikkim. Method, sources and caveats as in `west_bengal_summary.md` and `pressure_test.md`.
**Sikkim is not in EPFO's state tables**, so it has AISHE and PLFS measures only (tiny sample: 26,323 UG pass-outs over five years).

## Formal entrants (EPFO net payroll 18-25) per undergraduate pass-out, 2019-20 to 2023-24

| State | A. Baseline | B. Ages 22-25 only | C. One-year lag | D. Pass-outs in labour force | UG pass-outs per 100 youth | Formal entrants per 100 youth |
|---|---|---|---|---|---|---|
| **West Bengal** | **0.47** | **0.26** | **0.51** | **0.76** | 3.5 | 2.1 |
| Odisha | 0.38 | 0.21 | 0.43 | 0.58 | 3.9 | 1.9 |
| Jharkhand | 0.27 | 0.15 | 0.29 | 0.44 | 3.3 | 1.0 |
| Assam | 0.21 | 0.11 | 0.20 | 0.30 | 2.6 | 0.7 |
| Bihar | 0.09 | 0.06 | 0.11 | 0.16 | 3.5 | 0.3 |

(Youth columns: 2023-24, population aged 18-23 from AISHE Table 38. For comparison, Tamil Nadu, Telangana, Karnataka and Maharashtra register 9.7 to 11.1 formal entrants per 100 youth.)

## Graduates and young people (PLFS 2025)

| State | Graduate unemployment % | All-adult unemployment % | Graduate labour-force participation: men / women % | NEET 15-29 % |
|---|---|---|---|---|
| West Bengal | 11.4 | 2.8 | 85.7 / 40.2 | 29.9 |
| Odisha | 16.0 | 2.9 | 88.1 / 43.7 | 26.3 |
| Jharkhand | 13.8 | 2.7 | 88.5 / 35.6 | 21.0 |
| Bihar | 18.1 | 3.8 | 85.4 / 24.5 | 32.1 |
| Assam | 13.0 | 3.7 | 89.8 / 53.2 | 25.8 |
| Sikkim | 7.1 | 3.2 | 94.4 / 67.2 | 8.4 |

## What the comparison shows
- **West Bengal is the strongest of its neighbours on formal entry, under every scenario.** Its ratio is highest under A, B, C and D (0.47, 0.26, 0.51, 0.76), and its formal entry per young person (2.1 per 100) is above Odisha's (1.9) and well above Jharkhand's, Assam's and Bihar's. The ordering does not depend on the assumptions behind the pressure test.
- **Against the south and west, every eastern state is far behind.** Even Odisha, the closest, registers a fifth of the formal entry per young person that Karnataka or Maharashtra does. The shortfall looks regional, not specific to West Bengal.
- **Graduate unemployment is lower in West Bengal (11.4%) than in all four neighbours with a comparable sample (13.0% to 18.1%).** All are above the all-adult rate by a factor of four to six.
- **Graduate women's participation varies widely** (24.5% in Bihar to 53.2% in Assam; West Bengal 40.2%). Where participation is low, the unexplained shortfall is smaller after adjustment (scenario D), but the formal-entry ratio stays far below one everywhere in the region.
- **Bihar's 0.09** says that almost no young formal-sector entry is recorded in the state against about two million undergraduate pass-outs in five years. Bihar students commonly study in other states, and AISHE counts pass-outs by the state of the institution, so Bihar-origin graduates are undercounted at home and counted elsewhere.

## Cautions specific to this comparison
- AISHE counts pass-outs by institution location and EPFO probably counts by employer location (unconfirmed). Students and workers who cross state lines (for example, Bihar and Jharkhand students studying in other states, or workers moving to Kolkata) distort the ratios in both directions.
- The measures use different age bands (EPFO 18-25, population 18-23) and different years (academic and financial).
- Sikkim's PLFS figures come from a very small sample and are not reliable; do not read its low NEET and low graduate unemployment as a finding.
- EPFO coverage differs by state (share of employment in covered establishments), which limits how far "formal entry per young person" can be compared across the region.

## Inference, not finding
The neighbours' ratios mean that the West Bengal result is not unusual for eastern India: the common pattern is thin formal job entry relative to the young population. If graduates are moving out of the region (to the south and west), the gap would be the same shape in Odisha, Jharkhand, Assam and Bihar, and this data cannot yet distinguish that from low formal-sector job creation in all four. Tracer data (graduates' later location and work) is what would separate the two.
