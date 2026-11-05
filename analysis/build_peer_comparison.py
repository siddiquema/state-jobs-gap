"""Peer comparison: EPFO net new payroll (age 18-25) per undergraduate pass-out, by state and year.

Inputs : data/aishe_outturn_by_state.csv, data/epfo_statewise_net_payroll.csv (newest release for each year)
Output : data/peer_ratio.csv.  Run from repo root: python3 -I analysis/build_peer_comparison.py
Caveat : EPFO counts by state of the establishment (to be confirmed against EPFO's methodology note);
a ratio above 1 means more young formal-sector entrants than local UG pass-outs (in-migration and non-graduates included).
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YEARS = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]
STATES = {"West Bengal": "WEST BENGAL", "Karnataka": "KARNATAKA", "Tamil Nadu": "TAMIL NADU",
          "Maharashtra": "MAHARASHTRA", "Telangana": "TELANGANA"}

ug = {(r["year"], r["state"]): int(r["total"]) for r in csv.DictReader(open(ROOT / "data/aishe_outturn_by_state.csv"))
      if r["level"] == "Under Graduate"}
epfo, rel = {}, {}
for r in csv.DictReader(open(ROOT / "data/epfo_statewise_net_payroll.csv")):
    if r["age_bucket"] in ("18-21", "22-25"):
        k = (r["period"], r["state"], r["age_bucket"])
        if k not in rel or r["release_date"] > rel[k]:
            rel[k], epfo[k] = r["release_date"], int(r["net_payroll"])

rows = []
for s, es in STATES.items():
    for y in YEARS:
        e = epfo[(y, es, "18-21")] + epfo[(y, es, "22-25")]
        rows.append([s, y, ug[(y, s)], e, round(e / ug[(y, s)], 2)])
with open(ROOT / "data/peer_ratio.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["state", "year", "ug_passouts", "epfo_net_payroll_18_25", "ratio"])
    w.writerows(rows)
for r in rows:
    print(*r)
