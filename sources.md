# Sources

Status: AISHE final reports 2019-20 to 2023-24 (five years) downloaded manually on 2026-11-04 (see `raw/aishe/PROVENANCE.md`). EPFO payroll: 20 Jan 2025 release downloaded (see `raw/epfo/PROVENANCE.md`); newer releases still needed. PLFS 2025 district snapshot downloaded (see `raw/plfs/PROVENANCE.md`; the PLFS 2025 Annual Report and Million-plus Cities report are still needed). All other sources not yet fetched (the build environment's network blocked these hosts).
Deep links are deliberately omitted until verified; use the portal home and search by the dataset name.

| Dataset | Publisher / portal | Gives | Frequency | Typical lag | Caveats |
|---|---|---|---|---|---|
| EPFO payroll data | EPFO (https://www.epfo.gov.in/data-hub/), also via MoSPI | Net new members by state, age band, month | Monthly | ~1-2 months | Counts PF enrolments, not jobs; includes switchers |
| ESIC payroll data | ESIC (esic.gov.in) | Net new insured employees by state | Monthly | ~1-2 months | Wage-ceiling limited |
| PLFS | MoSPI (mospi.gov.in) | State employment, unemployment, LFPR, sector, wages; migration module | Quarterly/annual | 3-12 months | Survey estimates; limited district detail |
| Annual Survey of Industries | MoSPI | Factory employment by state | Annual | 1-2 years | Manufacturing only |
| AISHE (Table 33, state-wise out-turn) | Ministry of Education (aishe.gov.in/document-category/aishe-final-reports/) | Enrolment and pass-outs by state, university, discipline | Annual | 2-3 years | Lagged; check definitions of "pass-out" |
| AICTE dashboard | AICTE | Technical-institution intake and placement | Annual | ~1 year | Self-reported placements |
| NIRF | MoE (nirfindia.org) | Graduating numbers, placement, median salary (ranked institutes) | Annual | ~1 year | Ranked institutions only |
| Udyam registrations | Ministry of MSME | Registered units and reported employment by state | Continuous | Low | Self-reported |
| MCA / GST registrations | MCA, GSTN | New companies/taxpayers by state | Monthly | Low | No job counts |
| WB Economic Review, budget speeches, policies | Govt of West Bengal | Official claims, stated targets | Annual | Low | Claims, not outcomes |
| Bengal Global Business Summit MoUs | Govt of West Bengal / WBIDC | Announced investment and hiring intent | Event-based | n/a | Intent, not realised |
| LinkedIn Economic Graph, Naukri JobSpeak, Indeed Hiring Lab | Private | City-level hiring and talent-migration trends | Monthly/periodic | Low | Indices, not counts |
| CMIE (paid) | CMIE | Capex announced vs completed; household employment | Monthly | Low | Licence required |
