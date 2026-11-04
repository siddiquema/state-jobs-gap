"""Extract AISHE Table 33 (state-wise out-turn / pass-out by level) from the raw Excel files.

Reads raw/aishe/*.xlsx, writes data/aishe_outturn_by_state.csv (long format).
Run from repo root:  python3 -I scripts/extract_aishe_outturn.py
Level columns are located from the header row (cells are blank where a state has no data),
and every state row is checked: sum of the level totals must equal the Grand Total.
"""
import csv, sys
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "aishe"
OUT = ROOT / "data" / "aishe_outturn_by_state.csv"

# year -> (file, sheet). Add 2022-23 once its Excel is available.
FILES = {
    "2019-20": ("AISHE Final Report 2019-20.xlsx", "33OutTurnState"),
    "2020-21": ("AISHE Final Report 2020-21.xlsx", "33OutTurnState"),
    "2021-22": ("AISHE Final Report 2021-22.xlsx", "33OutTurnState"),
    "2023-24": ("AISHE Final Report 2023-24 (1).xlsx", "33 Out Turn"),
}
LEVELS = ["Ph.D.", "M.Phil.", "Post Graduate", "Under Graduate", "PG Diploma",
          "Diploma", "Certificate", "Integrated", "Grand Total"]


def num(v):
    return int(v) if isinstance(v, (int, float)) else 0


def parse(year, fname, sheet):
    ws = openpyxl.load_workbook(RAW / fname, read_only=True, data_only=True)[sheet]
    rows = list(ws.iter_rows(values_only=True))
    hdr = next(i for i, r in enumerate(rows) if any(c == "State/UTs" for c in r))
    name_col = list(rows[hdr]).index("State/UTs")
    start = {lvl: c for c, lvl in enumerate(rows[hdr]) if lvl in LEVELS}
    if set(start) != set(LEVELS):
        sys.exit(f"{year}: level headers not found, got {sorted(start)}")
    out, bad = [], []
    for r in rows[hdr + 3:]:
        name = r[name_col]
        if not isinstance(name, str) or not name.strip():
            continue
        rec = {}
        for lvl, c in start.items():
            m, f, t = (num(r[c + k]) for k in range(3))
            rec[lvl] = (m, f, t)
            out.append([year, name.strip(), lvl, m, f, t])
        if sum(rec[l][2] for l in LEVELS[:-1]) != rec["Grand Total"][2]:
            bad.append(name.strip())
    return out, bad


def main():
    OUT.parent.mkdir(exist_ok=True)
    allrows, problems = [], {}
    for y, (f, s) in FILES.items():
        rows, bad = parse(y, f, s)
        allrows += rows
        if bad:
            problems[y] = bad
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "state", "level", "male", "female", "total"])
        w.writerows(allrows)
    print(f"wrote {len(allrows)} rows to {OUT}")
    if problems:
        print("rows where level totals != Grand Total:", problems)


if __name__ == "__main__":
    main()
