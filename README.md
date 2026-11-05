# state-jobs-gap

Public-data baseline for one question, state by state:

> How many graduates does a state produce each year, how many formal jobs does it add,
> and what does the gap imply for out-migration of young professionals?

First state: **West Bengal**. Other states are added by copying `states/west_bengal.yaml`.

## Why
A public question (a LinkedIn post, Nov 2026) asked: how many jobs have been created in West Bengal,
when do people join, and how many migrations to other cities are planned to be stopped in the next
two years, based on graduates from the state's universities. No public white paper answers this.
This repo builds the baseline from public sources so claims can be tested against it.

## Method (planned)
1. **Supply**: graduates per year by state/discipline (AISHE, AICTE, NIRF).
2. **Demand proxy**: net new formal workers by state and month (EPFO payroll, ESIC), plus PLFS employment indicators.
3. **Gap**: supply minus in-state net formal additions = implied outflow (a rough estimate, with stated bounds).
4. **Claims check**: announced investments/hiring (summit MoUs, CMIE if licensed) vs realised EPFO additions.
5. **Targets**: search budget speeches and state policies for any stated migration/job target.

## What this cannot show
- Individual offer or joining dates (company-held).
- "Planned" migration reductions: a government target, not a dataset.
- Informal-sector jobs: EPFO/ESIC see only formal payroll; PLFS is survey-based and lagged.
- EPFO net additions include job switchers and formalisation, so they overstate "new jobs".

## Layout
```
states/     one YAML config per state
sources.md  every source: publisher, URL, frequency, lag, caveats
raw/        untouched downloads (never edited)
scripts/    fetch + clean, one per source
data/       cleaned state-year / state-month tables
analysis/   gap computation and charts
```

## Rules
- `raw/` is append-only. Cleaned data is always reproducible from `raw/` via `scripts/`.
- Every number in a report traces to a row in `data/` and a source in `sources.md`.
- No estimates presented as facts; state the formula and bounds.
