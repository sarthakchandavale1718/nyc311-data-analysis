# NYC 311 Service Requests: Exploratory Data Analysis (Task 2)

## Objective
Explore the cleaned NYC 311 dataset from Task 1 (`nyc311-data-cleaning`), calculate key statistics, and find trends, patterns and anomalies, supported by charts and written insights.

## Files
| File | Purpose |
|---|---|
| `eda_nyc311.py` | Python (pandas + matplotlib) analysis script |
| `nyc311_cleaned.csv` | Input: cleaned dataset from Task 1 |
| `summary_statistics.csv` | Descriptive statistics for every column |
| `charts/` | Nine PNG charts |
| `insights.md` | Key insights with computed numbers |

Run: `pip install pandas matplotlib` then `python eda_nyc311.py nyc311_cleaned.csv`

## What was analysed
1. Descriptive statistics for all columns (counts, unique values, mean, median, min, max)
2. Most common complaint types
3. Request volume by borough and the top complaint in each borough
4. Time patterns: by hour of day and day of week
5. Daily trend with a 7-day average and anomaly (spike) detection using a robust z-score
6. Resolution time: distribution, skew, outliers (IQR rule) and comparison across agencies
7. Request status and share of open cases

## Charts
| Chart | Shows |
|---|---|
| `01_top_complaint_types` | Ten most common complaints |
| `02_requests_by_borough` | Volume per borough |
| `03_requests_by_hour` | Daily rhythm |
| `04_requests_by_weekday` | Weekday vs weekend |
| `05_daily_trend` | Daily volume, 7-day average, spikes |
| `06_resolution_distribution` | How long requests take to close |
| `07_resolution_by_agency` | Fastest and slowest agencies |
| `08_status` | Status breakdown |
| `09_resolution_by_hour` | Resolution time by creation hour |

## Key insights
See `insights.md` for the full list with exact figures. In summary:
1. Complaints are concentrated in a few types
2. Volume and the leading complaint vary by borough
3. Requests follow a clear daily rhythm (and midnight timestamps may be a data artifact)
4. Weekdays are busier than weekends
5. A small number of days show anomalous spikes
6. Resolution times are heavily skewed, so the median is more representative than the mean
7. A share of requests remain open, indicating backlog

## Methods and assumptions
- Median is preferred over mean for resolution time because of strong right skew.
- Outliers use the IQR rule (above Q3 + 1.5 x IQR); daily spikes use a robust z-score (median and MAD) above 3.5.
- Agencies are compared only if they have at least 100 closed requests.
- Results describe a 50,000-row sample, not the full 311 history, so patterns may not generalise to all years.
