"""Run the West Bengal analysis (with its pressure-test scenarios) for the states bordering West Bengal.

Bordering states: Odisha, Jharkhand, Bihar, Assam, Sikkim. Sikkim is not in EPFO's state tables, so it only
gets the AISHE and PLFS measures. Output: data/adjacent_states_summary.csv.  Run from repo root:
python3 -I analysis/build_adjacent_states.py
Scenarios as in analysis/pressure_test.py: A baseline; B EPFO 22-25 only; C EPFO a year later; D supply reduced by graduate
labour-force participation (PLFS 2025, by sex, state-specific).
"""
import csv
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parent.parent
YEARS = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]
NEXT = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
# AISHE name -> EPFO name (None = not in EPFO state tables)
STATES = {"West Bengal": "WEST BENGAL", "Odisha": "ORISSA", "Jharkhand": "JHARKHAND", "Bihar": "BIHAR", "Assam": "ASSAM", "Sikkim": None}

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
for r in wb["38Pop2020(2011)"].iter_rows(values_only=True):
    c = [x for x in r if x is not None]
    if len(c) >= 5 and isinstance(c[1], str) and c[1].strip() in STATES:
        pop[c[1].strip()] = c[4]

out = []
for s, es in STATES.items():
    sup = sum(ug[(y, s)][2] for y in YEARS)
    row = {"state": s, "ug_passouts_5yr": sup, "female_share_2023_24": round(ug[("2023-24", s)][1] / ug[("2023-24", s)][2], 3),
           "ug_per_100_youth_2023_24": round(ug[("2023-24", s)][2] / pop[s] * 100, 1)}
    lm = plfs[("LFPR", "male", s if s != "West Bengal" else "West Bengal", "graduate")] / 100
    lf = plfs[("LFPR", "female", s, "graduate")] / 100
    row.update({"grad_lfpr_male": lm * 100, "grad_lfpr_female": lf * 100,
                "grad_ur": plfs[("UR", "persons", s, "graduate")], "all_ur": plfs[("UR", "persons", s, "all")], "neet_15_29": neet[s]})
    if es:
        a = sum(epf(y, es, ["18-21", "22-25"]) for y in YEARS)
        b = sum(epf(y, es, ["22-25"]) for y in YEARS)
        c = sum(epf(y, es, ["18-21", "22-25"]) for y in NEXT)
        d = sum(ug[(y, s)][0] * lm + ug[(y, s)][1] * lf for y in YEARS)
        row.update({"epfo_18_25_5yr": a, "ratio_A_baseline": round(a / sup, 2), "ratio_B_22_25_only": round(b / sup, 2), "ratio_C_lag": round(c / sup, 2),
                    "ratio_D_lf_adjusted": round(a / d, 2), "epfo_per_100_youth_2023_24": round(epf("2023-24", es, ["18-21", "22-25"]) / pop[s] * 100, 1)})
    out.append(row)
cols = ["state", "ug_passouts_5yr", "epfo_18_25_5yr", "ratio_A_baseline", "ratio_B_22_25_only", "ratio_C_lag", "ratio_D_lf_adjusted",
        "ug_per_100_youth_2023_24", "epfo_per_100_youth_2023_24", "female_share_2023_24", "grad_lfpr_male", "grad_lfpr_female", "grad_ur", "all_ur", "neet_15_29"]
with open(ROOT / "data/adjacent_states_summary.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    w.writerows([{c: r.get(c, "") for c in cols} for r in out])
for r in out:
    print({c: r.get(c, "") for c in cols})
