"""Extract the 'Labour Market Snapshot of Selected Districts' (PLFS 2025) headline table: state and district rows.

Indicators: LFPR, WPR, UR for age 15+ (Usual Status ps+ss, rural+urban); NEET for age 15-29.
Needs `pdftotext`. Usage (repo root): python3 -I scripts/extract_plfs_districts.py "raw/plfs/<file>.pdf"
Writes data/plfs2025_district_snapshot.csv. Rows whose district name wraps over two lines are
skipped (reported). '#' (under 250 households) and '*' (RSE >= 40%) flags are kept.
"""
import csv, re, subprocess, sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "plfs2025_district_snapshot.csv"
VAL = r"(-|[\d.]+\*?)"
ROW = re.compile(rf"^\s*(?:(\d+)\.\s+)?(.+?#?)\s+{VAL}\s+{VAL}\s+{VAL}\s+{VAL}\s*$")


def main():
    txt = subprocess.run(["pdftotext", "-layout", sys.argv[1], "-"], capture_output=True, text=True, check=True).stdout
    state, rows, skipped, lines = None, [], 0, txt.splitlines()
    for i, ln in enumerate(lines):
        if re.search(r"State/District\s+LFPR", ln):
            # state name is the nearest non-empty line above the header
            j = i - 1
            while j >= 0 and not lines[j].strip():
                j -= 1
            state = lines[j].strip()
            continue
        m = ROW.match(ln)
        if not (state and m) or "LFPR" in ln:
            continue
        num, name, *vals = m.groups()
        level = "district" if num else ("state" if name.strip() == state else "other")
        rows.append([state, level, name.strip(), *vals])
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["state", "level", "name", "lfpr_15plus", "wpr_15plus", "ur_15plus", "neet_15_29"])
        w.writerows(rows)
    print(f"{len(rows)} rows, {len({r[0] for r in rows})} states -> {OUT}")


if __name__ == "__main__":
    main()
