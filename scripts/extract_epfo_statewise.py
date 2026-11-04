"""Extract state-wise net payroll by age bucket from an EPFO 'Provisional Monthly Estimate of Payroll' PDF.

Source page: https://www.epfo.gov.in/data-hub/   (needs `pdftotext` from poppler)
Usage (repo root):  python3 -I scripts/extract_epfo_statewise.py "raw/epfo/<file>.pdf" <release-date YYYY-MM-DD>
Appends/overwrites rows for that release in data/epfo_statewise_net_payroll.csv (long format):
release_date, age_bucket, state, period, net_payroll
Check: state values per age bucket and period are summed and compared with the national
age-bucket table on page 1 of the same PDF; differences are printed, not hidden.
"""
import csv, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "epfo_statewise_net_payroll.csv"
NUM = r"-?\d+"


def text_of(pdf):
    return subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True).stdout


def parse(txt):
    """Returns periods, state rows, and the SUB TOTAL row of each age bucket (from the state section only)."""
    periods, bucket, rows, subtotals, in_state = None, None, [], {}, False
    for line in txt.splitlines():
        if "STATEWISE NEW PAYROLL DATA" in line:
            in_state = True
        elif "INDUSTRY WISE PAYROLL DATA" in line:
            in_state = False
        if not in_state:
            continue
        m = re.match(r"\s*Age Bucket:\s*(.+?)\s*$", line)
        if m:
            bucket = m.group(1)
            continue
        if bucket and re.match(r"\s*State\s+2017-18", line):
            periods = line.split()[1:]
            continue
        if not (bucket and periods):
            continue
        m = re.match(rf"^\s*([A-Z][A-Z &.,'()/-]*?[A-Z.)])\s+((?:{NUM}\s+){{{len(periods)-1}}}{NUM})\s*$", line)
        if m:
            vals = [int(v) for v in m.group(2).split()]
            name = m.group(1).strip()
            if name in ("SUB TOTAL", "TOTAL"):
                subtotals[(bucket, name)] = dict(zip(periods, vals))
            else:
                rows += [(bucket, name, p, v) for p, v in zip(periods, vals)]
    return periods, rows, subtotals


def national(txt, periods):
    """National net payroll by age bucket from page 1 (annual rows 2018-19.. and monthly rows)."""
    buckets = ["Less than 18", "18-21", "22-25", "26-28", "29-35", "More than 35"]
    nat = {}
    for line in txt.splitlines()[:40]:
        m = re.match(rf"^\s*(\d{{4}}-\d{{2}}|[A-Z][a-z]{{2}}-\d{{4}})\s+((?:{NUM}\s+){{7}}{NUM})\s*$", line)
        if m:
            vals = [int(v) for v in m.group(2).split()]
            key = m.group(1)
            key = key[:3] + "-" + key[-2:] if re.match(r"[A-Z][a-z]{2}-\d{4}", key) else key
            for b, v in zip(buckets, vals[:6]):
                nat[(b, key)] = v
    return nat


def main():
    pdf, rel = Path(sys.argv[1]), sys.argv[2]
    txt = text_of(pdf)
    periods, rows, subtotals = parse(txt)
    if not rows:
        sys.exit("no state rows parsed")
    nat = national(txt, periods)
    sums = {}
    for b, s, p, v in rows:
        sums[(b, p)] = sums.get((b, p), 0) + v
    # check 1: sum of state rows vs the table's own SUB TOTAL row (exact parse check)
    d1 = [(k, sums[k], subtotals[(k[0], "SUB TOTAL")][k[1]]) for k in sums
          if (k[0], "SUB TOTAL") in subtotals and sums[k] != subtotals[(k[0], "SUB TOTAL")][k[1]]]
    # check 2: sum of state rows vs national age-bucket table on page 1 (EPFO's own tables differ slightly)
    d2 = [(k, sums[k], nat[k]) for k in sums if k in nat and sums[k] != nat[k]]
    print(f"{len(rows)} rows, {len({r[1] for r in rows})} state/UT labels, {len(sums)} bucket-periods")
    print(f"state sum != SUB TOTAL row: {len(d1)}; state sum != national page-1 table: {len(d2)} of {sum(1 for k in sums if k in nat)}")
    for k, a, b in d1[:8]:
        print("  vs SUB TOTAL:", k, a, b)
    for k, a, b in sorted(d2, key=lambda t: -abs(t[1]-t[2]))[:5]:
        print("  vs national:", k, a, b)
    old = []
    if OUT.exists():
        old = [r for r in csv.reader(open(OUT)) if r and r[0] != rel and r[0] != "release_date"]
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["release_date", "age_bucket", "state", "period", "net_payroll"])
        w.writerows(old)
        w.writerows([(rel, *r) for r in rows])


if __name__ == "__main__":
    main()
