# West Bengal: graduates, formal jobs and the gap (public-data baseline, v1)

Prepared 2026-11-05 from AISHE, EPFO and PLFS. Every figure traces to `data/` and `sources.md`; code is in `scripts/` and `analysis/`.

## The question
A public post asked how many jobs have been created in West Bengal, when people join, and how many migrations to other cities are planned to be stopped in two years, given the state's graduates. This note says what public data can and cannot answer.

## 1. What public data answers

| Ask in the post | What we can say | Confidence |
|---|---|---|
| How many jobs created | Formal-sector net new payroll (EPFO) for age 18-25 was 218k (FY2022-23), 209k (FY2023-24) and 212k (FY2024-25). All ages: 488k, 476k, 458k. This is **not** a count of jobs created: it is new subscribers minus exits plus rejoiners, formal sector only. | Medium |
| Joining dates | Not public at company level. EPFO publishes monthly net payroll by state and age band (series in `data/epfo_statewise_net_payroll.csv`). | Low for the ask as worded |
| Migrations planned to be stopped | **No public target found, but I have not yet searched** WB budget speeches, IT/industrial policies or summit documents (the build environment could not reach those sites). Not evidence that none exists. | Open |

## 2. Supply versus demand (West Bengal)

| Year | UG pass-outs (AISHE) | EPFO net payroll, age 18-25 | Ratio |
|---|---|---|---|
| 2019-20 | 302,453 | 148,654 | 0.49 |
| 2020-21 | 400,113 | 123,340 | 0.31 |
| 2021-22 | 410,187 | 191,558 | 0.47 |
| 2022-23 | 424,345 | 217,552 | 0.51 |
| 2023-24 | 348,424 | 208,923 | 0.60 |
| **Five years** | **1,885,522** | **890,027** | **0.47** |

Over five years West Bengal's institutions produced about 1.89 million undergraduate pass-outs, while about 0.89 million young people (18-25) entered formal payroll in the state: a difference of about **1.0 million**. This is a gap, **not a migration count** (see section 5).

## 3. Peers: formal entrants per UG pass-out (2022-23 and 2023-24)

| State | 2022-23 | 2023-24 |
|---|---|---|
| West Bengal | 0.51 | 0.60 |
| Tamil Nadu | 1.21 | 1.07 |
| Telangana | 1.66 | 1.58 |
| Karnataka | 1.73 | 1.60 |
| Maharashtra | 1.76 | 2.02 |

Peer states register more young formal entrants than their own pass-outs, which fits them drawing people in from other states (and also counts non-graduates aged 18-25). West Bengal registers about half. The pattern is consistent with West Bengal being a net source of young workers, but it does not measure how many leave. Full series: `data/peer_ratio.csv`.

## 4. What graduates actually face in West Bengal (PLFS 2025, age 15+)
- Unemployment is **2.8%** overall but **11.4% for graduates** (India: 11.2%), 6.3% for postgraduates (India: 10.0%), 11.6% for diploma holders (India: 6.9%).
- Youth NEET (not working, not studying, 15-29): **29.9%** statewide; Kolkata 21.9% (women 44.2%); most other districts 31-38%.
- Kolkata's unemployment is low (1.9%, high sampling error) but regular wage/salary averages Rs 19,093 a month against Rs 28,808 for all million-plus cities: people work, but at lower pay.

## 5. What this does not show
- **Not a migration number.** The gap also contains graduates who study further, work informally or for government (outside EPFO), start businesses, are unemployed (graduate UR 11.4%), or are outside the labour force.
- **EPFO state is probably the state of the establishment.** A West Bengal graduate working for a Bengaluru-registered firm appears in Karnataka's payroll, which would make the gap partly a measure of leaving, but this needs confirming against EPFO's methodology note.
- **Calendar mismatch.** AISHE years are academic and EPFO years are financial; graduates mostly join in the following year.
- **AISHE 2023-24 fall (-18%) is unexplained** (`analysis/aishe_quality_check.md`); response rates do not explain it. Use multi-year totals, as above.
- **Provisional EPFO data** for recent months; annual figures for earlier years did not change between the Jan and Sep 2025 releases.
- PLFS measures where people live now, not where they studied, so it cannot show departures.

## 6. What would turn the gap into an outflow estimate
1. Where WB institutions' graduates are hired: NIRF/AICTE placement data and institute reports.
2. Progression to postgraduate study: AISHE PG enrolment by state.
3. Inter-state movement: PLFS "Migration in India" report; the next Census.
4. Any stated WB target (budget speeches, IT and industrial policy, summit MoUs).
5. Other states' calculations with the same code (`states/` config) to confirm the pattern holds beyond four peers.
