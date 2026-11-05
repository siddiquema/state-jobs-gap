"""Pressure test of the West Bengal gap: sensitivity of the ratio to its assumptions, and peer decomposition.

Writes data/pressure_test_sensitivity.csv and data/pressure_test_peers_per_youth.csv.
Run from repo root: python3 -I analysis/pressure_test.py
Inputs: data/aishe_outturn_by_state.csv, data/epfo_statewise_net_payroll.csv, data/plfs2025_education_by_state.csv,
        raw/aishe/*.xlsx (Table 38 population 18-23).
"""
import csv
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parent.parent
YEARS = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]

ug = {}
for r in csv.DictReader(open(ROOT / "data/aishe_outturn_by_state.csv")):
    if r["level"] == "Under Graduate":
        ug[(r["year"], r["state"])] = (int(r["male"]), int(r["female"]), int(r["total"]))

ep, rel = {}, {}
for r in csv.DictReader(open(ROOT / "data/epfo_statewise_net_payroll.csv")):
    k = (r["period"], r["state"], r["age_bucket"])
    if k not in rel or r["release_date"] > rel[k]:
        rel[k], ep[k] = r["release_date"], int(r["net_payroll"])
def epfo(fy, state, buckets): return sum(ep[(fy, state, b)] for b in buckets)

plfs = {(r["sex"], r["state"]): float(r["value"].rstrip("*")) for r in csv.DictReader(open(ROOT / "data/plfs2025_education_by_state.csv"))
        if r["indicator"] == "LFPR" and r["sector"] == "rural+urban" and r["education"] == "graduate"}
lf_m, lf_f = plfs[("male", "West Bengal")] / 100, plfs[("female", "West Bengal")] / 100

WB, WBE = "West Bengal", "WEST BENGAL"
sup = sum(ug[(y, WB)][2] for y in YEARS)
rows = []
def add(name, num, den, note):
    rows.append([name, round(num), round(den), round(num / den, 2), note])
add("A. Baseline: EPFO 18-25 / all UG pass-outs", sum(epfo(y, WBE, ["18-21", "22-25"]) for y in YEARS), sup, "As on the dashboard.")
add("B. Graduate-age band only: EPFO 22-25 / all UG pass-outs", sum(epfo(y, WBE, ["22-25"]) for y in YEARS), sup, "18-21 entrants are mostly school leavers, not graduates.")
fy_next = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
add("C. One-year lag: EPFO 18-25 in the following year / pass-outs", sum(epfo(y, WBE, ["18-21", "22-25"]) for y in fy_next), sup, "Graduates mostly join the year after.")
lfsup = sum(ug[(y, WB)][0] * lf_m + ug[(y, WB)][1] * lf_f for y in YEARS)
add("D. Pass-outs adjusted for labour-force participation", sum(epfo(y, WBE, ["18-21", "22-25"]) for y in YEARS), lfsup,
    "Pass-outs x PLFS 2025 graduate participation by sex (men 85.7%, women 40.2%). Upper bound: recent graduates participate less.")
with open(ROOT / "data/pressure_test_sensitivity.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["scenario", "numerator", "denominator", "ratio", "note"]); w.writerows(rows)

# peers per youth population (AISHE Table 38, age 18-23)
FILES = {"2022-23": "AISHE Final Report 2022-23.xlsx", "2023-24": "AISHE Final Report 2023-24 (1).xlsx"}
STATES = {"West Bengal": "WEST BENGAL", "Tamil Nadu": "TAMIL NADU", "Telangana": "TELANGANA", "Karnataka": "KARNATAKA", "Maharashtra": "MAHARASHTRA"}
out = []
for y, f in FILES.items():
    wb = openpyxl.load_workbook(ROOT / "raw/aishe" / f, read_only=True, data_only=True)
    ws = wb[[n for n in wb.sheetnames if n.lower().replace(" ", "").startswith("38")][0]]
    pop = {}
    for r in ws.iter_rows(values_only=True):
        c = [x for x in r if x is not None]
        if len(c) >= 5 and isinstance(c[1], str) and c[1].strip().replace("Tamilnadu", "Tamil Nadu") in STATES:
            pop[c[1].strip().replace("Tamilnadu", "Tamil Nadu")] = c[4]
    for s, es in STATES.items():
        e = epfo(y, es, ["18-21", "22-25"])
        out.append([s, y, pop[s], ug[(y, s)][2], e, round(ug[(y, s)][2] / pop[s] * 100, 1), round(e / pop[s] * 100, 1), round(e / ug[(y, s)][2], 2)])
with open(ROOT / "data/pressure_test_peers_per_youth.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["state", "year", "population_18_23", "ug_passouts", "epfo_net_payroll_18_25", "passouts_per_100_youth", "epfo_per_100_youth", "epfo_per_passout"])
    w.writerows(out)
for r in rows: print(r[:4])
for r in out: print(r)
