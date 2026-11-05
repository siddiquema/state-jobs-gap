# Robustness check: does "thin formal entry" survive without EPFO's state attribution?

Run 2026-11-05. Code: `analysis/robustness_plfs.py`. Data: `data/robustness_plfs.csv`.
Concern: EPFO may assign workers to the employer's registered state (unconfirmed; neither payroll PDF says how). If so, the high-entry states could look better, and West Bengal worse, for reasons that have nothing to do with jobs located there.
Test: compare the EPFO ordering with PLFS 2025 indicators measured where people **live** and work (a different source, unaffected by employer registration). 11 states with both measures (Sikkim has no EPFO figures).

## Results (rural+urban, persons)

| State | EPFO formal entrants per 100 youth | PLFS: regular wage/salaried share of workers % | PLFS: share of non-farm workers in limited companies % | PLFS: regular non-farm jobs with no social security % | PLFS: formal-job density per 100 people aged 15+ |
|---|---|---|---|---|---|
| Bihar | 0.3 | 12.0 | 2.0 | 61.3 | 2.2 |
| Assam | 0.7 | 17.9 | 6.3 | 51.4 | 5.2 |
| Jharkhand | 1.0 | 13.7 | 6.7 | 56.4 | 3.5 |
| Odisha | 1.9 | 15.0 | 7.4 | 50.2 | 4.6 |
| **West Bengal** | **2.1** | **22.3** | **8.3** | **60.5** | **5.1** |
| Andhra Pradesh | 2.3 | 23.6 | 9.4 | 53.7 | 6.4 |
| Kerala | 2.8 | 40.0 | 11.0 | 59.4 | 8.9 |
| Tamil Nadu | 9.7 | 37.3 | 17.6 | 45.1 | 12.3 |
| Telangana | 10.3 | 27.1 | 13.8 | 43.0 | 9.0 |
| Karnataka | 10.8 | 29.2 | 19.8 | 36.4 | 10.8 |
| Maharashtra | 11.1 | 32.8 | 24.3 | 45.0 | 10.5 |

Formal-job density is a rough construction: working-population ratio x regular wage/salaried share x (1 - share without social security). The regular share covers all workers and the social-security share covers non-farm regular employees, so treat it as indicative.

## What it shows
- **The ordering survives.** Rank correlation (Spearman, 11 states) between EPFO formal entry per young person and the PLFS measures: 0.99 with the limited-company share of non-farm workers, 0.88 with formal-job density, 0.83 with the regular wage/salaried share. A residence-based source reproduces the EPFO order, so state attribution is unlikely to be creating it. (Government employment correlates only 0.34, as expected: EPFO does not cover most of it.) Small sample, so this supports rather than proves.
- **But the size of the gap is smaller on PLFS.** EPFO puts West Bengal at about a fifth of the high-entry states (2.1 against 9.7 to 11.1 per 100 youth). On PLFS formal-job density West Bengal (5.1) is about half of them (9.0 to 12.3), and its limited-company share (8.3%) is between a third and three fifths of theirs (13.8 to 24.3%). EPFO measures new entrants and coverage, PLFS a stock of jobs, so they are not directly comparable, but EPFO probably overstates how far behind West Bengal is.
- **West Bengal has fewer regular jobs than the high-entry states, and more of them are informal.** Its regular wage/salaried share (22.3%) is close to India's (23.6%) and Andhra Pradesh's (23.6%) but below the high-entry states' (27.1 to 37.3%). And 60.5% of its non-farm regular jobs carry no social security (India 51.7%; the high-entry states 36 to 45%); only Bihar is worse. The gap is about the quality and formality of salaried work as well as its quantity.
- **Kerala is not like West Bengal after all.** On EPFO it matches West Bengal (2.8 against 2.1), but on PLFS Kerala has by far the highest regular wage/salaried share (40.0%) and a formal-job density (8.9) near the high-entry group. Kerala's EPFO figure may understate its formal employment; possible reasons (not tested) are public-sector and cooperative jobs outside EPFO. West Bengal, Andhra Pradesh, Odisha and Assam stay together at the low end on both sources.

## Cautions
- Eleven states, rank correlation: indicative only.
- PLFS shares are sample estimates; the report flags none of these tables for West Bengal, but sub-group errors are not published.
- If employers in Maharashtra (and Karnataka) register in head-office states, their EPFO figures could still be inflated a little; the PLFS company share of 24.3% for Maharashtra is the independent support for its high rank.

## Effect on earlier conclusions
- "Thin formal job entry" in West Bengal is **supported**, now by two independent sources.
- The "about a fifth" comparison with the high-entry states should be read as an EPFO figure; PLFS suggests **about half**.
- The caveat that EPFO's state attribution is unconfirmed stays, but its effect on the ordering is **tested and not found**.
- Kerala should not be grouped with West Bengal.
