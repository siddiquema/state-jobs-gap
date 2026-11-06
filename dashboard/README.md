# Dashboard: West Bengal graduates, formal jobs and the gap

A single-page dashboard that presents the findings in `analysis/`. It was published as an Artifact of type "Dashboard" (title "West Bengal Graduate Gap"); this folder holds everything needed to rebuild it.

| File | What it is |
|---|---|
| `index.html` | The page: text, charts and tables. Scripts read the datasets below; every number on the page comes from a dataset. |
| `manifest.json` | The ten datasets the page reads: id, title, description, file, and the table in `data/` each is built from. |
| `data/` | The two derived data files are stored here. The other eight are exact copies of tables in the repo's `data/` folder, so they are not stored twice: `scripts/build_dashboard_data.py` recreates them (git ignores them). |

## Rebuild the data
```bash
python3 -I scripts/build_dashboard_data.py
```
This writes all ten files into `dashboard/data/`. Eight are plain copies of cleaned tables in `data/` (see `manifest.json`, field `built_from`), recreated on demand and ignored by git. Four are derived and committed: `education-wb-vs-india.csv` (from `plfs2025_education_by_state.csv`), `west-bengal-districts.csv` (from `plfs2025_district_snapshot.csv`), and `gap-bridge-steps.csv` and `gap-bridge-cases.csv` (the bridge from pass-outs to employed graduates, computed in `report/facts.py`). The files matched, byte for byte, those attached to the published dashboard on 2026-11-06.

## Republish or recreate
1. Create an Artifact from the Dashboard type, titled as in `manifest.json`.
2. Run the script above, then attach each `dashboard/data/*.csv` file as a dataset, using the ids, titles and descriptions in `manifest.json` (all are fixed files, not live queries).
3. Write `index.html` as the page file.

Dataset ids matter: the page reads them by id (`gap`, `peers`, `education`, `districts`, `kolkata`, `sens`, `youth`, `adjacent`, `south`, `robust`, `bridgesteps`, `bridgecases`). The `/_blob/` URLs inside a published dashboard belong to that artifact and are not stored here.

## Notes
- The published page is a snapshot of the analysis at 2026-11-05. If `analysis/` changes, rebuild the data and update the page text; numbers in the page come from the data files, but some sentences (for example, which states form the "high-entry" group) are fixed wording in `index.html`.
- `kolkata-benchmarks.csv` (from `data/plfs2025_kolkata_howrah_vs_benchmarks.csv`) was copied by hand from the PLFS Million-plus Cities report. `scripts/extract_plfs_city_rows.py` extracts the same indicators for any cities directly from that report.
