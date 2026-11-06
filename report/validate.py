"""Validate every figure behind the report against the raw source files, by a second, independent route.

Route 1 (report/facts.py): cleaned CSVs in data/, produced by the repository's extraction scripts.
Route 2 (this file): fresh reads of the raw files in raw/ (xlsx cells by position; PDF text via `pdftotext -raw`/-layout with
different parsing), plus checks on every derived claim (sums, ratios, ranges, ranks, correlations).
Writes report/validation_log.csv and exits non-zero if anything fails. Run from the repo root: python3 -I report/validate.py
"""
import csv, glob, re, subprocess, sys
from pathlib import Path
import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import facts

ROOT = Path(__file__).resolve().parent.parent
F = facts.build()
LOG = []


def check(group, claim, got, expected, tol=0.0):
    ok = abs(got - expected) <= tol if isinstance(got, (int, float)) and isinstance(expected, (int, float)) else got == expected
    LOG.append((group, claim, got, expected, "PASS" if ok else "FAIL"))
    return ok


def pdf_text(path, mode):
    return subprocess.run(["pdftotext", mode, str(path), "-"], capture_output=True, text=True, check=True).stdout


# ---------- 1. AISHE: undergraduate pass-outs and population, read by cell position from the raw workbooks
FILES = {"2019-20": "AISHE Final Report 2019-20.xlsx", "2020-21": "AISHE Final Report 2020-21.xlsx", "2021-22": "AISHE Final Report 2021-22.xlsx",
         "2022-23": "AISHE Final Report 2022-23.xlsx", "2023-24": "AISHE Final Report 2023-24 (1).xlsx"}
raw_ug, raw_pg = {}, {}
for y, f in FILES.items():
    wb = openpyxl.load_workbook(ROOT / "raw/aishe" / f, read_only=True, data_only=True)
    sh = next(n for n in wb.sheetnames if n.replace(" ", "").lower().startswith("33") and "cat" not in n.lower() and "a" != n[-1])
    for r in wb[sh].iter_rows(values_only=True):
        if any(isinstance(c, str) and c.strip() == "West Bengal" for c in r):
            nums = [c for c in r if isinstance(c, (int, float))]
            raw_ug[y] = (nums[10], nums[11], nums[12])           # UG male, female, total (after Ph.D., M.Phil., PG triples)
            raw_pg[y] = nums[9]                                 # PG total
            check("AISHE", f"{y}: level totals add up to the grand total", nums[3] + nums[6] + nums[9] + nums[12] + nums[15] + nums[18] + nums[21] + nums[24], nums[-1])
            break
for y in FILES:
    check("AISHE", f"West Bengal UG pass-outs {y} (raw workbook vs cleaned table)", raw_ug[y][2], F["wb_ug"][y][2])
    check("AISHE", f"West Bengal UG male + female {y} equal total", raw_ug[y][0] + raw_ug[y][1], raw_ug[y][2])
raw_pop = {}
for y in ("2022-23", "2023-24"):
    wb = openpyxl.load_workbook(ROOT / "raw/aishe" / FILES[y], read_only=True, data_only=True)
    sh = next(n for n in wb.sheetnames if n.replace(" ", "").startswith("38"))
    for r in wb[sh].iter_rows(values_only=True):
        c = [x for x in r if x is not None]
        if len(c) >= 5 and isinstance(c[1], str):
            raw_pop[(y, c[1].strip().replace("Tamilnadu", "Tamil Nadu"))] = c[4]
check("AISHE", "West Bengal population aged 18-23, 2023-24", raw_pop[("2023-24", "West Bengal")], 9992600)

for y in FILES:
    check("AISHE", f"West Bengal PG pass-outs {y} (raw workbook vs cleaned table)", raw_pg[y], F["wb_pg"][y])

# ---------- 2. EPFO: West Bengal net payroll by age band, from the two raw payroll PDFs
def epfo_wb(pdf):
    out, bucket, periods = {}, None, None
    in_state = False
    for line in pdf_text(pdf, "-layout").splitlines():
        if "STATEWISE NEW PAYROLL DATA" in line:
            in_state = True
        elif "INDUSTRY WISE PAYROLL DATA" in line:
            in_state = False
        if not in_state:
            continue
        m = re.match(r"\s*Age Bucket:\s*(.+?)\s*$", line)
        if m:
            bucket = m.group(1)
        elif line.startswith("State") and "2017-18" in line:
            periods = line.split()[1:]
        elif line.startswith("WEST BENGAL") and periods:
            vals = [int(v) for v in line.split()[2:]]
            assert len(vals) == len(periods), (len(vals), len(periods))
            out.update({(p, bucket): v for p, v in zip(periods, vals)})
    return out

jan = epfo_wb(next((ROOT / "raw/epfo").glob("*January-2025*.pdf")))
sep = epfo_wb(next((ROOT / "raw/epfo").glob("*September-2025*.pdf")))
BK = facts.BUCKETS
for fy in facts.FYS:
    src = sep
    for b in BK:
        check("EPFO", f"West Bengal {fy}, age band {b} (raw PDF vs cleaned table)", src[(fy, b)], F["ep"][(fy, "WEST BENGAL", b)])
for fy in facts.FYS[:-1]:
    same = all(jan[(fy, b)] == sep[(fy, b)] for b in BK)
    check("EPFO", f"Jan-2025 and Sep-2025 releases agree for {fy} (all six age bands)", same, True)
for m in F["wb_month"]:
    src = jan if m.endswith("24") else sep
    raw_m = sum(src[(m, b)] for b in BK)
    check("EPFO", f"West Bengal net payroll {m} (all ages)", raw_m, F["wb_month"][m])
# national identity: net payroll = new subscribers - exits + rejoiners (first Total line of the Sep release)
t = pdf_text(next((ROOT / "raw/epfo").glob("*September-2025*.pdf")), "-layout")
tot = re.search(r"^\s*Total\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$", t, re.M)
a_, b_, c_, d_ = map(int, tot.groups())
check("EPFO", "definition: net payroll = new subscribers - exits + rejoiners (national, 2017-18)", a_ - b_ + c_, d_)
nat = {}
for m in re.finditer(r"^\s*(Apr|May|Jun|Jul|Aug|Sep|Oct|Nov)-2024\s+([\d\s]+?)\s*$", pdf_text(next((ROOT / "raw/epfo").glob("*January-2025*.pdf")), "-layout"), re.M):
    nums = m.group(2).split()
    nat[m.group(1)] = int(nums[6])                           # total column
check("EPFO", "October 2024 is the lowest month nationally, Apr-Nov 2024", min(nat, key=nat.get), "Oct")

# ---------- 3. PLFS annual report: tables read from `pdftotext -raw`, last page of each table = rural+urban (persons for 22-24, 19, 35)
ann = pdf_text(next((ROOT / "raw/plfs").glob("*PLFS_2025_F_REV*.pdf")), "-raw").split("\f")
NUM = r"-?[\d,]+(?:\.\d+)?"
def plfs_table(tno, ncols, which=-1):
    hits = [p for p in ann if re.search(rf"Table \({tno}\):", p) and re.search(r"^West Bengal ", p, re.M)]
    assert len(hits) in (3, 9), (tno, len(hits))
    out = {}
    for l in hits[which].splitlines():
        m = re.match(rf"^([A-Za-z&.\- ]+?) ((?:{NUM} ){{{ncols-1}}}{NUM})$", l.strip())
        if m:
            out[m.group(1)] = [float(v.replace(",", "")) for v in m.group(2).split()]
    return out
EDU = ["not literate", "literate & up to primary", "middle", "secondary", "higher secondary", "diploma/certificate course", "graduate", "post graduate & above", "secondary & above", "all"]
raw_ur = plfs_table(24, 10); raw_lf_m = plfs_table(22, 10, -3); raw_lf_f = plfs_table(22, 10, -2); raw_lf_p = plfs_table(22, 10); raw_wpr = plfs_table(23, 10)
for e in EDU:
    i = EDU.index(e)
    for st, key in (("West Bengal", "West Bengal"), ("all India", "all India")):
        check("PLFS", f"unemployment, {key}, {e}", raw_ur[st][i], F["edu"][("UR", "rural+urban", "persons", key, e)])
        check("PLFS", f"labour force participation, {key}, {e}", raw_lf_p[st][i], F["edu"][("LFPR", "rural+urban", "persons", key, e)])
for st in ("West Bengal", "all India"):
    check("PLFS", f"graduate men in labour force, {st}", raw_lf_m[st][6], F["edu"][("LFPR", "rural+urban", "male", st, "graduate")])
    check("PLFS", f"graduate women in labour force, {st}", raw_lf_f[st][6], F["edu"][("LFPR", "rural+urban", "female", st, "graduate")])
t19, t35, t36 = plfs_table(19, 6), plfs_table(35, 10), plfs_table(36, 12)
HUB = ["Tamil Nadu", "Telangana", "Karnataka", "Maharashtra"]
alias = lambda d, s: d.get(s) or d.get({"Kerala": "Keralam"}.get(s, s))
for s_est, s in [("WEST BENGAL", "West Bengal")] + [(h.upper(), h) for h in HUB] + [("ORISSA", "Odisha"), ("JHARKHAND", "Jharkhand"), ("BIHAR", "Bihar"), ("ASSAM", "Assam"), ("ANDHRA PRADESH", "Andhra Pradesh"), ("KERALA", "Kerala")]:
    R = F["robust"][s]
    check("PLFS", f"{s}: regular wage/salaried share of workers (Table 19, column 4)", alias(t19, s)[3], float(R["regular_share_of_workers"]))
    check("PLFS", f"{s}: share of non-farm workers in limited companies (Table 35, column 4)", alias(t35, s)[3], float(R["company_share_nonagri"]))
    check("PLFS", f"{s}: regular non-farm jobs with no social security (Table 36, persons)", alias(t36, s)[10], float(R["regular_no_ssb_share"]))
RAW_INDIA = {"regular": t19["all India"][3], "company": t35["all India"][3], "nossb": t36["all India"][10]}

# bridge from pass-outs to employed graduates, rebuilt from raw inputs only
ugr = sum(raw_ug[y][2] for y in FILES); pgr = sum(raw_pg[y] for y in FILES)
lfs_r = sum(raw_ug[y][0] * raw_lf_m["West Bengal"][6] / 100 + raw_ug[y][1] * raw_lf_f["West Bengal"][6] / 100 for y in FILES)
ur_r = raw_ur["West Bengal"][6] / 100
inlf_r = (ugr - pgr) * lfs_r / ugr
formal_1825 = sum(sep[(y, "18-21")] + sep[(y, "22-25")] for y in facts.YEARS); formal_2225 = sum(sep[(y, "22-25")] for y in facts.YEARS)
B = F["bridge"]
check("bridge", "PG pass-outs, five years (proxy for continuing to a master's)", pgr, B["pg"])
check("bridge", "PG pass-outs are about 19% of UG pass-outs", round(pgr / ugr * 100), 19)
check("bridge", "graduates outside the labour force after PG deduction (thousands)", round((ugr - pgr - inlf_r) / 1000), round(B["out_lf"] / 1000))
check("bridge", "unemployed graduates (thousands)", round(inlf_r * ur_r / 1000), round(B["unemployed"] / 1000))
emp_r = inlf_r * (1 - ur_r); emp0_r = lfs_r * (1 - ur_r)
check("bridge", "employed graduates, PG deducted (thousands)", round(emp_r / 1000), round(B["employed"] / 1000))
for nm, got, key in (("PG deducted, ages 18-25", emp_r - formal_1825, "res_pg_1825"), ("PG deducted, ages 22-25", emp_r - formal_2225, "res_pg_2225"),
                     ("no PG deduction, ages 18-25", emp0_r - formal_1825, "res_nopg_1825"), ("no PG deduction, ages 22-25", emp0_r - formal_2225, "res_nopg_2225")):
    check("bridge", f"remainder after adjustments, {nm} (thousands)", round(got / 1000), round(B[key] / 1000))
check("bridge", "the four remainders range from about -0.05 to +0.54 million", (round(min(B[k] for k in ("res_pg_1825", "res_pg_2225", "res_nopg_1825", "res_nopg_2225")) / 1e6, 2), round(max(B[k] for k in ("res_pg_1825", "res_pg_2225", "res_nopg_1825", "res_nopg_2225")) / 1e6, 2)), (-0.05, 0.54))
import math
for nn, want in ((15000, 0.98), (1250, 3.4)):
    check("design", f"margin of error for {nn} respondents (95%, design effect 1.5), points", round(1.96 * math.sqrt(1.5 * 0.25 / nn) * 100, 2 if nn == 15000 else 1), want)

# ---------- 3b. Average regular wage by state (Table 38) and by occupation (Table 51): two text routes that must agree
def t38_rows(text_pages, mode):
    if mode == "raw":
        hits = [p for p in text_pages if re.search(r"Table \(38\):", p) and re.search(r"^West Bengal ", p, re.M)]
        page = hits[-1]
        lines = page.splitlines()
    else:
        hits = [p for p in text_pages if re.search(r"Table \(38\):", p) and re.search(r"^West Bengal ", p, re.M)]
        lines = [re.sub(r"\s{2,}", " ", l) for l in hits[-1].splitlines()]
    out = {}
    for l in lines:
        m = re.match(r"^([A-Za-z&.\- ]+?) ((?:[\d,]+ ){8}[\d,]+)$", l.strip())
        if m:
            out[m.group(1).strip()] = [int(x.replace(",", "")) for x in m.group(2).split()]
    return out
lay_pages = pdf_text(next((ROOT / "raw/plfs").glob("*PLFS_2025_F_REV*.pdf")), "-layout").split("\f")
w_raw, w_lay = t38_rows(ann, "raw"), t38_rows(lay_pages, "layout")
check("wages", "Table 38 rows read by the two text routes agree (number of states and UTs)", (len(w_raw), w_raw == w_lay), (36, True))
check("wages", "West Bengal average regular wage or salary, persons, rural+urban (Rs a month)", w_raw["West Bengal"][8], 16618)
check("wages", "India average regular wage or salary, persons, rural+urban", w_raw["all India"][8], 22699)
states_w = {k: v[8] for k, v in w_raw.items() if k != "all India"}
rank_w = sorted(states_w, key=states_w.get)
check("wages", "West Bengal is the second lowest of 35 states and UTs", (rank_w.index("West Bengal") + 1, len(rank_w)), (2, 35))
check("wages", "only Punjab is lower than West Bengal", rank_w[0], "Punjab")
check("wages", "West Bengal is 27% below India", round((1 - w_raw["West Bengal"][8] / w_raw["all India"][8]) * 100), 27)
check("wages", "West Bengal urban average regular wage (persons) and India's", (w_raw["West Bengal"][5], w_raw["all India"][5]), (19019, 26247))
occ_pages = [p for p in ann if re.search(r"Table \(51\):", p)]
occ_lines = [l for l in occ_pages[-1].splitlines() if l.startswith("Average wage/salary earnings")]
occ_all = [[int(x.replace(",", "")) for x in re.findall(r"[\d,]{3,}", l)] for l in occ_lines]
occ_p = occ_all[2]
check("wages", "Table 51 (India, by occupation) all-occupation average equals Table 38's India figure", occ_p[9], w_raw["all India"][8])
check("wages", "Table 51 persons: managers, professionals, elementary occupations", (occ_p[0], occ_p[1], occ_p[8]), (50408, 38466, 12270))

# printed page labels for the source map
def page_label(tno, last=True):
    hits = [p for p in ann if re.search(rf"Table \({tno}\):", p) and re.search(r"^West Bengal ", p, re.M)]
    m = re.search(r"A-\d+", hits[-1] if last else hits[0])
    return m.group(0) if m else ""
labels = {t: page_label(t) for t in (19, 22, 23, 24, 35, 36, 38)}
_h22 = [p for p in ann if re.search(r"Table \(22\):", p) and re.search(r"^West Bengal ", p, re.M)]
labels["22f"] = re.search(r"A-\d+", _h22[-2]).group(0)
_sep_pages = pdf_text(next((ROOT / "raw/epfo").glob("*September-2025*.pdf")), "-layout").split("\f")
_state_pp = [i + 1 for i, p in enumerate(_sep_pages) if "Age Bucket:" in p and "State" in p and "WEST BENGAL" in p]
labels["epfo_state_pages"] = f"{min(_state_pp)} to {max(_state_pp)}"
labels["51"] = (re.search(r"A-\d+", occ_pages[-1]) or [""])[0] if re.search(r"A-\d+", occ_pages[-1]) else ""

# ---------- 3c. What the payroll figure is made of (national flows), West Bengal's share, and NEET by sex
FYS8 = ["2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
tots = re.findall(r"^\s*Total\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$", t, re.M)[:8]
flows = {fy: tuple(map(int, x)) for fy, x in zip(FYS8, tots)}
for fy_ in ("2022-23", "2023-24", "2024-25"):
    a1, b1, c1, d1 = flows[fy_]
    check("payroll", f"national net payroll {fy_} = new subscribers - exits + rejoiners", a1 - b1 + c1, d1)
check("payroll", "national flows 2024-25 (new subscribers, exits, rejoiners, net)", flows["2024-25"], (11391301, 18344519, 19931386, 12978168))
row1 = re.search(r"2024-25\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", t).groups()
check("payroll", "national net payroll 2024-25 agrees between the age-band table and the flows table", int(row1[6]), flows["2024-25"][3])
india_1825 = int(row1[1]) + int(row1[2])
wb_all = sum(sep[("2024-25", b)] for b in BK); wb_1825 = sep[("2024-25", "18-21")] + sep[("2024-25", "22-25")]
check("payroll", "West Bengal share of India's net new payroll, 2024-25, all ages (per cent, one decimal)", round(wb_all / int(row1[6]) * 100, 1), 3.5)
check("payroll", "West Bengal share of India's net new payroll aged 18-25, 2024-25 (per cent, one decimal)", round(wb_1825 / india_1825 * 100, 1), 3.3)
wbk = openpyxl.load_workbook(ROOT / "raw/aishe" / FILES["2023-24"], read_only=True, data_only=True)
shp = next(nm for nm in wbk.sheetnames if nm.replace(" ", "").startswith("38"))
pop_states = {}
for r in wbk[shp].iter_rows(values_only=True):
    c = [x for x in r if x is not None]
    if len(c) >= 5 and isinstance(c[0], (int, float)) and isinstance(c[1], str):
        pop_states[c[1].strip()] = c[4]
pop_all = sum(pop_states.values())
check("payroll", "population aged 18-23 across the 36 states and union territories, 2023-24", (len(pop_states), pop_all), (36, 149880817))
check("payroll", "West Bengal share of India's population aged 18-23 (per cent, one decimal)", round(pop_states["West Bengal"] / pop_all * 100, 1), 6.7)
check("payroll", "India net new payroll aged 18-25 per 100 people aged 18-23, 2024-25 (one decimal)", round(india_1825 / pop_all * 100, 1), 4.3)
check("payroll", "West Bengal net new payroll aged 18-25 per 100 people aged 18-23, 2024-25 (one decimal)", round(wb_1825 / pop_states["West Bengal"] * 100, 1), 2.1)
def neet_rows(pages_list):
    hits = [p for p in pages_list if re.search(r"Table \(57\.1\):", p) and re.search(r"^West Bengal ", p, re.M)]
    assert len(hits) == 9
    out = []
    for p in hits[-3:]:
        d = {}
        for l in p.splitlines():
            m = re.match(r"^\s*(West Bengal|all India)\s+((?:[\d.]+\s+){3}[\d.]+)\s*$", re.sub(r"\s{2,}", " ", l))
            if m: d[m.group(1)] = [float(x) for x in m.group(2).split()]
        out.append(d)
    return out
n_raw, n_lay = neet_rows(ann), neet_rows(lay_pages)
check("payroll", "NEET table read by two text routes agrees", n_raw == n_lay, True)
neet = {k: {"male": n_raw[0][k][1], "female": n_raw[1][k][1], "persons": n_raw[2][k][1]} for k in ("West Bengal", "all India")}
check("payroll", "NEET ages 15-29, West Bengal: men, women, persons", (neet["West Bengal"]["male"], neet["West Bengal"]["female"], neet["West Bengal"]["persons"]), (8.6, 49.0, 29.9))
check("payroll", "NEET ages 15-29, India: men, women, persons", (neet["all India"]["male"], neet["all India"]["female"], neet["all India"]["persons"]), (8.0, 42.2, 25.0))
check("payroll", "persons NEET agrees with the district snapshot's West Bengal figure", neet["West Bengal"]["persons"], float([r for r in F["districts"] if r["level"] == "state"][0]["neet_15_29"]))

# ---------- 4. City report and district snapshot
city = pdf_text(next((ROOT / "raw/plfs").glob("*Million_plus_city_F.pdf")), "-layout").splitlines()
def city_rows(prefix):
    start = next(i for i, l in enumerate(city) if l.startswith(prefix))
    end = next(i for i, l in enumerate(city) if i > start and re.match(r"Table \d+(\.\d+)?:", l))
    out = {}
    for l in city[start:end]:
        m = re.match(r"^\s*(.+?\S)\s{2,}([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*$", l)
        if m and "million" not in m.group(1) and "India" not in m.group(1):
            out[m.group(1)] = int(m.group(4).replace(",", ""))
    return out
wages = city_rows("Table 8:")
ranked = sorted(wages, key=wages.get)
check("PLFS cities", "number of million-plus cities with a regular wage estimate", len(wages), 46)
check("PLFS cities", "Kolkata average regular wage (Rs a month)", wages["Kolkata MC"], 19093)
check("PLFS cities", "Kolkata rank among cities from the lowest wage (5 = fifth lowest)", ranked.index("Kolkata MC") + 1, 5)
check("PLFS cities", "Howrah rank from the lowest wage", ranked.index("Howrah MC") + 1, 16)
check("PLFS cities", "Greater Mumbai average regular wage", wages["Greater Mumbai MC"], 36267)
check("PLFS cities", "Chennai average regular wage", wages["Chennai MC"], 28955)
snap = pdf_text(next((ROOT / "raw/plfs").glob("*Selected Districts*.pdf")), "-layout").splitlines()
i0 = next(i for i, l in enumerate(snap) if l.strip() == "West Bengal")
raw_d = {}
for l in snap[i0:i0 + 45]:
    m = re.match(r"^\s*(?:\d+\.\s+)?([A-Za-z\- ]+?)\s{2,}([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$", l)
    if m:
        raw_d[m.group(1).strip()] = tuple(float(x) for x in m.groups()[1:])
for r in F["districts"]:
    check("PLFS districts", f"{r['name']}: unemployment and NEET 15-29", (raw_d[r["name"]][2], raw_d[r["name"]][3]), (float(r["ur_15plus"]), float(r["neet_15_29"])))

ur_block = city[next(i for i, l in enumerate(city) if l.startswith("Table 11:")):]
kol_ur = re.search(r"^Kolkata MC\s+(\S+)\s+(\S+)\s+(\S+)\s*$", "\n".join(ur_block), re.M).groups()
how_ur = re.search(r"^Howrah MC\s+(\S+)\s+(\S+)\s+(\S+)\s*$", "\n".join(ur_block), re.M).groups()
check("PLFS cities", "Kolkata persons unemployment rate carries no high-error flag (the flag sits on the female rate)", kol_ur, ("2.2", "1.2*", "1.9"))
check("PLFS cities", "Howrah persons unemployment rate is flagged as a high-error estimate", how_ur[2], "0.8*")

rse_block = city[next(i for i, l in enumerate(city) if l.startswith("Table 13.1:")):]
rse_k = re.search(r"^Kolkata MC\s+((?:[\d.]+\s+){8}[\d.]+)\s*$", "\n".join(rse_block), re.M).group(1).split()
check("PLFS cities", "relative standard error of Kolkata's persons unemployment rate is 28.8% (below the 40% flag)", float(rse_k[8]), 28.8)

# ---------- 5. Derived claims used in the text
S = F["states"]
fy = F["wb_fy"]
check("claim", "West Bengal UG pass-outs, five years", sum(raw_ug[y][2] for y in FILES), 1885522)
check("claim", "West Bengal formal entrants aged 18-25, five years (same financial-year labels)", sum(sep[(y, "18-21")] + sep[(y, "22-25")] for y in facts.YEARS), 890027)
check("claim", "2024-25 net formal payroll, all ages", sum(sep[("2024-25", b)] for b in BK), 457697)
check("claim", "2024-25 net formal payroll, ages 18-25", sep[("2024-25", "18-21")] + sep[("2024-25", "22-25")], 212064)
check("claim", "net payroll peaked in 2022-23 (all ages)", max(facts.FYS, key=lambda y: fy[y]["all"]), "2022-23")
young = [fy[y]["y1825"] for y in ("2022-23", "2023-24", "2024-25")]
check("claim", "ages 18-25 stayed within 5% of 212,000 for three years", max(abs(v - 212064) / 212064 for v in young) < 0.05, True)
a25 = sum(F["wb_month"][m] for m in ("Apr-25", "May-25", "Jun-25", "Jul-25")); a24 = sum(F["wb_month"][m] for m in ("Apr-24", "May-24", "Jun-24", "Jul-24"))
check("claim", "April-July 2025 net payroll", a25, 214690); check("claim", "April-July 2024 net payroll", a24, 176091)
check("claim", "April-July 2025 is about 22% above April-July 2024", round((a25 / a24 - 1) * 100), 22)
check("claim", "October is West Bengal's lowest month, Apr-Nov 2024", min([m for m in F["wb_month"] if m.endswith("24")], key=F["wb_month"].get), "Oct-24")
for k, v in {"A": 0.47, "B": 0.26, "C": 0.51, "D": 0.76}.items():
    check("claim", f"scenario {k} ratio", round(F["scen"][k], 2), v)
check("claim", "shortfall under baseline is about 1.0 million", round(F["gap_baseline"] / 1e6, 1), 1.0)
check("claim", "shortfall under labour-force reading is about 0.28 million", round(F["gap_lf"] / 1e6, 2), 0.28)
check("claim", "every scenario ratio is below one", all(v < 1 for v in F["scen"].values()), True)
check("claim", "women's share of 2023-24 UG pass-outs is 52%", round(raw_ug["2023-24"][1] / raw_ug["2023-24"][2] * 100), 52)
check("claim", "ten points more participation among 2023-24 women pass-outs = about 18,000", round(raw_ug["2023-24"][1] * 0.10, -3), 18000)
def epfo_states_2324(pdf):
    out, bucket, periods, in_state = {}, None, None, False
    for line in pdf_text(pdf, "-layout").splitlines():
        if "STATEWISE NEW PAYROLL DATA" in line: in_state = True
        elif "INDUSTRY WISE PAYROLL DATA" in line: in_state = False
        if not in_state: continue
        m = re.match(r"\s*Age Bucket:\s*(.+?)\s*$", line)
        if m: bucket = m.group(1)
        elif line.startswith("State") and "2017-18" in line: periods = line.split()[1:]
        else:
            m = re.match(r"^([A-Z][A-Z &]+?)\s{2,}(-?\d[\d\s-]*)$", line)
            if m and bucket in ("18-21", "22-25") and periods and m.group(1) not in ("SUB TOTAL", "TOTAL"):
                vals = [int(v) for v in m.group(2).split()]
                if len(vals) == len(periods):
                    out[(m.group(1).strip(), bucket)] = vals[periods.index("2023-24")]
    return out
raw_es = epfo_states_2324(next((ROOT / "raw/epfo").glob("*September-2025*.pdf")))
EPFO_NAME = {"Odisha": "ORISSA", "West Bengal": "WEST BENGAL"}
for st, v in (("Odisha", 1.9), ("Jharkhand", 1.0), ("Bihar", 0.3), ("Assam", 0.7), ("Andhra Pradesh", 2.3), ("Kerala", 2.8), ("Tamil Nadu", 9.7), ("Telangana", 10.3), ("Karnataka", 10.8), ("Maharashtra", 11.1), ("West Bengal", 2.1)):
    check("claim", f"{st}: formal entrants per 100 young people, 2023-24", float(S[st]["epfo_per_100_youth_2023_24"]), v)
    pop = raw_pop[("2023-24", st)]
    es = EPFO_NAME.get(st, st.upper())
    check("claim", f"{st}: formal entrants per 100 young people recomputed from the raw payroll PDF and AISHE population", round((raw_es[(es, "18-21")] + raw_es[(es, "22-25")]) / pop * 100, 1), v)
check("claim", "West Bengal records more than Odisha? No: Odisha, Jharkhand, Bihar, Assam are all lower than West Bengal", all(float(S[s]["epfo_per_100_youth_2023_24"]) < float(S["West Bengal"]["epfo_per_100_youth_2023_24"]) for s in ("Odisha", "Jharkhand", "Bihar", "Assam")), True)
hub = [float(S[h]["epfo_per_100_youth_2023_24"]) for h in HUB]
check("claim", "four large states record 9.7 to 11.1 per 100", (min(hub), max(hub)), (9.7, 11.1))
adj = {r["state"]: r for r in facts.rows("adjacent_states_summary.csv")}
lead = [c for c in ("ratio_A_baseline", "ratio_B_22_25_only", "ratio_C_lag", "ratio_D_lf_adjusted")
        if all(float(adj["West Bengal"][c]) > float(adj[s][c]) for s in ("Odisha", "Jharkhand", "Bihar", "Assam"))]
check("claim", "West Bengal's ratio is the highest of its four neighbours under all four scenarios", len(lead), 4)
R = F["robust"]
def rho(a, b):
    def rk(x):
        o = sorted(range(len(x)), key=lambda i: x[i]); r = [0] * len(x)
        for k, i in enumerate(o): r[i] = k + 1
        return r
    ra, rb = rk(a), rk(b); n = len(a)
    return 1 - 6 * sum((p - q) ** 2 for p, q in zip(ra, rb)) / (n * (n * n - 1))
sts = list(R)
e_ = [float(R[s]["epfo_per_100_youth"]) for s in sts]
check("claim", "rank correlation, EPFO vs limited-company share", round(rho(e_, [float(R[s]["company_share_nonagri"]) for s in sts]), 2), 0.99)
check("claim", "rank correlation, EPFO vs formal-job density", round(rho(e_, [float(R[s]["formal_job_density_per_100"]) for s in sts]), 2), 0.88)
check("claim", "rank correlation, EPFO vs regular share", round(rho(e_, [float(R[s]["regular_share_of_workers"]) for s in sts]), 2), 0.83)
dens = [float(R[h]["formal_job_density_per_100"]) for h in HUB]
wbd = float(R["West Bengal"]["formal_job_density_per_100"])
check("claim", "West Bengal formal-job density against four large states", (wbd, min(dens), max(dens)), (5.1, 9.0, 12.3))
check("claim", "West Bengal density is 0.41 to 0.57 of theirs", (round(wbd / max(dens), 2), round(wbd / min(dens), 2)), (0.41, 0.57))
check("claim", "formal-job density recomputed from raw tables for West Bengal (WPR x regular share x share with social security)", round(raw_wpr["West Bengal"][9] * t19["West Bengal"][3] / 100 * (1 - t36["West Bengal"][10] / 100), 1), 5.1)
check("claim", "limited-company share: West Bengal 8.3, India 11.7, four large states 13.8-24.3", (t35["West Bengal"][3], RAW_INDIA["company"], min(t35[h][3] for h in HUB), max(t35[h][3] for h in HUB)), (8.3, 11.7, 13.8, 24.3))
check("claim", "no social security: West Bengal 60.5, India 51.7, four large states 36.4-45.1", (t36["West Bengal"][10], RAW_INDIA["nossb"], min(t36[h][10] for h in HUB), max(t36[h][10] for h in HUB)), (60.5, 51.7, 36.4, 45.1))
check("claim", "regular share: West Bengal 22.3, India 23.6, four large states 27.1-37.3", (t19["West Bengal"][3], RAW_INDIA["regular"], min(t19[h][3] for h in HUB), max(t19[h][3] for h in HUB)), (22.3, 23.6, 27.1, 37.3))
check("claim", "only Bihar has more regular non-farm jobs without social security than West Bengal, among the states compared", sorted([s for s in sts if float(R[s]["regular_no_ssb_share"]) > 60.5]), ["Bihar"])
check("claim", "graduate unemployment against all-adult rate is about four times", round(raw_ur["West Bengal"][6] / raw_ur["West Bengal"][9]), 4)
gu = [float(S[h]["grad_ur"]) for h in HUB]
check("claim", "graduate unemployment in the four large states ranges 6.8 to 17.6", (min(gu), max(gu)), (6.8, 17.6))
gm = [raw_lf_m[h][6] for h in HUB]; gf = [raw_lf_f[h][6] for h in HUB]
check("claim", "graduate men in labour force, four large states 85.0-87.9", (min(gm), max(gm)), (85.0, 87.9))
check("claim", "graduate women in labour force, four large states 38.8-44.5", (min(gf), max(gf)), (38.8, 44.5))
nonk = [(r["name"], float(r["neet_15_29"])) for r in F["districts"] if r["level"] == "district" and r["name"] != "Kolkata"]
check("claim", "NEET 15-29 across the nine other districts ranges 25.6 to 38.2", (min(v for _, v in nonk), max(v for _, v in nonk)), (25.6, 38.2))
check("claim", "Kolkata has the lowest NEET among the ten districts", min(F["districts"][1:], key=lambda r: float(r["neet_15_29"]))["name"], "Kolkata")
check("claim", "matching Tamil Nadu would need about 4.6 times West Bengal's formal entry (payroll measure)", round(min(hub) / float(S["West Bengal"]["epfo_per_100_youth_2023_24"]), 1), 4.6)
check("claim", "matching the lowest large state needs 1.8 to 2.4 times on the survey measure", (round(min(dens) / wbd, 1), round(max(dens) / wbd, 1)), (1.8, 2.4))

# AISHE 2023-24 fall and response rates (raw workbooks)
check("claim", "West Bengal UG pass-outs fell 18% from 2022-23 to 2023-24", round((raw_ug["2023-24"][2] / raw_ug["2022-23"][2] - 1) * 100), -18)
resp, univ = {}, {}
for y in ("2022-23", "2023-24"):
    wbk = openpyxl.load_workbook(ROOT / "raw/aishe" / FILES[y], read_only=True, data_only=True)
    sh = next(n for n in wbk.sheetnames if "insresponse" in n.lower().replace(" ", ""))
    for r in wbk[sh].iter_rows(values_only=True):
        if any(isinstance(c, str) and c.strip() == "West Bengal" for c in r):
            nums = [c for c in r if isinstance(c, (int, float))]
            resp[y] = (nums[-3], nums[-2])
            univ[y] = (nums[1], nums[2])
check("claim", "West Bengal institutions responding 2022-23 (registered, responded)", resp["2022-23"], (2249, 2243))
check("claim", "West Bengal institutions responding 2023-24 (registered, responded)", resp["2023-24"], (2435, 2331))
check("claim", "AISHE counts 59 universities in West Bengal in 2023-24 (registered, responded)", univ["2023-24"], (59, 59))
check("claim", "response rate fell by less than 5 points while pass-outs fell 18%", round(resp["2022-23"][1] / resp["2022-23"][0] * 100 - resp["2023-24"][1] / resp["2023-24"][0] * 100) < 5, True)
for st in ("Tamil Nadu", "Telangana", "Karnataka", "Maharashtra", "West Bengal"):
    check("claim", f"{st}: undergraduate pass-outs per 100 young people, 2023-24", round(F["ug"][("2023-24", st)][2] / raw_pop[("2023-24", st)] * 100, 1), float(S[st]["ug_per_100_youth_2023_24"]))
ratio_ug = [float(S["West Bengal"]["ug_per_100_youth_2023_24"]) / float(S[h]["ug_per_100_youth_2023_24"]) for h in HUB]
check("claim", "West Bengal's graduate output per young person is 38% to 64% of the four large states'", (round(min(ratio_ug) * 100), round(max(ratio_ug) * 100)), (38, 64))
import json
json.dump({"flows": flows, "wb_share": {"all": wb_all / int(row1[6]), "y1825": wb_1825 / india_1825, "pop": pop_states["West Bengal"] / pop_all, "india_per100": india_1825 / pop_all * 100, "wb_all": wb_all, "wb_1825": wb_1825, "india_all": int(row1[6]), "india_1825": india_1825, "pop_all": pop_all}, "neet": neet, "avg_wage": {k: v for k, v in w_raw.items()}, "occ_wage": occ_p, "page_labels": labels, "wages": wages, "india": RAW_INDIA, "kolkata_ur_rse": float(rse_k[8]), "months_national_total": nat},
          open(Path(__file__).resolve().parent / "validated_values.json", "w"), indent=1)

# ---------- write the log
out = Path(__file__).resolve().parent / "validation_log.csv"
with open(out, "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["group", "claim", "value found", "value expected", "result"]); w.writerows(LOG)
fails = [r for r in LOG if r[4] == "FAIL"]
print(f"{len(LOG)} checks, {len(LOG) - len(fails)} passed, {len(fails)} failed")
for r in fails: print("FAIL:", r[:4])
sys.exit(1 if fails else 0)
