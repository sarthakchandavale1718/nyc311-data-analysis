# NYC 311 Service Requests: End-to-End Data Analytics Case Study

**Tools:** Python, pandas, matplotlib, JavaScript (Chart.js), Power BI | **Data:** NYC Open Data (public) | **Domain:** Public services analytics

> Fill every `[bracket]` with numbers from your own `cleaning_log.txt` and `insights.md` before submitting.

---
## 1. Problem statement
New York City's 311 line receives millions of non-emergency complaints about noise, heating, parking, sanitation and street conditions. City agencies must decide where to send staff and how to cut response times, but the raw data is messy and hard to read at a glance.

**Goal:** turn raw 311 records into a clean dataset, find what drives demand and delays, and present the findings in an interactive dashboard that decision makers can use.

### Business questions
1. What do residents complain about most?
2. Which boroughs generate the most requests, and do their problems differ?
3. When (hour, weekday, date) does demand peak, and are there unusual spikes?
4. How quickly are requests resolved, and which agencies are fastest or slowest?
5. How many requests remain open (backlog)?

## 2. Dataset
| Item | Detail |
|---|---|
| Source | NYC Open Data, "311 Service Requests from 2010 to Present" |
| Link | https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9 |
| Sample used | 50,000 rows pulled via the public API |
| Raw size | [rows] rows x [columns] columns |
| Cleaned size | [rows] rows x [columns] columns |
| Key fields | `unique_key`, `created_date`, `closed_date`, `agency`, `complaint_type`, `borough`, `status`, `incident_zip`, `latitude`, `longitude` |
| Added field | `resolution_hours` (closed minus created) |

Limitation: this is a sample, not the full history, so findings describe the sample.

## 3. Data cleaning (Task 1)
Script: [`task1-data-cleaning/clean_nyc311.py`](task1-data-cleaning/clean_nyc311.py). Full log: `cleaning_log.txt`.

| Problem | Found | Action |
|---|---|---|
| Missing values | [N] columns over 90% empty; partial gaps elsewhere | Dropped sparse columns; filled borough/city with "Unknown"; left coordinates, ZIP and close date missing on purpose |
| Placeholder text | [N] values ("Unspecified", "N/A", blanks) | Converted to true missing values |
| Duplicates | [N] rows | Removed by row and by `unique_key` |
| Wrong data types | Everything loaded as text | Dates to datetime, coordinates to numbers, labels to categories |
| Inconsistent values | [N] spelling and case variants | Merged to the most common spelling |
| Invalid values | [N] bad ZIPs, [N] out-of-NYC coordinates, [N] close dates before open dates | Standardised or set to missing |

**Why not fill everything?** Open requests legitimately have no close date and guessing locations would invent data, so those gaps were kept.

## 4. Exploratory analysis (Task 2)
Script: [`task2-eda/eda_nyc311.py`](task2-eda/eda_nyc311.py). Outputs: `charts/`, `summary_statistics.csv`, `insights.md`.

Methods: descriptive statistics; counts by category and time; robust z-score (median and MAD above 3.5) for spike days; IQR rule for resolution outliers; median used instead of mean because resolution time is right-skewed.

![Top complaints](task2-eda/charts/01_top_complaint_types.png)
![Hourly pattern](task2-eda/charts/03_requests_by_hour.png)
![Daily trend](task2-eda/charts/05_daily_trend.png)

## 5. Dashboard (Task 3)
- **Interactive web dashboard:** [`task3-dashboard/dashboard.html`](task3-dashboard/dashboard.html). Open it, load the cleaned CSV, filter by borough, agency, complaint, status and date, or click bars to cross-filter.
- **Power BI version:** build steps, DAX measures and theme in [`task3-dashboard/powerbi/`](task3-dashboard/powerbi/).
- KPIs: total requests, median resolution hours, closure rate, open requests, top complaint, peak hour.

![Dashboard overview](screenshots/overview.png)

## 6. Key business insights
| # | Insight | Evidence | Business implication |
|---|---|---|---|
| 1 | Complaints are concentrated in a few types | [Top type] is [X]% of requests; top 3 are [Y]% | Prioritise staffing and prevention programs for these categories |
| 2 | Demand differs by borough | [Borough] has [X]% of requests; leading complaint varies by borough | Allocate crews locally instead of one citywide plan |
| 3 | Demand follows a daily and weekly rhythm | Peak at [hour]:00; weekdays [X]% busier than weekends | Schedule shifts around peak hours |
| 4 | Unusual spike days exist | [Date] had [N] requests vs a typical [M] | Plan surge capacity; investigate causes such as weather or events |
| 5 | Resolution times are heavily skewed | Median [X] h vs mean [Y] h; P90 [Z] h | Track the median and the slowest 10% of cases, not just the average |
| 6 | Agency speed varies | [Agency A] median [X] h vs [Agency B] [Y] h | Share practices from faster agencies; review the slowest |
| 7 | A backlog of open requests exists | [X]% have no close date | Monitor open-case aging and set closure targets |

## 7. Recommendations
1. Focus resources on the top complaint types identified in insight 1.
2. Match staffing to peak hours and weekdays, with reserve capacity for spike days.
3. Review slow-resolution agencies and the longest open cases.
4. Report median and 90th-percentile resolution times alongside averages.
5. Fix data capture issues (placeholders, default midnight timestamps, invalid coordinates) at the source.

## 8. Limitations and next steps
- Sample of 50,000 rows, not the full history; seasonality needs a longer window.
- Resolution time depends on agencies recording close dates accurately.
- Next steps: add population per borough for per-capita comparison, forecast daily volume, and analyse complaint descriptors and ZIP-level hotspots.

## 9. Repository structure
```
├── README.md                  (this case study)
├── requirements.txt
├── run_all.sh                 (reproduces cleaning and analysis)
├── data/                      (raw and cleaned CSVs)
├── task1-data-cleaning/       (script, README, log)
├── task2-eda/                 (script, charts, insights)
├── task3-dashboard/           (HTML dashboard, Power BI guide and theme)
└── screenshots/
```

## 10. How to reproduce
```bash
pip install -r requirements.txt
bash run_all.sh
```
Then open `task3-dashboard/dashboard.html` and load `task1-data-cleaning/nyc311_cleaned.csv`.

## 11. Skills demonstrated
Data cleaning, data validation, exploratory analysis, anomaly detection, statistical thinking (skew, outliers, median vs mean), data visualisation, dashboard design (KPIs, filters, cross-filtering), business storytelling, documentation and reproducibility.

## Author
[Your name] | [LinkedIn URL] | Completed for @swynextechnologics
