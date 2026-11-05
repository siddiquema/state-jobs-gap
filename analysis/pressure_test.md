# Pressure test of the West Bengal findings

Run 2026-11-05. Code: `analysis/pressure_test.py`. Data: `data/pressure_test_sensitivity.csv`, `data/pressure_test_peers_per_youth.csv`.
Each claim from `west_bengal_summary.md` and the dashboard is tested against the source files, with a verdict.

## Sensitivity of the headline ratio (EPFO net payroll vs UG pass-outs, 2019-20 to 2023-24)

| Scenario | Ratio | Reading |
|---|---|---|
| A. Baseline: EPFO 18-25 / all UG pass-outs | 0.47 | As published on the dashboard |
| B. Graduate-age band only (EPFO 22-25) | 0.26 | 18-21 entrants are mostly school leavers, not graduates |
| C. One-year lag (EPFO a year after the AISHE year) | 0.51 | Conclusion survives the timing mismatch |
| D. Pass-outs reduced to those in the labour force | 0.76 | Uses PLFS 2025 graduate participation: men 85.7%, women 40.2% |

The ratio ranges from 0.26 to 0.76 depending on assumptions. "West Bengal registers fewer young formal entrants than graduates" holds in all four. The size of the shortfall does not: the "about 1.0 million gap" is the **upper end**. Under D it is about 0.28 million (1.17 million labour-force entrants vs 0.89 million formal entrants). D is an upper bound on participation, since recent graduates participate less than all graduates aged 15+.

## Peers per young person (AISHE Table 38 population aged 18-23)

| State | UG pass-outs per 100 youth (2023-24) | EPFO net payroll 18-25 per 100 youth | EPFO per pass-out |
|---|---|---|---|
| West Bengal | 3.5 | 2.1 | 0.60 |
| Tamil Nadu | 9.1 | 9.7 | 1.07 |
| Telangana | 6.5 | 10.3 | 1.58 |
| Karnataka | 6.8 | 10.8 | 1.60 |
| Maharashtra | 5.5 | 11.1 | 2.02 |

(2022-23 gives the same picture, in `data/pressure_test_peers_per_youth.csv`.) West Bengal's formal entry per young person is about a fifth of the peers', a much larger gap than its graduate output per young person (about 40-65% of the peers'). **The low ratio comes mostly from thin formal-sector entry, not from an unusual surplus of graduates.** Matching the lowest peer (Tamil Nadu, 9.7 per 100) would mean about 0.97 million formal entrants a year against about 0.21 million now, roughly 4.6 times. Ages are not identical (18-25 vs 18-23), which does not change the order of magnitude.

## Claim-by-claim verdicts

| Claim | Verdict |
|---|---|
| 1.89 million UG pass-outs and 0.89 million formal entrants over five years | **Holds** (re-derived). The inputs have caveats: AISHE 2020-21 jump and 2023-24 fall are unexplained; replacing 2023-24 with the 2020-23 average moves the ratio from 0.47 to 0.46. |
| "About 1.0 million gap" | **Overstated.** Upper end of 0.28-1.0 million depending on assumptions. |
| "West Bengal registers about half the peers' ratio" | **Holds**, and understates the difference per young person (about a fifth). |
| "Consistent with West Bengal being a net source of young workers" | **Not supported as worded.** Equally consistent with thin formal job creation, low participation of women graduates and a larger informal sector. Migration cannot be separated from these with this data. |
| EPFO state = employer's state | **Unverified, but tested** (`analysis/robustness_check.md`): a residence-based PLFS measure reproduces the EPFO ordering across 11 states (rank correlation 0.88 to 0.99), so attribution is unlikely to create the ordering; it still cannot rule out some inflation for head-office states, and PLFS shows a smaller gap in size (about half, not a fifth). The dashboard stated it as fact; corrected to "probably, not confirmed". If employers file under head-office states, peer ratios are inflated, but a gap of this size (about 2 vs about 10 per 100) is unlikely to come from that alone. |
| EPFO net payroll is a count of entrants | **Weak.** Net = new subscribers - exits + rejoiners; for 22-25 nationally, rejoiners push net above gross new subscribers, so it is not first-time jobs. |
| Graduate unemployment 11.4% vs 2.8% overall | **Numbers verified; framing needs care.** India's graduate rate is 11.2%, so this is a national pattern, not a West Bengal failure. Comparing with the all-adult rate flatters the headline (many unlettered adults work out of necessity). The report publishes no standard error for this table. A rough estimate from sample size (assuming about 38,000 persons aged 15+ surveyed, a design effect of 2-3) gives roughly plus or minus 2 points. |
| Postgraduates do better than India (6.3% vs 10.0%) | **Suggestive only.** Sampling error is wider (about plus or minus 2.5 points for each rate). |
| Kolkata is low pay | **Holds, and stronger than first stated:** regular wage Rs 19,093 a month is the 5th lowest of 46 million-plus cities; Howrah (Rs 23,078) is 16th lowest. The comparison with the all-city average (Rs 28,808) is inflated by high-wage metros. "People take whatever work is available" remains an inference; cost of living and industry mix are alternative explanations. |
| "Most other districts have NEET of 31-38%" | **Imprecise.** Districts other than Kolkata range 25.6-38.2%; six of nine fall within 31-38%. |
| EPFO annual figures did not change between releases | **Holds** for FY2018-19 to FY2023-24 between the Jan and Sep 2025 releases (a short window). |

## Inferences not asked, but worth pondering (labelled as inference, not finding)
1. **The binding constraint looks like formal job creation per young person, not graduate supply.** Even if every West Bengal graduate stayed, current formal entry could not absorb them; a "stop migration" target is an arithmetic problem about job creation.
2. **Women graduates are the largest unused pool.** Women are the majority of UG pass-outs (about 52%), yet graduate women's participation is about 40% against about 86% for men. India shows the same pattern, so it is national, but it dominates the gap more than migration does.
3. **Vocational training looks like a weak link.** West Bengal's unemployment among diploma/certificate holders (11.6%) is well above India's (6.9%).
4. **The people who migrate most may not be graduates.** Graduate-focused framing can miss lower-skilled out-migration, which the 18-21 EPFO band and PLFS migration reports would show better.
5. **Kolkata looks like a low-wage, low-unemployment equilibrium.** If so, pay and productivity matter more than job counts.
6. **The question could be answered directly with linked data.** EPFO accounts are Aadhaar-linked and AISHE records pass-outs by institution; a state tracer study of graduates (where they work, how much, in which state) would replace every inference here.
7. **A three-number annual scorecard would make claims testable:** formal entry per 100 young people, graduate unemployment, and median graduate wage.
8. **Open data checks:** the composition of UG pass-outs (general degrees vs professional courses, regular vs distance) and ASI 2024-25 factory employment would test whether the formal-job shortfall is a manufacturing story.
