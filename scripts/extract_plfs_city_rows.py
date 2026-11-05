"""Pull chosen cities' headline rows from the PLFS 'Labour Market Dynamics in Million-plus Cities' report.

Usage (repo root): python3 -I scripts/extract_plfs_city_rows.py <output csv> "Kolkata MC" "Chennai MC" ...
Takes the FIRST block of each table (rural+urban style 'persons' columns are the last number of M,F,P triples):
Table 2 LFPR, Table 3 WPR (usual status, 15+), Table 8 average regular wage/salary (Rs per month),
Table 11 UR (usual status), Table 12 NEET (15-24 persons, 15-29 persons).
Includes the report's 'all million-plus cities' and 'urban India' rows for comparison. A '*' marks a high-RSE estimate.
"""
import csv, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
pdf = next((ROOT / "raw/plfs").glob("*Million_plus_city_F.pdf"))
txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True).stdout.splitlines()
names = sys.argv[2:] + ["all million-plus cities", "urban India"]


def block(prefix):
    start = next(i for i, l in enumerate(txt) if l.startswith(prefix))
    end = next((i for i, l in enumerate(txt) if i > start and re.match(r"Table \d+(\.\d+)?:", l) and not l.startswith(prefix)), len(txt))
    return txt[start:end]


def first_row(lines, name, n_vals):
    for l in lines:
        m = re.match(rf"^\s*{re.escape(name)}\s+(.*)$", l)
        if m:
            v = m.group(1).split()
            if len(v) == n_vals:
                return v
    return None


spec = [("LFPR % (usual status, 15+)", "Table 2:", 3, 2), ("WPR % (usual status, 15+)", "Table 3:", 3, 2),
        ("UR % (usual status, 15+)", "Table 11:", 3, 2), ("Average regular wage/salary, Rs per month", "Table 8:", 3, 2),
        ("NEET % 15-24", "Table 12:", 6, 2), ("NEET % 15-29", "Table 12:", 6, 5)]
rows = []
for label, prefix, n, idx in spec:
    b = block(prefix)
    rows.append([label] + [(first_row(b, nm, n) or ["", "", "", "", "", ""])[idx] for nm in names])
with open(ROOT / "data" / sys.argv[1], "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["indicator (persons)"] + names); w.writerows(rows)
for r in rows: print(r)
