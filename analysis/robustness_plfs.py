"""Robustness check on 'thin formal entry': compare EPFO formal entry per 100 youth with residence-based PLFS 2025 indicators
that do not depend on EPFO's state attribution.

PLFS annual report tables (rural+urban, persons): Table 19 (workers by status: regular wage/salaried share), Table 35
(non-agricultural workers by enterprise type: share in limited companies, share in government), Table 36 (regular
non-agricultural employees with no specified social security benefit). Plus WPR (Table 23, all levels).
Derived: formal-job density = WPR x regular share x (1 - no-SSB share), per 100 people aged 15+ (rough: the regular share is over all workers,
the no-SSB share is over non-agricultural regular employees).
Output: data/robustness_plfs.csv. Run from repo root: python3 -I analysis/robustness_plfs.py
"""
import csv, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
pdf = next((ROOT / "raw/plfs").glob("*PLFS_2025_F_REV*.pdf"))
pages = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True).stdout.split("\f")
NUM = r"-?[\d,]+(?:\.\d+)?"


def table(tno, label, ncols):
    for p in pages:
        if re.search(rf"Table \({tno}\):", p) and any(re.match(rf"^\s*{label}\s*(persons?)?\s*$", l, re.I) for l in p.splitlines()) and "West Bengal" in p:
            rows = {}
            for l in p.splitlines():
                m = re.match(rf"^\s*([A-Za-z&.\- ]+?)\s+((?:{NUM}\s+){{{ncols-1}}}{NUM})\s*$", l)
                if m:
                    rows[m.group(1).strip()] = [float(v.replace(",", "")) for v in m.group(2).split()]
            return rows
    raise SystemExit(f"table {tno} not found")


t19 = table(19, r"rural\s*\+\s*urban", 6)          # own account, helper, all self, regular, casual, all
t35 = table(35, r"rural\s*\+\s*urban", 10)         # prop, govt, autonomous, company, coop, trust, households, others, total, sample
t36 = table(36, r"rural\s*\+\s*urban", 12)         # M(4) F(4) P(4): no contract, no paid leave, no SSB, all three
wpr = {r["state"]: float(r["value"]) for r in csv.DictReader(open(ROOT / "data/plfs2025_education_by_state.csv"))
       if r["indicator"] == "WPR" and r["sector"] == "rural+urban" and r["sex"] == "persons" and r["education"] == "all"}

epfo = {}
for f in ("large_states_summary.csv", "adjacent_states_summary.csv"):
    for r in csv.DictReader(open(ROOT / "data" / f)):
        if r["epfo_per_100_youth_2023_24"]:
            epfo[r["state"]] = float(r["epfo_per_100_youth_2023_24"])
ALIAS = {"Kerala": "Keralam"}
alias = lambda s, d: d.get(s) or d.get(ALIAS.get(s, s))

out = []
for s, e in sorted(epfo.items(), key=lambda kv: kv[1]):
    reg, comp, govt, nossb, w = alias(s, t19)[3], alias(s, t35)[3], alias(s, t35)[1], alias(s, t36)[10], alias(s, wpr)
    out.append({"state": s, "epfo_per_100_youth": e, "regular_share_of_workers": reg, "company_share_nonagri": comp, "govt_share_nonagri": govt,
                "regular_no_ssb_share": nossb, "wpr_15plus": w, "formal_job_density_per_100": round(w * reg / 100 * (1 - nossb / 100), 1)})


def rank(xs):
    o = sorted(range(len(xs)), key=lambda i: xs[i]); r = [0] * len(xs)
    for k, i in enumerate(o): r[i] = k + 1
    return r


def spearman(a, b):
    ra, rb = rank(a), rank(b); n = len(a)
    return 1 - 6 * sum((x - y) ** 2 for x, y in zip(ra, rb)) / (n * (n * n - 1))


with open(ROOT / "data/robustness_plfs.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for r in out: print(r)
for k in ("regular_share_of_workers", "company_share_nonagri", "govt_share_nonagri", "formal_job_density_per_100"):
    print(k, "Spearman vs EPFO per 100 youth:", round(spearman([r["epfo_per_100_youth"] for r in out], [r[k] for r in out]), 2))
print("n =", len(out))
