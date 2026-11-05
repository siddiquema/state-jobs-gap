"""Build the report PDF. Refuses to run unless report/validate.py passes. Every number comes from validated data (facts.py, validated_values.json).
Run from the repo root: python3 -I report/build_report.py   (needs node with Playwright's Chromium)
"""
import csv, json, subprocess, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import facts, charts as C

if subprocess.run([sys.executable, "-I", str(HERE / "validate.py")]).returncode != 0:
    sys.exit("validation failed: no report produced")
F = facts.build()
V = json.load(open(HERE / "validated_values.json"))
LOG = list(csv.DictReader(open(HERE / "validation_log.csv")))

S, R, EP = F["states"], F["robust"], F["ep"]
fy = F["wb_fy"]
HUB = ["Tamil Nadu", "Telangana", "Karnataka", "Maharashtra"]
n = lambda v: f"{v:,.0f}"
m1 = lambda v: f"{v/1e6:.2f} million"
k = lambda v: f"{round(v/1000):,}"
per100 = lambda s: float(S[s]["epfo_per_100_youth_2023_24"])
ug_per = lambda s: float(S[s]["ug_per_100_youth_2023_24"])
hub100 = [per100(h) for h in HUB]
edu = F["edu"]
E = lambda ind, st, e, sex="persons": edu[(ind, "rural+urban", sex, st, e)]
wbd = float(R["West Bengal"]["formal_job_density_per_100"])
dens = [float(R[h]["formal_job_density_per_100"]) for h in HUB]
reg = [float(R[h]["regular_share_of_workers"]) for h in HUB]
comp = [float(R[h]["company_share_nonagri"]) for h in HUB]
nossb = [float(R[h]["regular_no_ssb_share"]) for h in HUB]
a25 = sum(F["wb_month"][m] for m in ("Apr-25", "May-25", "Jun-25", "Jul-25"))
a24 = sum(F["wb_month"][m] for m in ("Apr-24", "May-24", "Jun-24", "Jul-24"))
pct25 = round((a25 / a24 - 1) * 100)
ug5, ep5 = F["wb_ug_5yr"], F["ep_5yr"]
sc = F["scen"]
wages = V["wages"]
ranked = sorted(wages, key=wages.get)
IND = V["india"]
wb_ug24 = F["wb_ug"]["2023-24"]
BR = F["bridge"]
MIN = "\u2212"
mil = lambda v: f"{abs(v)/1e6:.2f}"
smil = lambda v: (MIN if v < 0 else "+") + mil(v)
RES = [BR["res_pg_1825"], BR["res_pg_2225"], BR["res_nopg_1825"], BR["res_nopg_2225"]]
r_lo, r_hi = min(RES), max(RES)
moe_state, moe_sub = facts.margin_of_error(15000), facts.margin_of_error(1250)
fem_share = round(wb_ug24[1] / wb_ug24[2] * 100)


def rho(a, b):
    def rk(x):
        o = sorted(range(len(x)), key=lambda i: x[i]); r = [0] * len(x)
        for q, i in enumerate(o): r[i] = q + 1
        return r
    ra, rb, m = rk(a), rk(b), len(a)
    return 1 - 6 * sum((p - q) ** 2 for p, q in zip(ra, rb)) / (m * (m * m - 1))
sts = list(R); e_ = [float(R[s]["epfo_per_100_youth"]) for s in sts]
rho_c, rho_d, rho_r = (rho(e_, [float(R[s][c]) for s in sts]) for c in ("company_share_nonagri", "formal_job_density_per_100", "regular_share_of_workers"))

CSS = f"""
@page {{ size: 297mm 210mm; margin: 0 }}
* {{ box-sizing: border-box }}
body {{ margin:0; font-family:'Liberation Sans',Arial,sans-serif; color:{C.NAVY}; font-size:10.5pt; line-height:1.38 }}
.slide {{ width:297mm; height:210mm; padding:13mm 16mm 11mm 16mm; page-break-after:always; position:relative; overflow:hidden; background:#fff }}
.tracker {{ font-size:8pt; letter-spacing:.09em; text-transform:uppercase; color:{C.MID}; margin-bottom:3mm }}
h1.title {{ font-family:'Liberation Serif',Georgia,serif; font-weight:normal; font-size:21pt; line-height:1.16; margin:0 0 4mm 0; max-width:255mm }}
.rule {{ border-top:1.4px solid {C.NAVY}; margin-bottom:5mm }}
.cols {{ display:flex; gap:9mm }} .main {{ flex:1.75; min-width:0 }} .side {{ flex:1; min-width:0 }}
.exh {{ font-size:9pt; font-weight:bold; margin:0 0 1mm }} .exs {{ font-size:8.8pt; color:{C.MID}; margin:0 0 2.5mm }}
.side h3 {{ font-size:10pt; margin:0 0 2mm; padding-bottom:1.5mm; border-bottom:1px solid {C.RULE} }}
.side ul, ul.t {{ padding-left:4.5mm; margin:0 }} .side li, ul.t li {{ margin-bottom:2.2mm }}
.src {{ position:absolute; left:16mm; right:16mm; bottom:8mm; font-size:7.6pt; color:{C.MID}; border-top:1px solid {C.LIGHT}; padding-top:1.6mm }}
.pg {{ position:absolute; right:16mm; bottom:3.2mm; font-size:7.6pt; color:{C.MID} }}
table {{ border-collapse:collapse; width:100%; font-size:9pt }}
th {{ text-align:left; font-weight:bold; border-bottom:1.4px solid {C.NAVY}; padding:1.6mm 2mm; vertical-align:bottom }}
td {{ border-bottom:1px solid {C.LIGHT}; padding:1.7mm 2mm; vertical-align:top }}
td.n, th.n {{ text-align:right; white-space:nowrap }} tr.hl td {{ background:#EEF2FF; font-weight:bold }}
.tag {{ display:inline-block; font-size:7.6pt; font-weight:bold; letter-spacing:.04em; padding:.4mm 1.8mm; border:1px solid {C.NAVY}; margin-right:1.5mm; text-transform:uppercase }}
.tag.inf {{ border-color:{C.BLUE}; color:{C.BLUE} }}
.big {{ font-family:'Liberation Serif',serif; font-size:26pt; line-height:1; color:{C.BLUE} }}
.kpi {{ display:flex; gap:6mm; margin:2mm 0 4mm }} .kpi div {{ flex:1; border-top:2px solid {C.NAVY}; padding-top:1.5mm; font-size:8.8pt }}
.cover {{ background:{C.NAVY}; color:#fff }} .cover h1 {{ font-family:'Liberation Serif',serif; font-weight:normal; font-size:33pt; line-height:1.12; margin:38mm 0 8mm; max-width:215mm }}
.cover .sub {{ font-size:14pt; color:#C8D3E0; max-width:200mm }} .cover .meta {{ position:absolute; left:16mm; bottom:16mm; font-size:10pt; color:#C8D3E0; line-height:1.6 }}
.cover .bar {{ width:30mm; border-top:4px solid {C.BLUE}; margin-top:12mm }}
.callout {{ background:#EEF2FF; border-left:3px solid {C.BLUE}; padding:2.5mm 3.5mm; margin-top:3mm; font-size:9.4pt }}
.three {{ display:flex; gap:7mm }} .three > div {{ flex:1; border-top:2px solid {C.NAVY}; padding-top:2mm }} .three h3 {{ font-size:11.5pt; margin:0 0 2mm }} .three.lg {{ font-size:11.5pt; line-height:1.45 }}
"""

slides = []


def slide(tracker, title, body, source, cls=""):
    slides.append(f'<section class="slide {cls}"><div class="tracker">{tracker}</div><h1 class="title">{title}</h1><div class="rule"></div>{body}<div class="src">{source}</div><div class="pg">{{pg}}</div></section>')


def exhibit(num, title, sub, svg):
    return f'<p class="exh">Exhibit {num}: {title}</p><p class="exs">{sub}</p>{svg}'


def side(head, items):
    return f'<div class="side"><h3>{head}</h3><ul>{"".join(f"<li>{i}</li>" for i in items)}</ul></div>'


# ---------------- cover
slides.append(f'''<section class="slide cover"><div class="bar"></div>
<h1>West Bengal's graduates and formal jobs: what public data can and cannot say</h1>
<div class="sub">A response to a public question on jobs created, joining dates and planned migration, with the wider picture the question did not ask for</div>
<div class="meta">Prepared for Kuunal Chatterjee<br>5 November 2026<br>Built entirely from public data: all figures re-derived from source files and independently validated ({len(LOG)} checks)</div></section>''')

# ---------------- executive summary
exec_items = [
    "<b>Public data answers the question only in part.</b> It measures formal job entry. It does not give company-level joining dates, a count of graduates who leave, or a state target. Treat every figure here as a directional indicator, not a decision-grade estimate.",
    f"<b>Jobs created:</b> West Bengal recorded {k(fy['2024-25']['all'])},000 net new formal-sector workers in 2024-25, {k(fy['2024-25']['y1825'])},000 of them aged 18 to 25. Formal work only; it includes people who left and rejoined, so it is not a count of first jobs.".replace(",000,000", ",000"),
    f"<b>The graduate gap cannot be read as unplaced graduates.</b> Raw, the state's institutions produced {m1(ug5)} undergraduate graduates over five years against {m1(ep5)} formal entrants aged 18 to 25. The two counts differ in place, age, kind and period. Once further study and non-participation are allowed for, the remainder is between {smil(r_lo)} and {smil(r_hi)} million depending on the age band used, and it could be informal or government work, non-graduate entrants, or moves out of state.",
    f"<b>The stronger finding needs no graduate assumption:</b> per 100 young people, Tamil Nadu, Telangana, Karnataka and Maharashtra record {min(hub100):.1f} to {max(hub100):.1f} formal entrants a year, West Bengal {per100('West Bengal'):.1f} and its four neighbours {min(per100(s) for s in ('Odisha','Jharkhand','Bihar','Assam')):.1f} to {max(per100(s) for s in ('Odisha','Jharkhand','Bihar','Assam')):.1f}. A household survey orders the states the same way, which supports the pattern but not EPFO's exact levels.",
    f"<b>Job quality:</b> {R['West Bengal']['regular_no_ssb_share']}% of West Bengal's regular non-farm jobs carry no social security (India {IND['nossb']}%). Graduate unemployment is {E('UR','West Bengal','graduate')}%, close to India's {E('UR','all India','graduate')}%, and about {round(E('LFPR','West Bengal','graduate','female'))}% of women graduates are in the labour force.",
    "<b>No state target for stopping migration was found,</b> but the state's budget speeches, policies and summit papers have not been read, so the question stays open. Pages 16 and 17 set out a graduate tracking study and three defined indicators that would give decision-grade answers.",
]
slide("Executive summary", "Public data shows thin formal job entry that West Bengal shares with several states; it does not show how many graduates are unplaced or leave",
      f'<div style="max-width:262mm"><ul class="t" style="font-size:10.4pt">{"".join(f"<li style=margin-bottom:2.6mm>{i}</li>" for i in exec_items)}</ul></div>',
      "Source: AISHE final reports 2019-20 to 2023-24; EPFO provisional payroll estimates (20 Jan and 20 Sep 2025); PLFS 2025 annual report, district snapshot and million-plus cities report; team analysis")

# ---------------- what can be answered
rows3 = [
    ("How many jobs have been created?", "EPFO net new formal payroll by state and age band", f"{k(fy['2024-25']['all'])},000 in 2024-25, {k(fy['2024-25']['y1825'])},000 aged 18 to 25. Formal work only; includes people who rejoined, so not a count of first jobs", "Partly answered"),
    ("When do people join?", "EPFO monthly totals by state", "Monthly totals for Apr to Nov 2024 and Apr to Jul 2025. No company-level dates found", "Partly answered"),
    ("How many migrations are planned to be stopped?", "None: no public series counts graduates who leave; no state target found", f"A gap of {F['gap_lf']/1e6:.2f} to {F['gap_baseline']/1e6:.1f} million between graduates and formal entry, which is not a migration count", "Not answerable; target search incomplete"),
]
tb = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td><b>{d}</b></td></tr>" for a, b, c, d in rows3).replace(",000,000", ",000")
slide("The question", "Public data answers the question in part: it measures formal job entry and a graduate gap, not joining dates, migration or targets",
      f'<p style="max-width:240mm">The question asked how many jobs have been created in West Bengal, when people join, and how many migrations are planned to be stopped over two years, given the graduates the state produces. Exhibit 1 sets each part against what public sources can offer.</p>'
      f'<p class="exh" style="margin-top:4mm">Exhibit 1: The three questions against public data</p><table><tr><th style="width:22%">Question asked</th><th style="width:25%">Closest public measure</th><th>What it can show</th><th style="width:15%">Status</th></tr>{tb}</table>'
      '<div class="three lg" style="margin-top:9mm"><div><h3>Part 1 · Your three questions</h3>Pages 4 to 6 take jobs created, joining dates and migration in turn, with what the data can and cannot say.</div><div><h3>Part 2 · What you did not ask</h3>Pages 7 to 17 cover the size of the gap and how far it can be read, how West Bengal compares, job quality, graduates, Kolkata, and a design that would settle the question.</div><div><h3>Appendices</h3>Sources, limits, and how every figure was validated before this report was produced.</div></div>',
      "Source: EPFO provisional payroll estimates; AISHE final reports; team analysis")

# ---------------- Q1
cats = facts.FYS
q1 = C.grouped_columns(cats, [("All ages", C.GREY, [fy[c]["all"] for c in cats]), ("Ages 18 to 25", C.BLUE, [fy[c]["y1825"] for c in cats])], width=660, height=380)[0]
y_last3 = [fy[c]["y1825"] for c in ("2022-23", "2023-24", "2024-25")]
slide("Part 1 · Question 1 · Jobs created", f"West Bengal's net formal payroll additions peaked at {k(fy['2022-23']['all'])},000 in 2022-23 and have eased to {k(fy['2024-25']['all'])},000 in 2024-25".replace(",000,000", ",000"),
      '<div class="cols"><div class="main">' + exhibit(2, "Net new formal-sector payroll, West Bengal", "People per financial year (April to March)", q1) + "</div>" +
      side("What the figure is, and is not", [
          f"The 18 to 25 age group has stayed between {k(min(y_last3))},000 and {k(max(y_last3))},000 for three years.".replace(",000,000", ",000"),
          "It counts new provident-fund members, less those who left, plus those who rejoined.",
          "It covers the formal sector only. Rejoiners are included, so it is not a count of first jobs and can overstate new ones. Informal work is not counted.",
          f"For context, regular wage or salaried work makes up {R['West Bengal']['regular_share_of_workers']}% of West Bengal's workers (India {IND['regular']}%).",
      ]) + "</div>",
      "Source: EPFO provisional monthly payroll estimates, releases of 20 Jan and 20 Sep 2025 (state tables); PLFS 2025 annual report, Table 19; team analysis")

# ---------------- Q2
MONTHS = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
m24 = [F["wb_month"].get(f"{m}-24") for m in MONTHS]
m25 = [F["wb_month"].get(f"{m}-25") for m in MONTHS]
q2 = C.grouped_columns(MONTHS, [("2024", C.GREY, m24), ("2025 (provisional)", C.BLUE, m25)], width=660, height=380)[0]
slide("Part 1 · Question 2 · Joining dates", f"On provisional figures, April to July 2025 added about {pct25}% more net formal payroll than a year earlier; no company-level joining dates were found",
      '<div class="cols"><div class="main">' + exhibit(3, "Net new formal-sector payroll by month, West Bengal", "People per month, all ages", q2) + "</div>" +
      side("Reading the months", [
          f"April to July 2025 added {n(a25)} against {n(a24)} in the same months of 2024.",
          "The comparison is not like for like: 2025 months have had less time to be updated, and both are provisional.",
          "October 2024 is the low month in West Bengal, as it is nationally.",
          "The two releases used do not cover December 2024 to March 2025 month by month.",
          "Monthly totals by state and age band are the finest breakdown in the releases reviewed. No company-level joining dates were found.",
      ]) + "</div>",
      "Source: EPFO provisional monthly payroll estimates, releases of 20 Jan 2025 (Apr to Nov 2024) and 20 Sep 2025 (Apr to Jul 2025); team analysis")

# ---------------- Q3
slide("Part 1 · Question 3 · Migration", "Public data does not count graduates who leave, and no state target was found, though the search is incomplete",
      f'''<div class="three"><div><h3>What public data offers</h3><ul class="t"><li>A gap between graduates produced and formal job entry: {F['gap_lf']/1e6:.2f} to {F['gap_baseline']/1e6:.1f} million over five years, and why it cannot be read as unplaced graduates (pages 7 and 8)</li><li>Survey measures of unemployment and of young people not working or studying</li><li>Occasional national migration surveys exist; they were not reviewed for this report and are not specific to graduates</li></ul></div>
<div><h3>What is missing</h3><ul class="t"><li>A public count of graduates who leave the state</li><li>A state target. The budget speeches, IT and industrial policies and summit papers could not be read for this report, so we can neither confirm nor deny that a white paper exists</li></ul></div>
<div><h3>What a target would need</h3><ul class="t"><li>A definition: leaving for study or for work, for how long, and which graduates</li><li>A baseline measured the same way each year</li><li>Linked records from graduates' institutions to later employment</li></ul></div></div>
<div class="callout"><b>Why this matters.</b> Graduates who study further, work informally or for government, or are out of work all sit inside the gap. Without a definition, any number put on "migrations stopped" cannot be checked.</div>''',
      "Source: team analysis; AISHE, EPFO and PLFS as cited on the following pages")

# ---------------- gap
gy = facts.YEARS
q4 = C.grouped_columns(gy, [("Undergraduate pass-outs", C.GREY, [F["gap"][y]["ug"] for y in gy]), ("Formal entrants aged 18 to 25", C.BLUE, [F["gap"][y]["ep"] for y in gy])], width=620, height=360, sub=[f"{F['gap'][y]['ep']/F['gap'][y]['ug']:.2f}" for y in gy])[0]
pct_fall = abs(round((F["wb_ug"]["2023-24"][2] / F["wb_ug"]["2022-23"][2] - 1) * 100))
scen_rows = [("Baseline: ages 18 to 25 against all pass-outs", sc["A"]), ("Graduate-age band only (22 to 25)", sc["B"]), ("One-year lag in joining", sc["C"]), ("Pass-outs counted only if in the labour force", sc["D"])]
st_tbl = "<table><tr><th>The raw ratio under four assumptions</th><th class='n'>Entrants per graduate</th></tr>" + "".join(f"<tr><td>{a}</td><td class='n'><b>{b:.2f}</b></td></tr>" for a, b in scen_rows) + "</table>"
slide("Part 2 · The size of the gap", f"Counted raw, formal entry by 18 to 25-year-olds is below graduate output every year, but the two counts are not like for like",
      '<div class="cols"><div class="main">' + exhibit(4, "Undergraduate pass-outs and formal entrants, West Bengal", "People per year. The figure under each year is formal entrants per pass-out", q4) + "</div>" +
      f'<div class="side"><h3>Raw ratio, before any adjustment</h3>{st_tbl}<ul style="margin-top:3mm"><li>Over five years: <b>{n(ug5)}</b> pass-outs against <b>{n(ep5)}</b> formal entrants.</li><li>The raw difference is <b>{F["gap_lf"]/1e6:.2f} to {F["gap_baseline"]/1e6:.1f} million</b>. The next page shows why it cannot be read as unplaced graduates.</li><li>Pass-outs for 2023-24 fall {pct_fall}% for reasons the data does not explain, so five-year totals are used.</li></ul></div></div>',
      "Note: AISHE academic years are matched to EPFO financial years by label; graduates mostly join the year after. Source: AISHE final reports 2019-20 to 2023-24 (Table 33); EPFO payroll estimates (state tables); PLFS 2025 (graduate participation by sex); team analysis")

# ---------------- reading the gap
items8 = [("Undergraduate\npass-outs", BR["ug"] / 1e6, "total", C.GREY),
          ("Continue to a\nmaster's (proxy)", BR["pg"] / 1e6, "down", C.NAVY),
          ("Outside the\nlabour force", BR["out_lf"] / 1e6, "down", C.NAVY),
          ("Unemployed", BR["unemployed"] / 1e6, "down", C.NAVY),
          ("Employed\ngraduates (est.)", BR["employed"] / 1e6, "total", C.GREY),
          ("Formal entrants\nages 18 to 25", BR["formal_1825"] / 1e6, "ref", C.BLUE),
          ("Formal entrants\nages 22 to 25", BR["formal_2225"] / 1e6, "ref", C.BLUE)]
q4b = C.bridge(items8, width=640, height=285)
case_rows = [("Master's deducted, ages 18 to 25", BR["employed"], BR["formal_1825"], BR["res_pg_1825"]), ("Master's deducted, ages 22 to 25", BR["employed"], BR["formal_2225"], BR["res_pg_2225"]),
             ("No master's deduction, ages 18 to 25", BR["employed_no_pg"], BR["formal_1825"], BR["res_nopg_1825"]), ("No master's deduction, ages 22 to 25", BR["employed_no_pg"], BR["formal_2225"], BR["res_nopg_2225"])]
case_tbl = "<table><tr><th>Case</th><th class='n'>Employed graduates</th><th class='n'>Formal entrants</th><th class='n'>Remainder</th></tr>" + "".join(
    f"<tr><td>{a}</td><td class='n'>{mil(b)}</td><td class='n'>{mil(c)}</td><td class='n'><b>{smil(d)}</b></td></tr>" for a, b, c, d in case_rows) + "</table>"
mism = [("Place", "Pass-outs are counted by the institution's state; EPFO assigns workers to states by a method it does not state. Students, graduates and workers cross state lines."),
        ("Age", "Pass-outs are graduates of any age; payroll entrants are aged 18 to 25 and include people who are not graduates; population is aged 18 to 23."),
        ("Kind", "Payroll is a flow of new entrants. The household survey used to check it counts a stock of people in work."),
        ("Period", "Academic years run July to June, financial years April to March, and graduates mostly join the year after.")]
mism_html = "".join(f"<li><b>{a}.</b> {b}</li>" for a, b in mism)
slide("Part 2 · Reading the gap", f"Allowing for further study and non-participation, the remainder is {smil(r_lo)} to {smil(r_hi)} million; it is not a count of unplaced graduates",
      '<div class="cols"><div class="main">' + exhibit(5, "From undergraduate pass-outs to employed graduates, West Bengal, five years", "Millions of people, 2019-20 to 2023-24; illustrative, with the assumptions in the note below", q4b) +
      f'<div style="margin-top:3mm">{case_tbl}</div></div>' +
      f'<div class="side"><h3>Read with care: four mismatches</h3><ul>{mism_html}</ul><div class="callout"><b>What the remainder could be.</b> Informal or government work, formal entrants who are not graduates, people who moved in from other states, and graduates working in other states. This data cannot separate them.</div></div></div>',
      f"Note: continuing to a master's is proxied by postgraduate pass-outs in the same five years ({mil(BR['pg'])} million, {round(BR['pg']/BR['ug']*100)}% of undergraduate pass-outs), which also include students from elsewhere. Participation by sex and the unemployment rate are the 2025 survey's graduate figures. Source: AISHE final reports (Table 33); EPFO payroll estimates; PLFS 2025 annual report, Tables 22 and 24; team analysis")

# ---------------- peers
GROUP = {"West Bengal": ("West Bengal", C.BLUE), "Odisha": ("n", C.NAVY), "Jharkhand": ("n", C.NAVY), "Bihar": ("n", C.NAVY), "Assam": ("n", C.NAVY)}
order = sorted(["West Bengal", "Odisha", "Jharkhand", "Bihar", "Assam", "Andhra Pradesh", "Kerala", "Tamil Nadu", "Telangana", "Karnataka", "Maharashtra"], key=lambda s: -per100(s))
rows_h = [(s, per100(s), C.BLUE if s == "West Bengal" else (C.NAVY if s in ("Odisha", "Jharkhand", "Bihar", "Assam") else C.GREY), s == "West Bengal") for s in order]
q5 = C.hbars(rows_h, width=620, row_h=24, label_w=110, legend_items=[("West Bengal", C.BLUE), ("Neighbouring states", C.NAVY), ("Other large states", C.GREY)])
ug_lo, ug_hi = min(ug_per(h) for h in HUB), max(ug_per(h) for h in HUB)
slide("Part 2 · Not only West Bengal", f"Without any graduate assumption, four large states record {min(hub100):.1f} to {max(hub100):.1f} formal entrants per 100 young people and West Bengal {per100('West Bengal'):.1f}; its neighbours record less",
      '<div class="cols"><div class="main">' + exhibit(6, "Net new formal payroll aged 18 to 25 per 100 people aged 18 to 23, 2023-24", "Formal entrants a year per 100 young people", q5) + "</div>" +
      side("What stands out", [
          f"West Bengal's four neighbours record {per100('Bihar'):.1f} (Bihar) to {per100('Odisha'):.1f} (Odisha).",
          f"Andhra Pradesh ({per100('Andhra Pradesh'):.1f}) and Kerala ({per100('Kerala'):.1f}) look like West Bengal on this measure; Kerala does not on the survey measure (next page).",
          f"West Bengal's graduate output per young person ({ug_per('West Bengal'):.1f} per 100) is {round(ug_per('West Bengal')/max(ug_per(h) for h in HUB)*100)}% to {round(ug_per('West Bengal')/min(ug_per(h) for h in HUB)*100)}% of the four large states' ({ug_lo:.1f} to {ug_hi:.1f}). Both parts of the ratio differ, but formal entry differs far more.",
          "Payroll entrants are aged 18 to 25 and the population 18 to 23. The same mismatch applies to every state, so the order is less affected than the levels.",
          "EPFO does not say how it assigns workers to states. If it uses the employer's registered state, Maharashtra's and Karnataka's figures could be inflated by head-office registration.",
      ]) + "</div>",
      "Source: EPFO provisional payroll estimates (Sep 2025 release, state tables); AISHE final report 2023-24 (Table 38, population aged 18 to 23); team analysis")

# ---------------- survey check
pts = [(s, float(R[s]["company_share_nonagri"]), float(R[s]["epfo_per_100_youth"])) for s in R]
q6 = C.scatter(pts, width=600, height=320, xlab="Share of non-farm workers in limited companies, household survey", ylab="EPFO formal entrants per 100 young people", label_set=("West Bengal", "Kerala", "Maharashtra", "Bihar", "Karnataka", "Tamil Nadu", "Telangana"))
tbl6 = "<table><tr><th></th><th class='n'>West Bengal</th><th class='n'>Four large states</th></tr>" + \
    f"<tr><td>Formal-job density per 100 people aged 15+</td><td class='n'><b>{wbd:.1f}</b></td><td class='n'>{min(dens):.1f} to {max(dens):.1f}</td></tr>" + \
    f"<tr><td>Non-farm workers in limited companies</td><td class='n'><b>{R['West Bengal']['company_share_nonagri']}%</b></td><td class='n'>{min(comp):.1f}% to {max(comp):.1f}%</td></tr></table>"
slide("Part 2 · A second source", "A household survey orders the states the same way, which supports the pattern but cannot confirm EPFO's levels",
      '<div class="cols"><div class="main">' + exhibit(7, "EPFO formal entry against the survey's share of non-farm workers in limited companies", "Eleven states with both measures", q6) + "</div>" +
      f'<div class="side"><h3>Does the pattern survive a different source?</h3>{tbl6}<ul style="margin-top:3mm"><li>EPFO counts a flow of new entrants; the survey counts a stock of people in work. Ordering the states alike does not show that EPFO\'s figures are accurate or comparable across states.</li><li>Rank correlation with EPFO: <b>{rho_c:.2f}</b> (limited-company share), <b>{rho_d:.2f}</b> (formal-job density), <b>{rho_r:.2f}</b> (regular salaried share). Eleven states, so indicative.</li><li>West Bengal\'s density is <b>{wbd/max(dens):.2f} to {wbd/min(dens):.2f}</b> of the large states\', a smaller gap than EPFO shows, though on a different kind of measure.</li><li>Kerala is the exception: {R["Kerala"]["regular_share_of_workers"]}% of its workers are in regular salaried work, yet EPFO shows {R["Kerala"]["epfo_per_100_youth"]} entrants per 100. EPFO may understate its formal jobs.</li></ul></div></div>',
      "Note: formal-job density = working-population ratio x regular wage or salaried share x share of regular jobs with some social security; rough, as the shares cover different groups of workers. Source: PLFS 2025 annual report, Tables 19, 23, 35, 36; EPFO payroll estimates; team analysis")

# ---------------- job quality
q7 = C.hbars([("West Bengal", nossb_wb := float(R["West Bengal"]["regular_no_ssb_share"]), C.BLUE, True), ("India", IND["nossb"], C.NAVY, False)] + [(h, float(R[h]["regular_no_ssb_share"]), C.GREY, False) for h in sorted(HUB, key=lambda h: -float(R[h]["regular_no_ssb_share"]))], width=560, row_h=26, label_w=100, fmt=lambda v: f"{v:.1f}%", vmax=70)
tbl7 = "<table><tr><th>Household survey, 2025</th><th class='n'>West Bengal</th><th class='n'>India</th><th class='n'>Four large states</th></tr>" + "".join(
    f"<tr><td>{a}</td><td class='n'><b>{b}%</b></td><td class='n'>{c}%</td><td class='n'>{d:.1f}% to {e:.1f}%</td></tr>" for a, b, c, d, e in [
        ("Regular wage or salaried work, share of workers", R["West Bengal"]["regular_share_of_workers"], IND["regular"], min(reg), max(reg)),
        ("Non-farm workers in limited companies", R["West Bengal"]["company_share_nonagri"], IND["company"], min(comp), max(comp))]) + "</table>"
slide("Part 2 · The quality of the jobs", "West Bengal has a smaller share of regular salaried work than the large states, and more of it lacks social security",
      '<div class="cols"><div class="main">' + exhibit(8, "Regular non-farm jobs with no social security", "Per cent of regular wage or salaried employees in non-farm work, 2025", q7) + f'<div style="margin-top:4mm">{tbl7}</div></div>' +
      side("Reading the figures", [
          f"{nossb_wb}% of West Bengal's regular non-farm jobs carry no social security, against {IND['nossb']}% for India and {min(nossb):.1f}% to {max(nossb):.1f}% in the four large states. Only Bihar is higher among the states compared.",
          "No social security means not eligible for provident fund or pension, gratuity, or health care or maternity benefit (the survey's definition).",
          "Job count and job quality therefore need separate measures. Counting jobs alone would overstate progress.",
      ]) + "</div>",
      "Source: PLFS 2025 annual report, Tables 19, 35 and 36 (rural and urban, persons); team analysis")

# ---------------- graduates
EDUS = [("graduate", "Graduate"), ("post graduate & above", "Postgraduate and above"), ("diploma/certificate course", "Diploma or certificate"), ("higher secondary", "Higher secondary"), ("all", "All levels")]
q8 = C.hbars_grouped([lab for _, lab in EDUS], [("West Bengal", C.BLUE, [E("UR", "West Bengal", e) for e, _ in EDUS]), ("India", C.GREY, [E("UR", "all India", e) for e, _ in EDUS])], width=600, row_h=52, label_w=170, vmax=14)
wf, wm = E("LFPR", "West Bengal", "graduate", "female"), E("LFPR", "West Bengal", "graduate", "male")
WORD = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
slide("Part 2 · Graduates", f"Graduate unemployment is {WORD[round(E('UR','West Bengal','graduate')/E('UR','West Bengal','all'))]} times the headline rate yet is close to India's; about {round(wf)}% of women graduates are in the labour force",
      '<div class="cols"><div class="main">' + exhibit(9, "Unemployment rate by highest level of education", "Per cent of the labour force, age 15 and over, 2025", q8) + "</div>" +
      f'<div class="side"><h3>What stands out</h3><div class="kpi"><div><span class="big">{E("UR","West Bengal","graduate")}%</span><br>graduates unemployed (all adults {E("UR","West Bengal","all")}%)</div><div><span class="big">{round(wf)}%</span><br>of women graduates in the labour force (men {round(wm)}%)</div></div><ul>'
      f'<li>West Bengal is close to India for graduates ({E("UR","all India","graduate")}%), so this is a national pattern. India\'s figures for women and men are {round(E("LFPR","all India","graduate","female"))}% and {round(E("LFPR","all India","graduate","male"))}%.</li>'
      f'<li>Women are {fem_share}% of undergraduate pass-outs. Each ten points of extra participation among one year\'s women pass-outs would add about {round(wb_ug24[1]*0.10,-3):,.0f} people to the labour force.</li>'
      f'<li>Diploma and certificate holders fare worse than India ({E("UR","West Bengal","diploma/certificate course")}% against {E("UR","all India","diploma/certificate course")}%). <span class="tag inf">Inference</span>This may point to a mismatch in vocational training.</li>'
      "<li>These are sample estimates. The report publishes no relative standard error for these tables; a rough estimate puts them within about two points either side.</li></ul></div></div>",
      "Note: 'Graduate' and 'postgraduate and above' are the survey's categories for highest level of education. Source: PLFS 2025 annual report, Tables 22 and 24 (usual status, rural and urban, persons); AISHE final report 2023-24 (Table 33); team analysis")

# ---------------- Kolkata and districts
hl = [("Kolkata", wages["Kolkata MC"], C.BLUE, 0, "middle"), ("Howrah", wages["Howrah MC"], C.NAVY, -22, "middle"), ("Chennai", wages["Chennai MC"], C.NAVY, 0, "middle"), ("Greater Mumbai", wages["Greater Mumbai MC"], C.NAVY, -22, "middle")]
q9 = C.strip(list(wages.values()), hl, width=620, height=270, refs=[(26258, "Urban India (Rs 26,258)")])
dist = F["districts"]
drows = [(r["name"], float(r["neet_15_29"]), C.BLUE if r["level"] == "state" else (C.NAVY if r["name"] == "Kolkata" else C.GREY), r["level"] == "state") for r in sorted(dist, key=lambda r: float(r["neet_15_29"]))]
q10 = C.hbars(drows, width=400, row_h=21, label_w=190, fmt=lambda v: f"{v:.1f}%", vmax=45, top=6)
kur = float(F["kolkata"]["UR %|15+"]["persons_Kolkata_MC"].rstrip("*"))
slide("Part 2 · Kolkata and the districts", f"Kolkata combines very low unemployment with the fifth-lowest regular pay among {len(wages)} million-plus cities",
      '<div class="cols"><div class="main">' + exhibit(10, "Average regular wage or salary, million-plus cities", f"Rupees a month, one dot per city ({len(wages)} cities)", q9) +
      f'<ul class="t" style="margin-top:3mm"><li>Kolkata averages Rs {n(wages["Kolkata MC"])} a month; Howrah Rs {n(wages["Howrah MC"])} (rank {ranked.index("Howrah MC")+1} from the lowest); Greater Mumbai Rs {n(wages["Greater Mumbai MC"])}; Chennai Rs {n(wages["Chennai MC"])}.</li>'
      f'<li>Kolkata\'s unemployment rate is {kur}% (relative standard error {V["kolkata_ur_rse"]}%, so approximate), against {F["kolkata"]["UR %|15+"]["persons_all_million_plus"]}% for all million-plus cities. <span class="tag inf">Inference</span>Low unemployment with low pay suggests many people take whatever work is available; cost of living and industry mix are other explanations.</li></ul></div>'
      + '<div class="side">' + exhibit(11, "Youth not working or studying, by district", "Per cent of 15 to 29-year-olds, 2025; ten most populous districts", q10) + '</div></div>',
      "Source: PLFS 2025 Labour Market Dynamics in Million-plus Cities (Tables 8 and 11, 13.1) and Labour Market Snapshot of Selected Districts; team analysis")

# ---------------- inferences
inf_rows = [
    ("The graduate-to-payroll gap is not a measure of unplaced graduates", f"After allowing for further study and non-participation the remainder is {smil(r_lo)} to {smil(r_hi)} million, depending on the age band used", "High that it cannot be read that way"),
    ("A migration target is mostly a job-creation target", f"Matching the lowest large state ({min(hub100):.1f} per 100) would need about {min(hub100)/per100('West Bengal'):.1f} times today's formal entry on the payroll measure, and {min(dens)/wbd:.1f} to {max(dens)/wbd:.1f} times on the survey measure", "Medium"),
    ("Job count and job quality need separate targets", f"{R['West Bengal']['regular_no_ssb_share']}% of regular non-farm jobs carry no social security (India {IND['nossb']}%)", "High on the facts, medium on the policy reading"),
    ("Women graduates are a large pool outside the labour force", f"{round(wf)}% participation against {round(wm)}% for men; {fem_share}% of pass-outs are women; the pattern is national", "High on the facts, medium on the policy reading"),
    ("Vocational training deserves a look", f"Diploma and certificate unemployment {E('UR','West Bengal','diploma/certificate course')}% against India's {E('UR','all India','diploma/certificate course')}%, a gap of {E('UR','West Bengal','diploma/certificate course')-E('UR','all India','diploma/certificate course'):.1f} points, wider than the rough sampling error", "Medium that the gap is real; low on the cause"),
    ("Pay may matter more than job counts in Kolkata", f"Fifth-lowest regular pay of {len(wages)} cities with {kur}% unemployment", "Low to medium: other explanations not ruled out"),
    ("The people who leave may not be graduates", "Not tested here; migration surveys would show lower-skilled out-migration better", "Low"),
    ("The shortfall is shared with other states", f"Andhra Pradesh and Kerala also record low formal entry per young person, and all four neighbours record fewer formal entrants per young person ({min(per100(s) for s in ('Odisha','Jharkhand','Bihar','Assam')):.1f} to {max(per100(s) for s in ('Odisha','Jharkhand','Bihar','Assam')):.1f}) than West Bengal ({per100('West Bengal'):.1f})", "Medium: payroll measure; Assam is level with West Bengal on the survey measure and Kerala is not low on it"),
]
itb = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in inf_rows)
slide("Beyond the three questions", "Beyond the three questions, the evidence points to job creation and job quality more than to graduate supply",
      f'<p><span class="tag inf">Inference</span>The points below are readings of the data, not findings, and each could be wrong. The last column says how firmly the data supports it.</p><table style="margin-top:3mm"><tr><th style="width:30%">Reading</th><th>Evidence</th><th style="width:20%">Confidence</th></tr>{itb}</table>',
      "Source: team analysis of AISHE, EPFO and PLFS data as cited on pages 4 to 13")

# ---------------- next steps
slide("What would settle it", "Three actions would answer the original question directly",
      '''<div class="three"><div><h3>1. Track graduates after they pass out (design on page 16)</h3><ul class="t"><li>EPFO accounts are linked to Aadhaar, and AISHE collects pass-out data from each institution</li><li>A tracer study of where graduates work, for how much and in which state would replace most of the inferences in this report</li></ul></div>
<div><h3>2. Publish three numbers every year (definitions on page 17)</h3><ul class="t"><li>Formal entry per 100 young people</li><li>Graduate unemployment</li><li>Median graduate pay</li></ul><p style="margin-top:2mm">Any claim about jobs or migration could then be tested against them.</p></div>
<div><h3>3. Close the open items</h3><ul class="t"><li>Read the state's budget speeches, IT and industrial policies and summit papers for a stated target</li><li>Obtain EPFO's method note on how workers are assigned to states</li><li>Add factory employment from the Annual Survey of Industries</li></ul></div></div>
<p class="exh" style="margin-top:9mm">Exhibit 12: What each action resolves</p>
<table><tr><th style="width:30%">Action</th><th style="width:30%">Resolves</th><th>What it needs</th></tr>
<tr><td><b>1. Track graduates after they pass out</b></td><td>Question 3: how many graduates leave, and where they work</td><td>Access to linked records held by the agencies concerned</td></tr>
<tr><td><b>2. Publish three numbers every year</b></td><td>Question 1, and the testing of any later claim</td><td>Formal entry and graduate unemployment use existing public data; graduate pay may need survey microdata</td></tr>
<tr><td><b>3. Close the open items</b></td><td>Question 3 (is there a target?) and how comparable the payroll figures are across states</td><td>The state's documents, EPFO's method note and the factory-survey file</td></tr></table>''',
      "Source: team analysis")

# ---------------- tracer study design
ug24 = wb_ug24[2]
tr = [("Question it answers", "Where do West Bengal's graduates work after they graduate: in which sector (formal, government, informal or self-employed), in which state and city, at what pay, and how many go on to further study or leave and return?"),
      ("Who collects", "The state's higher-education department and the universities hold institution records and contact details and run the survey. A statistical agency such as the NSO designs the sample. EPFO and ESIC verify formal employment under a data-sharing agreement. Roles are proposals, to be agreed."),
      ("Cohort", f"Undergraduate graduating classes of 2025 and 2026 from all institutions in the state. For scale, institutions reported {n(ug24)} undergraduate pass-outs in 2023-24."),
      ("Sample", f"About 15,000 graduates per cohort, drawn at random and stratified by institution type, discipline, gender and district. This gives about ±{moe_state:.1f} percentage points at state level and about ±{moe_sub:.1f} points for each of 12 subgroups of about 1,250 (95% confidence, design effect 1.5)."),
      ("Follow-up", "Contact at 6, 12 and 24 months after graduation; a new cohort every year."),
      ("Outcomes recorded", "Activity (working, studying, unemployed, not seeking work); employer type and sector; contract and social-security status; monthly earnings band; district and state of work; whether the graduate lived or studied outside the state and why; plan to stay or move."),
      ("Linking and consent", "Consent-based linkage to payroll records to confirm formal work. Data-protection rules and legal basis to be confirmed before fieldwork."),
      ("Publication", "An annual state report with the three indicators on the next page, and anonymised data for researchers.")]
trt = "".join(f"<tr><td style='width:17%'><b>{a}</b></td><td>{b}</td></tr>" for a, b in tr)
slide("What would settle it · Design", "A tracer study of West Bengal graduates would answer the question directly; this is a workable design",
      f'<p class="exh">Exhibit 13: Proposed design for a graduate tracer study</p><p class="exs">Team proposal. Costs, legal basis and agreements between agencies have not been assessed.</p><table>{trt}</table>',
      "Note: margins of error use n = 1.96 x sqrt(design effect x p(1-p) / respondents) with p = 0.5 and a design effect of 1.5, an assumption. Source: AISHE final report 2023-24 (Table 33) for the cohort size; team design")

# ---------------- indicator definitions
ind = [("Formal entry per 100 young people", "Net new EPFO payroll, ages 18 to 25, in the financial year, divided by the population aged 18 to 23, times 100", "EPFO (numerator); population projections as published in the higher-education survey tables, underlying source to be confirmed", "Annual; the payroll is published monthly", "Employer-state attribution unconfirmed; ages in numerator and denominator differ"),
       ("Graduate unemployment rate", "Persons whose highest education is graduate, aged 20 to 29 (and all graduates aged 15 and over, as published), unemployed as a share of the labour force, usual status", "National Statistics Office, household survey (unit-level data for the age 20 to 29 cut)", "Annual", "Sample estimates; the published reports give no standard error for these tables"),
       ("Median graduate pay", "Median monthly earnings of regular wage or salaried employees with graduate education, aged 20 to 29, in rupees", "National Statistics Office, household survey (unit-level data)", "Annual", "The reports reviewed give averages, not medians; small samples for a single state")]
it = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>" for a, b, c, d, e in ind)
slide("What would settle it · Indicators", "Three yearly indicators would make claims testable, once each has a definition and a named data owner",
      f'<p class="exh">Exhibit 14: Proposed indicators</p><p class="exs">Team proposal. Owners are the agencies that already produce the underlying data; whether each would publish the indicator is for them to decide.</p><table><tr><th style="width:15%">Indicator</th><th style="width:30%">Definition</th><th style="width:20%">Data owner</th><th style="width:10%">Frequency</th><th>Known limits</th></tr>{it}</table>'
      '<div class="callout">Read together, the three give a yearly view of how many young people enter formal work, how graduates fare in the labour market, and what they earn. None of them counts migration, which is what the tracer study is for.</div>',
      "Source: team design; data owners as named in the sources on page 18")

# ---------------- appendices
src_rows = [("Graduates", "All India Survey of Higher Education (Ministry of Education), final reports 2019-20 to 2023-24", "Table 33 pass-outs by state and level; Table 38 population aged 18 to 23", "aishe.gov.in/document-category/aishe-final-reports"),
            ("Formal jobs", "Employees' Provident Fund Organisation, provisional monthly payroll estimates, releases of 20 Jan and 20 Sep 2025", "Net new payroll by state and age band, financial years 2018-19 to 2024-25; months Apr to Nov 2024 and Apr to Jul 2025", "epfo.gov.in/data-hub"),
            ("Employment", "Periodic Labour Force Survey 2025 (MoSPI): annual report, district snapshot, million-plus cities report", "Unemployment, participation, job type and social security by state; city and district figures", "mospi.gov.in/publications-reports")]
st = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in src_rows)
slide("Appendix A", "Sources and method", f'<table><tr><th style="width:11%">Topic</th><th>Source</th><th>Used for</th><th style="width:22%">Page</th></tr>{st}</table><ul class="t" style="margin-top:4mm"><li>Graduate supply is undergraduate pass-outs counted by the state of the institution. Formal demand is EPFO net new payroll (new subscribers less exits plus rejoiners), ages 18 to 25 standing in for graduates.</li><li>The gap is counted four ways (page 7) to show how far it moves with the assumptions.</li><li>States are compared per 100 people aged 18 to 23, and checked against survey measures counted where people live (page 10).</li><li>Files were downloaded on 4 and 5 November 2026. Code and cleaned data are in the project\'s state-jobs-gap repository.</li></ul>',
      "Source: as listed")
lim = [("EPFO does not state how it assigns workers to states", "Head-office states could be inflated", "Order of states tested against survey data counted where people live; it holds"),
       (f"AISHE pass-outs for 2023-24 fall {pct_fall}% in West Bengal", "Single-year ratios are unreliable", "Response rates do not explain it; five-year totals used"),
       ("Academic and financial years differ", "Joining lag blurs year-by-year matching", f"A one-year lag tested (ratio {sc['C']:.2f}, against {sc['A']:.2f} baseline)"),
       ("EPFO covers formal work only; net payroll is not first jobs", "Overstates new jobs, ignores informal work", "Described as a proxy throughout"),
       ("Students and workers cross state lines", "Distorts every ratio", "Stated on each comparison; migration not inferred"),
       ("Survey estimates carry sampling error", "Small gaps may not be real", "Rough error of about two points for graduate tables (our estimate; the report publishes none); small differences flagged"),
       ("The raw graduate gap compares different kinds of counts", "Cannot be read as unplaced graduates", "Restated as a remainder after further study and non-participation (page 8); stronger indicator used"),
       ("State documents not yet read", "Question 3 cannot be settled", "Stated as open")]
lt = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in lim)
slide("Appendix B", "Limits and how each was handled", f'<table><tr><th style="width:38%">Limit</th><th style="width:26%">Effect</th><th>How it was handled</th></tr>{lt}</table>', "Source: team analysis")
import re


def audit(html):
    """Trace every number in the text back to the data. Returns (matched, structural, unmatched list)."""
    uni = set()
    for r in LOG:
        for fld in ("value found", "value expected"):
            for t in re.findall(r"-?\d[\d,]*\.?\d*", r[fld]):
                try: uni.add(float(t.replace(",", "")))
                except ValueError: pass
    for f in (HERE.parent / "data").glob("*.csv"):
        for row in csv.reader(open(f)):
            for c in row:
                try: uni.add(float(c.rstrip("*").replace(",", "")))
                except ValueError: pass
    for d in (F["wb_month"], V["wages"], V["india"]):
        uni.update(float(v) for v in d.values())
    uni.update({F["gap_baseline"], F["gap_lf"], float(ug5), float(ep5), a25, a24, pct25, rho_c, rho_d, rho_r, wbd / max(dens), wbd / min(dens), min(hub100) / per100("West Bengal"), min(dens) / wbd, max(dens) / wbd, V["kolkata_ur_rse"], float(pct_fall)} | set(F["scen"].values()))
    wide = set()
    for u in uni:
        for div in (1, 1e3, 1e6):
            wide.add(u / div)
    text = re.sub(r"<style>.*?</style>", " ", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\b(?:19|20)\d\d(?:-\d\d)?\b|Exhibit \d+|[Pp]ages? \d+(?: to \d+)?|Tables? \d+(?:\.\d+)?(?:, \d+)*(?: and \d+)?|\b\d+ (?:Jan|Nov|Sep)[a-z]*\b|\b\d+ and \d+ November\b|\(\d+ checks\)", " ", text)
    matched, unmatched = 0, []
    for t in re.findall(r"\d[\d,]*\.?\d*", text):
        v = float(t.replace(",", "").rstrip("."))
        dec = len(t.split(".")[1]) if "." in t else 0
        ok = any(abs(round(u, dec) - v) < 1e-9 for u in wide) or (v >= 1000 and v % 1000 == 0 and any(abs(u - v) <= 500 for u in wide))
        if ok: matched += 1
        else: unmatched.append(t)
    return matched, unmatched


a_matched, a_unmatched = audit("".join(slides))
grp = Counter(r["group"] for r in LOG)
pas = Counter(r["group"] for r in LOG if r["result"] == "PASS")
names = {"AISHE": "Pass-outs and population re-read from the raw workbooks", "EPFO": "West Bengal payroll re-read from the raw PDFs; two releases compared; definition checked", "PLFS": "Survey tables re-read by a second text route; table columns confirmed by viewing the tables",
         "PLFS cities": "City wages, rank and flags re-read from the raw report", "PLFS districts": "District figures re-read from the raw report", "claim": "Every derived figure, range, rank and correlation in the text recomputed"}
vt = "".join(f"<tr><td><b>{g}</b></td><td>{names.get(g, '')}</td><td class='n'>{pas[g]} of {grp[g]}</td></tr>" for g in grp)
ISSUES_PRE = 0
issues = ["A hand-copied value for Kolkata's unemployment carried a high-error flag that belongs to the women's rate; corrected in the data",
          "A draft headline said four states record 10 or more entrants per 100; Tamil Nadu records 9.7, so the range 9.7 to 11.1 is used",
          "'Largest unused pool' for women graduates was not supported by the data; reworded to a large pool",
          f"The payroll-based gap to the large states ({per100('West Bengal'):.1f} against {min(hub100):.1f} to {max(hub100):.1f} per 100) is now shown beside the survey-based one ({wbd/max(dens):.2f} to {wbd/min(dens):.2f} of theirs)",
          "An earlier inference that West Bengal is a net source of young workers was withdrawn; Kerala is not grouped with West Bengal on the survey measure",
          "The meaning of columns in three survey tables was confirmed by viewing the tables, not inferred from text layout",
          "The diploma-holder gap was first described as close to the sampling error; at 4.7 points it is wider than the rough error, so the wording and confidence were changed",
          "'Regional' was changed to 'shared with other states', since Andhra Pradesh and Kerala also record low formal entry",
          "'Joining dates are not public' was changed to 'none were found', since absence in the sources reviewed is not proof",
          "'No public series measures migration' was narrowed to 'does not count graduates who leave', since occasional national migration surveys exist",
          "'Fewer regular jobs' was changed to 'a smaller share of regular salaried work', which is what the data shows",
          "Reviewer feedback: the headline gap was restated; after allowing for further study and non-participation the remainder is between about \u22120.05 and +0.54 million, so it is no longer read as unplaced graduates",
          "Reviewer feedback: the place, age, kind and period mismatches moved from the appendix to the main text (page 8)",
          "Reviewer feedback: a flow-versus-stock caveat was added to the survey check (page 10), which now says it supports the pattern but not EPFO's levels",
          "Reviewer feedback: a tracer-study design and three defined indicators with named data owners were added (pages 16 and 17)",
          "A policy reading of job quality, and the Kolkata pay reading, had their confidence lowered to match the evidence"]
slide("Appendix C", f"Validation: all {len(LOG)} checks passed, and the pressure test corrected or tightened {len(issues)} points along the way",
      f'<div class="cols"><div class="main"><table><tr><th>Check group</th><th>What was checked</th><th class="n">Passed</th></tr>{vt}</table><p class="exs" style="margin-top:3mm">Figures in the text are inserted by code from the validated data. As a guard against typing errors, a final audit looked for each of the {a_matched + len(a_unmatched)} numbers in the report body among the validated values and found {a_matched}; years, page and exhibit numbers are excluded. It checks that a number exists in the data, not that it is used correctly, which the claim checks above cover. The checks run before every build, and the report is not produced if any fails.</p></div>'
      f'<div class="side"><h3>Corrected during the pressure test</h3><ul>{"".join(f"<li>{i}</li>" for i in issues)}</ul></div></div>',
      "Source: report/validate.py and report/validation_log.csv in the project repository")

html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>" + "".join(s.replace("{pg}", str(i + 1) if i else "") for i, s in enumerate(slides)) + "</body></html>"
(HERE / "report.html").write_text(html)
m_all, u_all = audit(html)
print(f"number audit: {m_all} traced, {len(u_all)} not traced: {sorted(set(u_all))}")
subprocess.run(["node", str(HERE / "render_pdf.js"), str(HERE / "report.html"), str(HERE / "West_Bengal_graduates_and_formal_jobs.pdf")], check=True)
print("pages:", len(slides))
