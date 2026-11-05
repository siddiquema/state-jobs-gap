"""All figures used in the report, computed from the cleaned tables in data/ (no number is typed into the report text).
Independent re-derivation from the raw source files is done in report/validate.py; the report build refuses to run unless that passes.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
YEARS = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]
FYS = ["2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
BUCKETS = ["Less than 18", "18-21", "22-25", "26-28", "29-35", "More than 35"]


def rows(name):
    return list(csv.DictReader(open(D / name)))


def build():
    F = {}
    # --- AISHE undergraduate pass-outs
    ug = {}
    for r in rows("aishe_outturn_by_state.csv"):
        if r["level"] == "Under Graduate":
            ug[(r["year"], r["state"])] = (int(r["male"]), int(r["female"]), int(r["total"]))
    F["ug"] = ug
    F["wb_ug"] = {y: ug[(y, "West Bengal")] for y in YEARS}
    F["wb_ug_5yr"] = sum(v[2] for v in F["wb_ug"].values())
    # --- EPFO West Bengal and all states (newest release wins)
    ep, rel = {}, {}
    for r in rows("epfo_statewise_net_payroll.csv"):
        k = (r["period"], r["state"], r["age_bucket"])
        if k not in rel or r["release_date"] > rel[k]:
            rel[k], ep[k] = r["release_date"], int(r["net_payroll"])
    F["ep"] = ep
    wb = "WEST BENGAL"
    F["wb_fy"] = {fy: {"all": sum(ep[(fy, wb, b)] for b in BUCKETS), "y1825": ep[(fy, wb, "18-21")] + ep[(fy, wb, "22-25")],
                       "y2225": ep[(fy, wb, "22-25")]} for fy in FYS}
    months = ["Apr-24", "May-24", "Jun-24", "Jul-24", "Aug-24", "Sep-24", "Oct-24", "Nov-24", "Apr-25", "May-25", "Jun-25", "Jul-25"]
    F["wb_month"] = {m: sum(ep[(m, wb, b)] for b in BUCKETS) for m in months}
    # --- gap and scenarios (West Bengal)
    sup = F["wb_ug_5yr"]
    a = sum(F["wb_fy"][y]["y1825"] for y in YEARS)
    F["gap"] = {y: {"ug": F["wb_ug"][y][2], "ep": F["wb_fy"][y]["y1825"]} for y in YEARS}
    F["ep_5yr"] = a
    edu = {(r["indicator"], r["sector"], r["sex"], r["state"], r["education"]): float(r["value"].rstrip("*")) for r in rows("plfs2025_education_by_state.csv")}
    F["edu"] = edu
    lfm = edu[("LFPR", "rural+urban", "male", "West Bengal", "graduate")] / 100
    lff = edu[("LFPR", "rural+urban", "female", "West Bengal", "graduate")] / 100
    F["scen"] = {
        "A": a / sup,
        "B": sum(F["wb_fy"][y]["y2225"] for y in YEARS) / sup,
        "C": sum(F["wb_fy"][y]["y1825"] for y in FYS[2:]) / sup,
        "D": a / sum(F["wb_ug"][y][0] * lfm + F["wb_ug"][y][1] * lff for y in YEARS),
    }
    F["lf_supply"] = sum(F["wb_ug"][y][0] * lfm + F["wb_ug"][y][1] * lff for y in YEARS)
    F["gap_baseline"] = sup - a
    F["gap_lf"] = F["lf_supply"] - a
    # --- bridge from pass-outs to employed graduates (illustrative, five years)
    pg = {r["year"]: int(r["total"]) for r in rows("aishe_outturn_by_state.csv") if r["state"] == "West Bengal" and r["level"] == "Post Graduate"}
    F["wb_pg"] = pg
    ur_g = edu[("UR", "rural+urban", "persons", "West Bengal", "graduate")] / 100
    pg5 = sum(pg[y] for y in YEARS)
    remaining = sup - pg5
    share = F["lf_supply"] / sup
    in_lf = remaining * share
    f2225 = sum(F["wb_fy"][y]["y2225"] for y in YEARS)
    emp_pg, emp_nopg = in_lf * (1 - ur_g), F["lf_supply"] * (1 - ur_g)
    F["bridge"] = {"ug": sup, "pg": pg5, "remaining": remaining, "lf_share": share, "in_lf": in_lf, "out_lf": remaining - in_lf, "unemployed": in_lf * ur_g,
                   "employed": emp_pg, "employed_no_pg": emp_nopg, "formal_1825": a, "formal_2225": f2225,
                   "res_pg_1825": emp_pg - a, "res_pg_2225": emp_pg - f2225, "res_nopg_1825": emp_nopg - a, "res_nopg_2225": emp_nopg - f2225}
    # --- states: per 100 youth, graduate unemployment, NEET (cleaned tables)
    st = {}
    for f in ("large_states_summary.csv", "adjacent_states_summary.csv"):
        for r in rows(f):
            st[r["state"]] = r
    F["states"] = st
    F["robust"] = {r["state"]: r for r in rows("robustness_plfs.csv")}
    F["districts"] = [r for r in rows("plfs2025_district_snapshot.csv") if r["state"] == "West Bengal"]
    F["kolkata"] = {r["indicator"] + "|" + r["age_group"]: r for r in rows("plfs2025_kolkata_howrah_vs_benchmarks.csv")}
    F["cities_tn"] = rows("tamil_nadu_cities.csv")
    F["cities_mh"] = rows("maharashtra_cities.csv")
    return F


def margin_of_error(n, deff=1.5, p=0.5):
    """95% margin of error in percentage points for a proportion from n respondents, design effect deff."""
    return 1.96 * (deff * p * (1 - p) / n) ** 0.5 * 100


if __name__ == "__main__":
    F = build()
    print({k: round(v, 3) for k, v in F["scen"].items()}, F["wb_ug_5yr"], F["ep_5yr"], round(F["gap_baseline"]), round(F["gap_lf"]))
