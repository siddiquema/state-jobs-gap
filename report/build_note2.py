"""Build the 4-page note on what the 458,000 payroll figure is made of and on idle youth (PDF).
Refuses to run unless report/validate.py passes. Run from the repo root: python3 -I report/build_note2.py
"""
import csv, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import facts, charts as C

if subprocess.run([sys.executable, "-I", str(HERE / "validate.py")]).returncode != 0:
    sys.exit("validation failed: no note produced")
F = facts.build()
V = json.load(open(HERE / "validated_values.json"))
LOG = list(csv.DictReader(open(HERE / "validation_log.csv")))
FL, SH, NT = V["flows"]["2024-25"], V["wb_share"], V["neet"]
n = lambda v: f"{v:,.0f}"
mm = lambda v: f"{v/1e6:.1f}"
pc = lambda v: f"{v*100:.1f}"
a_new, a_exit, a_rej, a_net = FL
wb_per100 = SH["wb_1825"] / (SH["pop"] * SH["pop_all"]) * 100

CSS = f"""
@page {{ size: 297mm 210mm; margin: 0 }} * {{ box-sizing: border-box }}
body {{ margin:0; font-family:'Liberation Sans',Arial,sans-serif; color:{C.NAVY}; font-size:10.5pt; line-height:1.38 }}
.slide {{ width:297mm; height:210mm; padding:13mm 16mm 11mm 16mm; page-break-after:always; position:relative; overflow:hidden }}
.tracker {{ font-size:8pt; letter-spacing:.09em; text-transform:uppercase; color:{C.MID}; margin-bottom:3mm }}
h1.title {{ font-family:'Liberation Serif',Georgia,serif; font-weight:normal; font-size:21pt; line-height:1.16; margin:0 0 4mm; max-width:262mm }}
.rule {{ border-top:1.4px solid {C.NAVY}; margin-bottom:5mm }}
.cols {{ display:flex; gap:9mm }} .main {{ flex:1.6; min-width:0 }} .side {{ flex:1; min-width:0 }}
.exh {{ font-size:9pt; font-weight:bold; margin:0 0 1mm }} .exs {{ font-size:8.8pt; color:{C.MID}; margin:0 0 2.5mm }}
.side h3 {{ font-size:10pt; margin:0 0 2mm; padding-bottom:1.5mm; border-bottom:1px solid {C.RULE} }}
.side ul {{ padding-left:4.5mm; margin:0 }} .side li {{ margin-bottom:2.4mm }}
.src {{ position:absolute; left:16mm; right:16mm; bottom:8mm; font-size:7.6pt; color:{C.MID}; border-top:1px solid {C.LIGHT}; padding-top:1.6mm }}
.pg {{ position:absolute; right:16mm; bottom:3.2mm; font-size:7.6pt; color:{C.MID} }}
table {{ border-collapse:collapse; width:100%; font-size:9.2pt }}
th {{ text-align:left; font-weight:bold; border-bottom:1.4px solid {C.NAVY}; padding:1.5mm 2mm }}
td {{ border-bottom:1px solid {C.LIGHT}; padding:1.8mm 2mm; vertical-align:top }}
.tag {{ display:inline-block; font-size:7.6pt; font-weight:bold; letter-spacing:.04em; padding:.4mm 1.8mm; border:1px solid {C.BLUE}; color:{C.BLUE}; margin-right:1.5mm; text-transform:uppercase }}
.callout {{ background:#EEF2FF; border-left:3px solid {C.BLUE}; padding:2.5mm 3.5mm; margin-top:3mm; font-size:9.4pt }}
.big {{ font-family:'Liberation Serif',serif; font-size:26pt; line-height:1; color:{C.BLUE} }}
.kpi {{ display:flex; gap:6mm; margin:2mm 0 4mm }} .kpi div {{ flex:1; border-top:2px solid {C.NAVY}; padding-top:1.5mm; font-size:8.8pt }}
"""
slides = []


def slide(tracker, title, body, source):
    slides.append(f'<section class="slide"><div class="tracker">{tracker}</div><h1 class="title">{title}</h1><div class="rule"></div>{body}<div class="src">{source}</div><div class="pg">{{pg}}</div></section>')


def exhibit(num, title, sub, svg):
    return f'<p class="exh">Exhibit {num}: {title}</p><p class="exs">{sub}</p>{svg}'


def side(head, items):
    return f'<div class="side"><h3>{head}</h3><ul>{"".join(f"<li>{i}</li>" for i in items)}</ul></div>'


# ---- page 1: what the net figure is made of
q1 = C.hbars([("New subscribers", a_new / 1e6, C.GREY, False), ("Exits", a_exit / 1e6, C.GREY, False), ("Rejoiners", a_rej / 1e6, C.GREY, False), ("Net new payroll", a_net / 1e6, C.BLUE, True)],
             width=600, row_h=40, label_w=130, fmt=lambda v: f"{v:.1f} million", vmax=24)
slide("Reading the 458,000", "The 458,000 is a net figure built from much larger flows; it is not a count of new jobs",
      '<div class="cols"><div class="main">' + exhibit(1, "India, 2024-25: the flows behind net new payroll", "Millions of people. Net = new subscribers − exits + rejoiners", q1) +
      f'<div class="callout">{mm(a_new)} − {mm(a_exit)} + {mm(a_rej)} = {mm(a_net)} million. West Bengal\'s own split into these three parts is not in the releases reviewed; EPFO holds it.</div></div>' +
      side("What follows", [
          f"Exits ({mm(a_exit)} million) and rejoiners ({mm(a_rej)} million) are each larger than new subscribers ({mm(a_new)} million). The figure is the small difference of large flows, which is what heavy job-changing and re-registration look like.",
          "New subscribers are people whose first provident-fund contribution arrives in the month. That can be a first job. It can equally be an existing worker whose employer newly registers them. The data cannot tell these apart.",
          "So the figure does not need a new industry or a new call centre to move. Existing employers replacing leavers, hiring, or registering staff can raise it. That is a possible reading, not a tested one.",
          "The earlier report already described the figure as not a count of first jobs. The flows above show why.",
      ]) + "</div>",
      "Source: EPFO provisional payroll estimates, release of 20 Sep 2025 (national tables of new subscribers, exits and rejoiners); team analysis")

# ---- page 2: share vs population
q2 = C.hbars([("Population aged 18 to 23", SH["pop"] * 100, C.GREY, False), ("Net new payroll, ages 18 to 25", SH["y1825"] * 100, C.BLUE, True), ("Net new payroll, all ages", SH["all"] * 100, C.BLUE, False)],
             width=600, row_h=44, label_w=200, fmt=lambda v: f"{v:.1f}%", vmax=8)
slide("Reading the 458,000", f"Relative to its size, West Bengal records about half its population share of young formal entrants, so the figure is low, not high, compared with the rest of India",
      '<div class="cols"><div class="main">' + exhibit(2, "West Bengal's share of India, 2023-24 population and 2024-25 payroll", "Each bar is West Bengal's share of the India total, per cent", q2) +
      f'<div class="kpi"><div><span class="big">{wb_per100:.1f}</span><br>West Bengal: net new payroll aged 18 to 25 per 100 people aged 18 to 23</div><div><span class="big">{SH["india_per100"]:.1f}</span><br>India, same measure</div></div></div>' +
      side("What can and cannot be checked", [
          "The figures are compiled by the Employees' Provident Fund Organisation, a central body under the Ministry of Labour and Employment, not by the state government.",
          "West Bengal's figures for 2018-19 to 2023-24 are identical in the January and September 2025 releases, so they were not revised.",
          "A household survey, a different source, orders the states the same way as the payroll data.",
          "These checks show the figures are consistent with each other. They cannot show that every registration is new employment. That needs the breakdown requested on page 4.",
          "EPFO does not say how it assigns workers to states. If it uses the employer's registered state, a West Bengal worker employed by a firm registered elsewhere would be counted there.",
      ]) + "</div>",
      "Note: payroll ages 18 to 25 against population aged 18 to 23; the same mismatch applies to India and to West Bengal. Source: EPFO payroll estimates (Sep 2025); AISHE final report 2023-24 (Table 38); team analysis")

# ---- page 3: NEET by sex
q3 = C.hbars_grouped(["Men", "Women", "All persons"], [("West Bengal", C.BLUE, [NT["West Bengal"]["male"], NT["West Bengal"]["female"], NT["West Bengal"]["persons"]]), ("India", C.GREY, [NT["all India"]["male"], NT["all India"]["female"], NT["all India"]["persons"]])],
                     width=600, row_h=64, label_w=110, vmax=60)
slide("Young people neither working nor studying", f"Nearly half of West Bengal's women aged 15 to 29 are neither working nor studying; for men the rate is {NT['West Bengal']['male']:.1f}%, close to India's",
      '<div class="cols"><div class="main">' + exhibit(3, "Young people not in employment, education or training, ages 15 to 29", "Per cent of the age group, 2025", q3) + "</div>" +
      side("What this does and does not tell you", [
          f"The high overall rate ({NT['West Bengal']['persons']:.1f}%, against {NT['all India']['persons']:.1f}% for India) comes mainly from women: {NT['West Bengal']['female']:.1f}% against {NT['all India']['female']:.1f}% for India. For men it is {NT['West Bengal']['male']:.1f}% against {NT['all India']['male']:.1f}%.",
          "The survey counts people living in households in the state. Graduates who have moved away for work are generally not in its sample. A high rate among residents is therefore not evidence that graduates are leaving, and it does not show that they are not.",
          "Whether West Bengal's graduates leave for call-centre and software jobs elsewhere cannot be answered from public data. A tracer study of graduates (page 16 of the earlier report) would answer it.",
          "The higher-education survey counts 59 universities in the state; you mentioned 64, so a list is needed to reconcile.",
      ]) + "</div>",
      "Source: PLFS 2025 annual report, Table 57.1 (usual status, rural and urban); AISHE final report 2023-24 (Table 1a); team analysis")

# ---- page 4: questions to put to government
qs = [("What is being done to raise median pay?", "A written plan with the baseline median by sector, a target for each sector, the owner and the reporting date. West Bengal's average regular wage is Rs 16,618 a month against Rs 22,699 for India (earlier note).", "A published baseline and yearly sector targets, not a statement of intent"),
      ("Why are so many young people neither working nor studying, and are graduates leaving?", "District-wise rates for men and women, a plan to raise women's participation, and a tracer study of graduates that records where they work after 6, 12 and 24 months.", "Rates by district and sex; a tracer with a named owner, sample and publication date"),
      ("How can 458,000 net formal jobs arise without new industry?", "From EPFO's regional offices: West Bengal's new subscribers, exits and rejoiners for 2024-25; the same by sector and establishment size; and how many establishments registered for the first time.", "A split showing how much is first registration by new or existing employers, and how much is rejoining")]
qt = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in qs)
slide("What to ask", "Three precise requests would settle your three questions with figures the government can be held to",
      f'<p style="max-width:250mm"><span class="tag">Team proposal</span>On whether anyone is manipulating data: the checks run here found the figures consistent with each other and unrevised across releases. They cannot show that the underlying registrations are all genuine new employment, which only the breakdown in the last row can. This note takes no position on any person or party.</p>'
      f'<table style="margin-top:4mm"><tr><th style="width:24%">Your question</th><th>What to ask for</th><th style="width:28%">What a good answer looks like</th></tr>{qt}</table>',
      "Source: team proposal; no part of this request has been agreed with any agency")

html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>" + "".join(s.replace("{pg}", str(i + 1)) for i, s in enumerate(slides)) + "</body></html>"
(HERE / "note2.html").write_text(html)


def audit(h):
    uni = set()
    for r in LOG:
        for fld in ("value found", "value expected"):
            for t in re.findall(r"-?\d[\d,]*\.?\d*", r[fld]):
                try: uni.add(float(t.replace(",", "")))
                except ValueError: pass
    for k in ("flows",):
        for v in V[k].values(): uni.update(float(x) for x in v)
    for d in (SH, NT["West Bengal"], NT["all India"]): uni.update(float(x) for x in d.values())
    uni.update({SH["pop"] * 100, SH["y1825"] * 100, SH["all"] * 100, wb_per100, SH["india_per100"], 16618.0, 22699.0, 59.0, 64.0, 458.0})
    for k in ("avg_wage",):
        for v in V[k].values(): uni.update(float(x) for x in v)
    wide = {u / d for u in uni for d in (1, 1e3, 1e6)}
    text = re.sub(r"<style>.*?</style>", " ", h, flags=re.S); text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\b(?:19|20)\d\d(?:-\d\d)?\b|Exhibit \d+|[Pp]ages? \d+(?: of the earlier report)?|Tables? \d+(?:\.\d+)?[a-z]?(?:, \d+)*|\b\d+ Sep\b|\b(?:6, 12 and 24)\b|\bpage \d+\b", " ", text)
    ok, bad = 0, []
    for t in re.findall(r"\d[\d,]*\.?\d*", text):
        v = float(t.replace(",", "").rstrip(".")); dec = len(t.split(".")[1]) if "." in t else 0
        if any(abs(round(u, dec) - v) < 1e-9 for u in wide) or (v >= 1000 and v % 1000 == 0 and any(abs(u - v) <= 500 for u in wide)): ok += 1
        else: bad.append(t)
    return ok, bad


ok, bad = audit(html)
print(f"number audit: {ok} traced, {len(bad)} not traced: {sorted(set(bad))}")
subprocess.run(["node", str(HERE / "render_pdf.js"), str(HERE / "note2.html"), str(HERE / "Reading_the_458000.pdf")], check=True)
print("pages:", len(slides))
