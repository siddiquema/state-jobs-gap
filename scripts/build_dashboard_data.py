"""Rebuild the ten data files the dashboard reads (dashboard/data/*.csv) from the repo's cleaned tables.

Run from the repo root: python3 -I scripts/build_dashboard_data.py
Eight files are plain copies of tables in data/; two are derived here (education, districts). See dashboard/README.md.
"""
import csv, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dashboard" / "data"
OUT.mkdir(parents=True, exist_ok=True)

COPIES = {  # dashboard file -> data/ file
    "west-bengal-gap.csv": "wb_gap.csv",
    "peer-states-ratio.csv": "peer_ratio.csv",
    "kolkata-benchmarks.csv": "plfs2025_kolkata_howrah_vs_benchmarks.csv",
    "pressure-test-sensitivity.csv": "pressure_test_sensitivity.csv",
    "peers-per-youth.csv": "pressure_test_peers_per_youth.csv",
    "adjacent-states.csv": "adjacent_states_summary.csv",
    "large-states.csv": "large_states_summary.csv",
    "robustness-plfs.csv": "robustness_plfs.csv",
}
for dst, src in COPIES.items():
    shutil.copyfile(ROOT / "data" / src, OUT / dst)

EDU = ["not literate", "literate & up to primary", "middle", "secondary", "higher secondary",
       "diploma/certificate course", "graduate", "post graduate & above", "secondary & above", "all"]
rows = list(csv.DictReader(open(ROOT / "data/plfs2025_education_by_state.csv")))
def val(ind, state, edu):
    return next(r["value"] for r in rows if r["indicator"] == ind and r["sector"] == "rural+urban" and r["sex"] == "persons"
                and r["state"] == state and r["education"] == edu)
with open(OUT / "education-wb-vs-india.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["education", "lfpr_wb", "lfpr_india", "wpr_wb", "wpr_india", "ur_wb", "ur_india"])
    for e in EDU:
        w.writerow([e] + [val(i, s, e).rstrip("*") for i in ("LFPR", "WPR", "UR") for s in ("West Bengal", "all India")])

with open(OUT / "west-bengal-districts.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["name", "level", "lfpr_15plus", "wpr_15plus", "ur_15plus", "neet_15_29"])
    for r in csv.DictReader(open(ROOT / "data/plfs2025_district_snapshot.csv")):
        if r["state"] == "West Bengal":
            w.writerow([r["name"], r["level"], r["lfpr_15plus"], r["wpr_15plus"], r["ur_15plus"], r["neet_15_29"]])
print("wrote", len(list(OUT.glob("*.csv"))), "files to", OUT)
