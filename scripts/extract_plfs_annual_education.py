"""Extract PLFS 2025 Annual Report Tables 22-24 (LFPR / WPR / UR by highest education level, Usual Status ps+ss,
age 15+) for every State/UT plus all-India.

Needs `pdftotext`. Usage (repo root): python3 -I scripts/extract_plfs_annual_education.py "<annual report pdf>"
Writes data/plfs2025_education_by_state.csv (long): table, indicator, sector, sex, state, education, value.
Each page is identified by its own title ("Table (N)") and its "<sector> <sex>" label line, not by line position.
Education columns (confirmed from the printed header of Table 24): see EDU below.
"""
import csv, re, subprocess, sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "plfs2025_education_by_state.csv"
EDU = ["not literate", "literate & up to primary", "middle", "secondary", "higher secondary",
       "diploma/certificate course", "graduate", "post graduate & above", "secondary & above", "all"]
IND = {"22": "LFPR", "23": "WPR", "24": "UR"}
NUM = r"-?\d+(?:\.\d+)?\*?"
ROW = re.compile(rf"^\s*([A-Za-z&.\- ]+?)\s+((?:{NUM}\s+){{9}}{NUM})\s*$")
LABEL = re.compile(r"^\s*(rural\s*\+\s*urban|rural|urban)\s+(males?|females?|persons?)\s*$", re.I)


def main():
    txt = subprocess.run(["pdftotext", "-layout", sys.argv[1], "-"], capture_output=True, text=True, check=True).stdout
    rows, pages_used = [], 0
    for page in txt.split("\f"):
        m = re.search(r"Table \((22|23|24)\):", page)
        if not m:
            continue
        label = next((LABEL.match(l) for l in page.splitlines() if LABEL.match(l)), None)
        if not label:
            continue
        sector = re.sub(r"\s", "", label.group(1)).lower()
        sex = label.group(2).lower().rstrip("s") if label.group(2).lower() != "females" else "female"
        sex = {"person": "persons"}.get(sex, sex)
        n = 0
        for l in page.splitlines():
            r = ROW.match(l)
            if r and not re.match(r"\s*State", l):
                for edu, v in zip(EDU, r.group(2).split()):
                    rows.append([m.group(1), IND[m.group(1)], sector, sex, r.group(1).strip(), edu, v])
                n += 1
        pages_used += 1
        if n not in (36, 37):
            print(f"  note: page with Table {m.group(1)} {sector} {sex} has {n} state rows")
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["table", "indicator", "sector", "sex", "state", "education", "value"])
        w.writerows(rows)
    print(f"{len(rows)} values from {pages_used} table pages -> {OUT}")


if __name__ == "__main__":
    main()
