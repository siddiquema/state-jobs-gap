# West Bengal: graduates, formal jobs and the gap (public-data baseline, v2)

Prepared 2026-11-05 from AISHE, EPFO and PLFS. Every figure traces to `data/` and `sources.md`; code is in `scripts/` and `analysis/`.

**v2 (after pressure test, see `analysis/pressure_test.md`):** the shortfall is given as a range (about 0.28 to 1.0 million) instead of one figure; the claim that West Bengal is "a net source of young workers" is withdrawn as unsupported; peers are compared per young person; EPFO's state attribution is marked unconfirmed; and a section of inferences not asked in the original post is added.

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

Over five years West Bengal's institutions produced about 1.89 million undergraduate pass-outs, while about 0.89 million young people (18-25) entered formal payroll in the state: a difference of about **1.0 million**. That figure is the **top of a range**, not a finding. It is **not a migration count** (see section 5).

### How much the headline depends on assumptions
| Scenario (2019-20 to 2023-24) | Formal entrants per pass-out |
|---|---|
| A. EPFO 18-25 over all UG pass-outs (baseline) | 0.47 |
| B. EPFO 22-25 only (graduate-age band) | 0.26 |
| C. EPFO a year later than the AISHE year (lag) | 0.51 |
| D. Pass-outs reduced to those in the labour force (PLFS 2025 graduate participation: men 85.7%, women 40.2%) | 0.76 |

West Bengal falls short on every reading. Under D, 1.17 million graduates would be in the labour force against 0.89 million formal entrants: a difference of about **0.28 million**. D is an upper bound on participation, since recent graduates participate less than all graduates aged 15+. So the unexplained difference lies between roughly 0.28 and 1.0 million, depending on assumptions.

## 3. Peers: formal entrants per UG pass-out (2022-23 and 2023-24)

| State | 2022-23 | 2023-24 |
|---|---|---|
| West Bengal | 0.51 | 0.60 |
| Tamil Nadu | 1.21 | 1.07 |
| Telangana | 1.66 | 1.58 |
| Karnataka | 1.73 | 1.60 |
| Maharashtra | 1.76 | 2.02 |

Peer states register more young formal entrants than their own pass-outs. Part of that may be people drawn in from other states, and the 18-25 band also counts non-graduates. West Bengal registers about half. Full series: `data/peer_ratio.csv`.

**Per young person (AISHE Table 38, population aged 18-23), 2023-24:**

| State | UG pass-outs per 100 youth | Formal entrants (EPFO 18-25) per 100 youth |
|---|---|---|
| West Bengal | 3.5 | 2.1 |
| Tamil Nadu | 9.1 | 9.7 |
| Telangana | 6.5 | 10.3 |
| Karnataka | 6.8 | 10.8 |
| Maharashtra | 5.5 | 11.1 |

West Bengal's formal entry per young person is about a fifth of the peers', a much wider difference than its graduate output per young person (about 40-65% of theirs). **The low ratio comes mostly from thin formal job entry, not from a surplus of graduates.** The earlier reading that West Bengal is "a net source of young workers" is **withdrawn**: the same pattern is equally consistent with thin formal job creation, low participation of women graduates and a larger informal sector. Migration cannot be separated from these with this data. Series: `data/pressure_test_peers_per_youth.csv`.

## 4. What graduates actually face in West Bengal (PLFS 2025, age 15+)
- Unemployment is **2.8%** overall but **11.4% for graduates** (India: 11.2%), 6.3% for postgraduates (India: 10.0%), 11.6% for diploma holders (India: 6.9%). West Bengal matches India for graduates, so this is a national pattern. The report publishes no standard error for this table; a rough estimate from sample size gives about 2 points either side, so the postgraduate difference with India is suggestive only.
- Youth NEET (not working, not studying, 15-29): **29.9%** statewide; Kolkata 21.9% (women 44.2%); districts other than Kolkata range from 25.6% to 38.2%.
- Kolkata's unemployment is low (1.9%, relative standard error about 29%, so approximate) but regular wage/salary averages Rs 19,093 a month against Rs 28,808 for all million-plus cities: people work, but at lower pay. Kolkata's regular wage is the 5th lowest of 46 million-plus cities (Howrah 16th lowest). Why is an inference: cost of living and industry mix are alternative explanations to scarce good jobs.

## 5. What this does not show
- **Not a migration number.** The gap also contains graduates who study further, work informally or for government (outside EPFO), start businesses, are unemployed (graduate UR 11.4%), or are outside the labour force.
- **EPFO's state attribution is unconfirmed.** It is probably the employer's state, in which case a West Bengal graduate working for a Bengaluru-registered firm appears in Karnataka's payroll. This has not been checked against EPFO's methodology note, but a PLFS check that does not depend on it reproduces the ordering of states (`analysis/robustness_check.md`); that check also puts West Bengal's gap to the high-entry states at about half, not a fifth, and shows more of its regular jobs lack social security (60.5% against 51.7% for India). A gap as large as 2 versus about 10 formal entrants per 100 young people is unlikely to come from attribution alone.
- **EPFO net payroll is not first-time jobs.** It is new subscribers minus exits plus rejoiners; for ages 22-25 nationally, rejoiners push net above gross new subscribers.
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

## 7. Inferences not asked in the post, but worth pondering
Inferences from the data, not findings; each could be wrong. Full reasoning in `analysis/pressure_test.md`.
1. **The binding constraint looks like formal job entry, not graduate supply.** Matching the lowest peer's formal entry per young person (Tamil Nadu, 9.7 per 100) would mean about 4.6 times today's formal entrants. Even if every graduate stayed, current formal hiring could not absorb them, so a target to stop migration is mainly a job-creation target.
2. **Women graduates are the largest unused pool.** Women are about 52% of undergraduate pass-outs, but graduate women's participation is about 40% against about 86% for men. India shows the same pattern, so it is national, yet it explains more of the shortfall than migration can.
3. **Vocational training looks like a weak link.** Unemployment among diploma and certificate holders is 11.6% in West Bengal against 6.9% in India.
4. **The people who migrate most may not be graduates.** A graduate-focused question can miss lower-skilled out-migration, which migration surveys would show better.
5. **Kolkata looks like a low-wage, low-unemployment city.** If so, pay and productivity matter more than counting jobs.
6. **The question can be answered directly.** EPFO accounts are linked to Aadhaar and AISHE records pass-outs by institution; a graduate tracer study (where graduates work, for how much, in which state) would replace most of these inferences.
7. **A three-number yearly scorecard would make any claim testable:** formal entry per young person, graduate unemployment, and median graduate pay.
8. **Still unchecked:** the mix of pass-outs (general degrees against professional courses, regular against distance), and factory employment from ASI 2024-25.
