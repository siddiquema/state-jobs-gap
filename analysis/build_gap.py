"""Build the West Bengal supply-vs-demand table and chart.

Inputs : data/aishe_outturn_by_state.csv, data/epfo_statewise_net_payroll.csv
Outputs: data/wb_gap.csv, analysis/wb_ug_vs_epfo.svg
Run from repo root: python3 -I analysis/build_gap.py

Alignment is by label only: AISHE academic year 20XX-YY vs EPFO financial year 20XX-YY.
This is a rough alignment; graduates of academic year t mostly join in FY t+1.
EPFO uses the newest release in the file for each year.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YEARS = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]

ug = {r["year"]: int(r["total"]) for r in csv.DictReader(open(ROOT / "data/aishe_outturn_by_state.csv"))
      if r["state"] == "West Bengal" and r["level"] == "Under Graduate"}

epfo = {}   # (period, bucket) -> value, newest release wins
rel = {}
for r in csv.DictReader(open(ROOT / "data/epfo_statewise_net_payroll.csv")):
    if r["state"] != "WEST BENGAL":
        continue
    k = (r["period"], r["age_bucket"])
    if k not in rel or r["release_date"] > rel[k]:
        rel[k], epfo[k] = r["release_date"], int(r["net_payroll"])

rows = []
for y in YEARS:
    all_ages = sum(v for (p, b), v in epfo.items() if p == y)
    a1825 = epfo[(y, "18-21")] + epfo[(y, "22-25")]
    rows.append(dict(year=y, ug_passouts=ug[y], epfo_net_payroll_18_25=a1825, epfo_net_payroll_all_ages=all_ages,
                     ratio_18_25_to_ug=round(a1825 / ug[y], 3), shortfall_ug_minus_18_25=ug[y] - a1825))
with open(ROOT / "data/wb_gap.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

# ---- SVG grouped bar chart (one axis, two series, direct labels) ----
BLUE, ORANGE = "#2a78d6", "#eb6834"
W, H, L, R, T, B = 760, 462, 70, 20, 78, 110
pw, ph = W - L - R, H - T - B
ymax = 500_000
def y(v): return T + ph - v / ymax * ph
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="system-ui,Segoe UI,Arial,sans-serif">',
       f'<rect width="{W}" height="{H}" fill="#fcfcfb"/>',
       f'<text x="{L}" y="26" font-size="17" font-weight="600" fill="#0b0b0b">West Bengal: undergraduate pass-outs vs new formal-sector payroll (age 18-25)</text>',
       f'<text x="{L}" y="46" font-size="12" fill="#52514e">People per year. AISHE academic year vs EPFO financial year, matched by label.</text>']
for t in range(0, ymax + 1, 100_000):
    out.append(f'<line x1="{L}" x2="{W-R}" y1="{y(t):.1f}" y2="{y(t):.1f}" stroke="#e3e2de" stroke-width="1"/>')
    out.append(f'<text x="{L-8}" y="{y(t)+4:.1f}" font-size="11" text-anchor="end" fill="#52514e">{t//1000}k</text>')
gw = pw / len(rows); bw = gw * 0.30
for i, r in enumerate(rows):
    cx = L + gw * (i + 0.5)
    for j, (key, col) in enumerate([("ug_passouts", BLUE), ("epfo_net_payroll_18_25", ORANGE)]):
        v = r[key]; x = cx + (j - 1) * bw + (1 if j else -1) * 1  # 2px gap
        out.append(f'<path d="M{x:.1f},{y(0):.1f} V{y(v)+4:.1f} a4,4 0 0 1 4,-4 h{bw-8:.1f} a4,4 0 0 1 4,4 V{y(0):.1f} Z" fill="{col}"><title>{r["year"]} {key.replace("_"," ")}: {v:,}</title></path>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{y(v)-5:.1f}" font-size="11" text-anchor="middle" fill="#0b0b0b">{v/1000:.0f}k</text>')
    out.append(f'<text x="{cx:.1f}" y="{y(0)+18:.1f}" font-size="12" text-anchor="middle" fill="#0b0b0b">{r["year"]}</text>')
out.append(f'<line x1="{L}" x2="{W-R}" y1="{y(0):.1f}" y2="{y(0):.1f}" stroke="#52514e"/>')
ly = H - 76
out += [f'<rect x="{L}" y="{ly}" width="12" height="12" rx="2" fill="{BLUE}"/><text x="{L+18}" y="{ly+10}" font-size="12" fill="#0b0b0b">Undergraduate pass-outs (AISHE Table 33)</text>',
        f'<rect x="{L+290}" y="{ly}" width="12" height="12" rx="2" fill="{ORANGE}"/><text x="{L+308}" y="{ly+10}" font-size="12" fill="#0b0b0b">EPFO net new payroll, age 18-25 (state tables)</text>',
        f'<text x="{L}" y="{H-44}" font-size="11" fill="#52514e">Not "jobs created": EPFO net payroll counts new subscribers minus exits plus rejoiners, formal sector only.</text>',
        f'<text x="{L}" y="{H-8-14}" font-size="11" fill="#52514e">AISHE 2023-24 fall is unexplained (see analysis/aishe_quality_check.md).</text>',
        f'<text x="{L}" y="{H-8}" font-size="11" fill="#52514e">Sources: AISHE final reports; EPFO payroll release of 20 Sep 2025.</text>',
        '</svg>']
(ROOT / "analysis/wb_ug_vs_epfo.svg").write_text("\n".join(out))
for r in rows: print(r)
