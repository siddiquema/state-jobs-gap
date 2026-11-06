"""Build the response note to the five specific questions (PDF) and the two data-request templates (CSV).
Refuses to run unless report/validate.py passes. Run from the repo root: python3 -I report/build_response.py
"""
import csv, json, re, subprocess, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import facts, charts as C

if subprocess.run([sys.executable, "-I", str(HERE / "validate.py")]).returncode != 0:
    sys.exit("validation failed: no note produced")
F = facts.build()
V = json.load(open(HERE / "validated_values.json"))
LOG = list(csv.DictReader(open(HERE / "validation_log.csv")))
W, OCC, PL = V["avg_wage"], V["occ_wage"], V["page_labels"]
n = lambda v: f"{v:,.0f}"
wb, ind = W["West Bengal"][8], W["all India"][8]
states_w = {k: v[8] for k, v in W.items() if k != "all India"}
rank_low = sorted(states_w, key=states_w.get)
rk = rank_low.index("West Bengal") + 1
below = round((1 - wb / ind) * 100)
fy = F["wb_fy"]
ug24 = F["wb_ug"]["2023-24"][2]

CSS = f"""
@page {{ size: 297mm 210mm; margin: 0 }} * {{ box-sizing: border-box }}
body {{ margin:0; font-family:'Liberation Sans',Arial,sans-serif; color:{C.NAVY}; font-size:10.5pt; line-height:1.38 }}
.slide {{ width:297mm; height:210mm; padding:13mm 16mm 11mm 16mm; page-break-after:always; position:relative; overflow:hidden }}
.tracker {{ font-size:8pt; letter-spacing:.09em; text-transform:uppercase; color:{C.MID}; margin-bottom:3mm }}
h1.title {{ font-family:'Liberation Serif',Georgia,serif; font-weight:normal; font-size:21pt; line-height:1.16; margin:0 0 4mm; max-width:262mm }}
.rule {{ border-top:1.4px solid {C.NAVY}; margin-bottom:5mm }}
.cols {{ display:flex; gap:9mm }} .main {{ flex:1.7; min-width:0 }} .side {{ flex:1; min-width:0 }}
.exh {{ font-size:9pt; font-weight:bold; margin:0 0 1mm }} .exs {{ font-size:8.8pt; color:{C.MID}; margin:0 0 2.5mm }}
.side h3 {{ font-size:10pt; margin:0 0 2mm; padding-bottom:1.5mm; border-bottom:1px solid {C.RULE} }}
.side ul, ul.t {{ padding-left:4.5mm; margin:0 }} .side li, ul.t li {{ margin-bottom:2.2mm }}
.src {{ position:absolute; left:16mm; right:16mm; bottom:8mm; font-size:7.6pt; color:{C.MID}; border-top:1px solid {C.LIGHT}; padding-top:1.6mm }}
.pg {{ position:absolute; right:16mm; bottom:3.2mm; font-size:7.6pt; color:{C.MID} }}
table {{ border-collapse:collapse; width:100%; font-size:8.8pt }}
th {{ text-align:left; font-weight:bold; border-bottom:1.4px solid {C.NAVY}; padding:1.5mm 2mm; vertical-align:bottom }}
td {{ border-bottom:1px solid {C.LIGHT}; padding:1.6mm 2mm; vertical-align:top }}
td.n, th.n {{ text-align:right; white-space:nowrap }}
.tag {{ display:inline-block; font-size:7.6pt; font-weight:bold; letter-spacing:.04em; padding:.4mm 1.8mm; border:1px solid {C.NAVY}; margin-right:1.5mm; text-transform:uppercase }}
.tag.inf {{ border-color:{C.BLUE}; color:{C.BLUE} }}
.callout {{ background:#EEF2FF; border-left:3px solid {C.BLUE}; padding:2.5mm 3.5mm; margin-top:3mm; font-size:9.4pt }}
.big {{ font-family:'Liberation Serif',serif; font-size:26pt; line-height:1; color:{C.BLUE} }}
.kpi {{ display:flex; gap:6mm; margin:2mm 0 4mm }} .kpi div {{ flex:1; border-top:2px solid {C.NAVY}; padding-top:1.5mm; font-size:8.8pt }}
"""
slides = []


def slide(tracker, title, body, source):
    slides.append(f'<section class="slide"><div class="tracker">{tracker}</div><h1 class="title">{title}</h1><div class="rule"></div>{body}<div class="src">{source}</div><div class="pg">{{pg}}</div></section>')


def exhibit(num, title, sub, svg):
    return f'<p class="exh">Exhibit {num}: {title}</p><p class="exs">{sub}</p>{svg}'


# ---------------- page 1: the five answers
rows = [
    ("1", "Companies starting in Q1 and the jobs they create; 2027 and 2028 only",
     "None was found in the sources reviewed. Public payroll data records hiring after it happens, not planned start dates or planned jobs by company.",
     f"A baseline only: West Bengal added {n(fy['2024-25']['all'])} net formal jobs in 2024-25.",
     "State industry and IT departments, the state's industrial development body, Chamber members", "Needs state or Chamber figures"),
    ("2", "Where graduates of the state's universities find jobs, in West Bengal or elsewhere",
     "No source reviewed follows graduates after they pass out.",
     f"Scale only: institutions in the state reported {n(ug24)} undergraduate pass-outs in 2023-24. The higher-education survey counts 59 universities in the state; you mentioned 62, so a list is needed to reconcile.",
     "University placement cells, higher-education department, payroll records (with consent)", "Needs a tracer study"),
    ("3", "Median salary, and how it compares with other states",
     "Official averages exist; medians need unit-level survey files.",
     f"Average regular monthly wage or salary: Rs {n(wb)} in West Bengal against Rs {n(ind)} for India; second lowest of 35 states and union territories (page 2).",
     "National Statistics Office (survey files)", "Partly answered: average, not median"),
    ("4", "Companies going live in each quarter of 2027 and 2028",
     "Same gap as question 1. MoSPI lists a monthly report on large infrastructure projects; it was not reviewed for this note.",
     "Nothing for 2027 and 2028.",
     "State departments, the industrial development body, Chamber members", "Needs state or Chamber figures"),
    ("5", "How to raise median salary sector by sector",
     "A method, not a data question alone. No state sector-wise pay figures were found in the public reports reviewed.",
     "A measure-then-target method (page 3) and a data request (page 5).",
     "State labour and industry departments with the National Statistics Office", "Method given; baseline needs data"),
]
tb = "".join(f"<tr><td><b>{a}</b></td><td><b>{b}</b></td><td>{c}</td><td>{d}</td><td>{e}</td><td><b>{f}</b></td></tr>" for a, b, c, d, e, f in rows)
slide("Response to the five questions", "Public data answers one of your five questions in part, and shows a pay gap behind it; the other four need figures only the state and the Chamber hold",
      f'<p style="max-width:250mm">You asked for government-validated figures. All the data in the earlier report comes from official publications, and the calculations on top of it are ours. None of it has been ratified by the state government, and none of it answers questions about future companies. This note says plainly what exists, what does not, and what to ask for.</p>'
      f'<table style="margin-top:3mm"><tr><th style="width:3%">#</th><th style="width:17%">Your question</th><th style="width:21%">What public sources hold</th><th style="width:25%">What we can say now</th><th style="width:19%">Who holds the figures</th><th>Status</th></tr>{tb}</table>',
      "Source: AISHE final report 2023-24 (Tables 1a, 33); EPFO payroll estimates (Sep 2025); PLFS 2025 annual report, Table 38; team analysis")

# ---------------- page 2: salary
names = ["West Bengal", "Odisha", "Jharkhand", "Bihar", "Assam", "Andhra Pradesh", "Kerala", "Tamil Nadu", "Karnataka", "Telangana", "Maharashtra"]
order = sorted(names, key=lambda s: states_w[s])
rows_h = [(s, states_w[s], C.BLUE if s == "West Bengal" else (C.NAVY if s in ("Odisha", "Jharkhand", "Bihar", "Assam") else C.GREY), s == "West Bengal") for s in order]
q1 = C.hbars(rows_h, width=620, row_h=25, label_w=110, fmt=lambda v: f"Rs {v:,.0f}", vmax=32000, legend_items=[("West Bengal", C.BLUE), ("Neighbouring states", C.NAVY), ("Other large states", C.GREY)], ref=(ind, f"India Rs {n(ind)}"))
ratio_hi = max(states_w[s] for s in ("Telangana", "Karnataka", "Maharashtra", "Tamil Nadu")) / wb
slide("Question 3 · Salary", f"West Bengal's average regular wage is Rs {n(wb)} a month, {below}% below India's and the second lowest of 35 states and union territories",
      '<div class="cols"><div class="main">' + exhibit(1, "Average monthly wage or salary of regular wage and salaried employees", "Rupees a month, rural and urban, all persons, 2025; sorted from lowest", q1) + "</div>" +
      f'<div class="side"><h3>What this does and does not tell you</h3><div class="kpi"><div><span class="big">{below}%</span><br>below the India average</div><div><span class="big">{rk} of 35</span><br>from the lowest</div></div><ul>'
      f'<li>This is the official national household survey, published by the National Statistics Office. It is an <b>average</b>, not the median you asked for. A median needs the survey\'s unit-level files.</li>'
      f'<li>West Bengal\'s urban average is Rs {n(W["West Bengal"][5])} against Rs {n(W["all India"][5])} for India. Kolkata\'s city average is Rs {n(V["wages"]["Kolkata MC"])}.</li>'
      f'<li>Telangana, Karnataka, Maharashtra and Tamil Nadu range from Rs {n(min(states_w[s] for s in ("Telangana","Karnataka","Maharashtra","Tamil Nadu")))} to Rs {n(max(states_w[s] for s in ("Telangana","Karnataka","Maharashtra","Tamil Nadu")))}, up to {ratio_hi:.2f} times West Bengal\'s.</li>'
      "<li>The figures come from a sample survey, so small differences between states are uncertain; the gap to India is large.</li></ul></div></div>",
      f"Source: PLFS 2025 annual report, Table 38 (printed page {PL['38']}; rural and urban, persons, current weekly status); team analysis. Government statistics, not ratified by the state government.")

# ---------------- page 3: question 5
occ_labels = ["Managers", "Professionals", "Technicians and associates", "Clerical support", "Service and sales", "Skilled agriculture and fishery", "Craft and related trades", "Plant and machine operators", "Elementary occupations"]
occ_rows = sorted([(l, OCC[i], C.GREY, False) for i, l in enumerate(occ_labels)], key=lambda r: -r[1])
q2 = C.hbars(occ_rows, width=620, row_h=24, label_w=190, fmt=lambda v: f"Rs {v:,.0f}", vmax=56000, ref=(OCC[9], f"All occupations Rs {n(OCC[9])}"))
steps = [("1. Measure the baseline", "Median monthly regular wage by sector and occupation for West Bengal and for the comparison states, from the survey's unit-level files, with the margin of error."),
         ("2. Find out why pay is low", "Split the gap to a comparison state into two parts: the state has people in lower-paying kinds of work (mix), or pays less for the same work (within-sector). The remedies differ."),
         ("3. Choose sectors and set targets", "Pick the sectors where the state has many jobs or many new jobs and the pay gap is largest. Set yearly targets for each sector's median, with a published baseline."),
         ("4. Publish every year", "Report the median by sector against the target and against other states, so that progress can be checked by anyone.")]
st = "".join(f"<tr><td style='width:26%'><b>{a}</b></td><td>{b}</td></tr>" for a, b in steps)
slide("Question 5 · Sector-wise pay", "Raising median pay by sector starts with measuring why pay is low; national pay differs four-fold by occupation, so the mix of jobs matters",
      '<div class="cols"><div class="main">' + exhibit(2, "India: average monthly wage or salary of regular employees, by occupation", "Rupees a month, rural and urban, all persons, 2025", q2) + "</div>" +
      f'<div class="side"><h3>A measure-then-target method</h3><table>{st}</table><div class="callout"><span class="tag inf">Team proposal</span> No promise is made about what any policy would achieve. The data to run steps 1 and 2 for West Bengal is not in the public reports reviewed.</div></div></div>',
      f"Source: PLFS 2025 annual report, Table 51 (printed page {PL['51']}; all India, rural and urban, persons); team analysis")

# ---------------- page 4: source map
smap = [("Net new formal jobs, West Bengal, 2024-25: 457,697; ages 18 to 25: 212,064", "EPFO provisional payroll estimates, release of 20 Sep 2025", f"State tables 'Net New Payroll Statewise & Age Buckets', PDF pages {PL['epfo_state_pages']}; sum the six age-band rows for West Bengal, column 2024-25", "epfo.gov.in/data-hub"),
        (f"Undergraduate pass-outs, West Bengal: {n(ug24)} in 2023-24", "AISHE final report 2023-24 (Excel)", "Sheet '33 Out Turn' (Table 33), row West Bengal, Under Graduate total", "aishe.gov.in/document-category/aishe-final-reports"),
        ("Universities in West Bengal: 59", "AISHE final report 2023-24 (Excel)", "Sheet '1a.InsResponse' (Table 1a), row West Bengal, Universities", "as above"),
        (f"Average regular wage, West Bengal Rs {n(wb)}, India Rs {n(ind)}", "PLFS 2025 annual report", f"Appendix A, Table 38, printed page {PL['38']}, rural+urban persons column, rows West Bengal and all India", "mospi.gov.in/publications-reports"),
        ("Graduate unemployment 11.4%; women graduates in labour force 40.2%", "PLFS 2025 annual report", f"Table 24 (page {PL['24']}, persons) and Table 22 (page {PL['22f']}, women), rural+urban, column 'graduate'", "as above"),
        ("Regular non-farm jobs with no social security: 60.5%", "PLFS 2025 annual report", f"Table 36, printed page {PL['36']}, rural+urban, persons, column 'without any specified SSB'", "as above"),
        ("Kolkata average regular wage Rs 19,093; fifth lowest of 46 cities", "PLFS 2025 Labour Market Dynamics in Million-plus Cities", "Table 8, row Kolkata MC, persons", "as above"),
        ("District youth idleness (NEET), unemployment", "PLFS 2025 Labour Market Snapshot of Selected Districts", "State page for West Bengal, ten most populous districts", "as above")]
sm = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in smap)
slide("Where the numbers come from", "Every figure comes from three official publications; each can be checked against the table and page below",
      f'<p style="max-width:250mm">The earlier report was prepared with an AI assistant. The figures were not generated by it: they were read from the official files and computed by code, then checked by {len(LOG)} separate tests, including re-reading the source files a second way. You or the Chamber can check any figure yourself from this table.</p>'
      f'<table style="margin-top:3mm"><tr><th style="width:27%">Figure</th><th style="width:21%">Document</th><th>Where to find it</th><th style="width:19%">Page</th></tr>{sm}</table>',
      "Source: EPFO, Ministry of Education and MoSPI publications as listed; team analysis")

# ---------------- page 5: data request
req = [("1 and 4. Companies going live, 2027 and 2028",
        "Company name; sector; district; project status (announced, approved, under construction, operational); evidence of the status (land possession, building approval, power connection, first payroll registration); planned go-live quarter; planned direct jobs by quarter; indicative wage band",
        "State industry and IT departments; the industrial development body; Chamber members",
        "Each row verified by a department officer against the evidence named; a share spot-checked against payroll registration once the company is operating"),
       ("2. Graduate placement and location",
        "Institution; course; year of passing out; graduates placed; employer name; employer's state and city; job role; monthly salary band; further study; consented follow-up at 6, 12 and 24 months",
        "University placement cells; the higher-education department; payroll records with consent",
        "Same definitions across all universities; a list of the 62 universities named, so counts reconcile with the survey's 59"),
       ("3. Median pay by sector",
        "Median monthly regular wage by sector and occupation, West Bengal and comparison states, with sample sizes and margins of error",
        "National Statistics Office survey files; state labour department records",
        "Computed from the unit-level files by a method that can be re-run and published"),
       ("5. Sector pay targets",
        "Baseline medians from item 3; the state's yearly target for each sector; the measure used to report progress",
        "State labour and industry departments",
        "Published baseline before targets are set; yearly report against the target")]
rt = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in req)
slide("What to ask for", "A data request the Chamber or the state can answer: definitions that make each figure verifiable",
      f'<p style="max-width:250mm">Templates for items 1 and 4 and for item 2 are in two CSV files that accompany this note. The point of the definitions is that no row is counted on an announcement alone.</p><table style="margin-top:3mm"><tr><th style="width:17%">Question</th><th style="width:38%">Fields</th><th style="width:20%">Who holds it</th><th>How it is validated</th></tr>{rt}</table>',
      "Source: team proposal; no part of this request has been agreed with any agency")

# ---------------- page 6: limits
lim = [("These figures are not ratified by the state government.", "They are official national statistics. Ratification by the state is a separate step, and the source table lets the state's statistics department do it."),
       ("Averages are not medians.", "Question 3 asked for the median. The reports give averages; the median needs the survey's unit-level files."),
       ("Nothing about 2027 and 2028 is estimated.", "No forecast, pipeline or company list is given, because none was found in public data."),
       ("Statements about named companies and ministers were not checked.", "Investments by named firms, real-estate and power projects, the absence of global capability centres, and the comparison with other states' leadership were raised in your message. None of it is used here, and this note takes no position on policy or on individuals."),
       ("The earlier report stands, with its limits.", "It measures formal job entry per young person and job quality. It does not measure where graduates go, which is why the tracer study on its page 16 matters, and it does not cover short- and long-term job opportunities, which is the gap the requests on page 5 are meant to fill.")]
lt = "".join(f"<tr><td style='width:34%'><b>{a}</b></td><td>{b}</td></tr>" for a, b in lim)
slide("Limits of this note", "What this note does not do", f"<table>{lt}</table>", "Source: team analysis")

html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>" + "".join(s.replace("{pg}", str(i + 1) if i else "") for i, s in enumerate(slides)) + "</body></html>"
(HERE / "response.html").write_text(html)


def audit(h):
    uni = set()
    for r in LOG:
        for fld in ("value found", "value expected"):
            for t in re.findall(r"-?\d[\d,]*\.?\d*", r[fld]):
                try: uni.add(float(t.replace(",", "")))
                except ValueError: pass
    for v in W.values(): uni.update(float(x) for x in v)
    uni.update(float(x) for x in OCC); uni.update(float(x) for x in V["wages"].values())
    for f in (HERE.parent / "data").glob("*.csv"):
        for row in csv.reader(open(f)):
            for c in row:
                try: uni.add(float(c.rstrip("*").replace(",", "")))
                except ValueError: pass
    uni.update({float(ug24), float(fy["2024-25"]["all"]), float(fy["2024-25"]["y1825"]), float(below), float(rk), float(ratio_hi), float(len(LOG))})
    wide = {u / d for u in uni for d in (1, 1e3, 1e6)}
    text = re.sub(r"<style>.*?</style>", " ", h, flags=re.S); text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\b(?:19|20)\d\d(?:-\d\d)?\b|Exhibit \d+|[Pp]ages? \d+(?: to \d+)?|PDF pages \d+ to \d+|Tables? \d+[a-z]?(?: \(\d+\))?(?:, \d+)*(?: and \d+)?|printed page A-\d+|A-\d+|\b\d+ (?:Jan|Nov|Sep)[a-z]*\b|\b\d+ and \d+ \b|\b\d+ separate tests\b|\b(?:6, 12 and 24)\b", " ", text)
    ok, bad = 0, []
    for t in re.findall(r"\d[\d,]*\.?\d*", text):
        v = float(t.replace(",", "").rstrip(".")); dec = len(t.split(".")[1]) if "." in t else 0
        if any(abs(round(u, dec) - v) < 1e-9 for u in wide) or (v >= 1000 and v % 1000 == 0 and any(abs(u - v) <= 500 for u in wide)): ok += 1
        else: bad.append(t)
    return ok, bad


ok, bad = audit(html)
print(f"number audit: {ok} traced, {len(bad)} not traced: {sorted(set(bad))}")
subprocess.run(["node", str(HERE / "render_pdf.js"), str(HERE / "response.html"), str(HERE / "Response_to_five_questions.pdf")], check=True)

# ---------------- data-request templates
with open(HERE / "data_request_pipeline.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["company_name", "sector", "district", "project_status (announced/approved/under construction/operational)", "evidence_of_status (document and date)", "planned_go_live_quarter (e.g. 2027-Q2)",
                "planned_direct_jobs_in_first_quarter", "planned_direct_jobs_by_end_of_year_1", "indicative_monthly_wage_band_rs", "source_of_figures", "verified_by (officer and date)"])
    w.writerow(["(example only)", "", "", "", "", "", "", "", "", "", ""])
with open(HERE / "data_request_graduate_placement.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["institution", "course", "year_passed_out", "graduates_passed_out", "graduates_placed", "placed_employer_state", "placed_employer_city", "job_role", "monthly_salary_band_rs", "further_study", "followup_consent (yes/no)"])
    w.writerow(["(example only)", "", "", "", "", "", "", "", "", "", ""])
print("pages:", len(slides))
