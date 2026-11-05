"""Run the West Bengal analysis (baseline plus pressure-test scenarios) for any list of states, and the city comparison
from the PLFS Million-plus Cities report.

Usage (repo root): python3 -I analysis/build_state_summary.py <output csv name> "<AISHE state>:<EPFO state>:<population-sheet alias>" ...
Example:           python3 -I analysis/build_state_summary.py tamil_nadu_summary.csv "West Bengal:WEST BENGAL:" "Tamil Nadu:TAMIL NADU:Tamilnadu"
Scenarios: A baseline (EPFO 18-25 / UG pass-outs); B EPFO 22-25 only; C EPFO a year later; D supply reduced by graduate
labour-force participation (PLFS 2025 graduate LFPR by sex, state-specific). Needs `pdftotext` only for the city table
(optional 4th arg group via CITIES below).
"""
import csv, re, subprocess, sys
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parent.parent
YEARS = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]
NEXT = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
out_name = sys.argv[1]
SNAPSHOT_NAME = {"Kerala": "Keralam"}   # the 2025 district snapshot uses the state's new name
spec = [a.split(":") for a in sys.argv[2:]]            # [aishe, epfo, pop alias]

ug = {}
for r in csv.DictReader(open(ROOT / "data/aishe_outturn_by_state.csv")):
    if r["level"] == "Under Graduate":
        ug[(r["year"], r["state"])] = (int(r["male"]), int(r["female"]), int(r["total"]))
ep, rel = {}, {}
for r in csv.DictReader(open(ROOT / "data/epfo_statewise_net_payroll.csv")):
    k = (r["period"], r["state"], r["age_bucket"])
    if k not in rel or r["release_date"] > rel[k]:
        rel[k], ep[k] = r["release_date"], int(r["net_payroll"])
epf = lambda fy, es, b: sum(ep[(fy, es, x)] for x in b)
plfs = {}
for r in csv.DictReader(open(ROOT / "data/plfs2025_education_by_state.csv")):
    if r["sector"] == "rural+urban" and r["education"] in ("graduate", "all"):
        plfs[(r["indicator"], r["sex"], r["state"], r["education"])] = float(r["value"].rstrip("*"))
neet = {r["state"]: r["neet_15_29"] for r in csv.DictReader(open(ROOT / "data/plfs2025_district_snapshot.csv")) if r["level"] == "state"}
pop = {}
wb = openpyxl.load_workbook(ROOT / "raw/aishe/AISHE Final Report 2023-24 (1).xlsx", read_only=True, data_only=True)
alias = {a[2]: a[0] for a in spec if a[2]}
for r in wb["38Pop2020(2011)"].iter_rows(values_only=True):
    c = [x for x in r if x is not None]
    if len(c) >= 5 and isinstance(c[1], str):
        n = alias.get(c[1].strip(), c[1].strip())
        if n in [a[0] for a in spec]:
            pop[n] = c[4]

cols = ["state", "ug_passouts_5yr", "epfo_18_25_5yr", "ratio_A_baseline", "ratio_B_22_25_only", "ratio_C_lag", "ratio_D_lf_adjusted",
        "ug_per_100_youth_2023_24", "epfo_per_100_youth_2023_24", "female_share_2023_24", "grad_lfpr_male", "grad_lfpr_female", "grad_ur", "all_ur", "neet_15_29"]
rows = []
for s, es, _ in spec:
    sup = sum(ug[(y, s)][2] for y in YEARS)
    lm, lf = plfs[("LFPR", "male", s, "graduate")] / 100, plfs[("LFPR", "female", s, "graduate")] / 100
    a = sum(epf(y, es, ["18-21", "22-25"]) for y in YEARS)
    b = sum(epf(y, es, ["22-25"]) for y in YEARS)
    c = sum(epf(y, es, ["18-21", "22-25"]) for y in NEXT)
    d = sum(ug[(y, s)][0] * lm + ug[(y, s)][1] * lf for y in YEARS)
    rows.append({"state": s, "ug_passouts_5yr": sup, "epfo_18_25_5yr": a, "ratio_A_baseline": round(a / sup, 2), "ratio_B_22_25_only": round(b / sup, 2),
                 "ratio_C_lag": round(c / sup, 2), "ratio_D_lf_adjusted": round(a / d, 2),
                 "ug_per_100_youth_2023_24": round(ug[("2023-24", s)][2] / pop[s] * 100, 1),
                 "epfo_per_100_youth_2023_24": round(epf("2023-24", es, ["18-21", "22-25"]) / pop[s] * 100, 1),
                 "female_share_2023_24": round(ug[("2023-24", s)][1] / ug[("2023-24", s)][2], 3),
                 "grad_lfpr_male": lm * 100, "grad_lfpr_female": lf * 100, "grad_ur": plfs[("UR", "persons", s, "graduate")],
                 "all_ur": plfs[("UR", "persons", s, "all")], "neet_15_29": neet[SNAPSHOT_NAME.get(s, s)]})
with open(ROOT / "data" / out_name, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
for r in rows: print(r)
