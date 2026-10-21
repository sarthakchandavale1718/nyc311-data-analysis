# NYC 311 Service Requests: Interactive Dashboard (Task 3)

## Objective
Turn the analysis from Task 2 into an interactive dashboard that communicates the main findings at a glance.

## How to use
1. Open `dashboard.html` in any modern browser (internet needed once to load the chart libraries).
2. Click **Load nyc311_cleaned.csv** and select the cleaned file from Task 1. Data is processed locally in your browser and never uploaded.
3. Use the filters or click bars in the charts to explore. **Reset filters** clears everything.
4. **Use sample data** shows a synthetic preview (clearly labelled) if you only want to see the layout.

Required columns: `created_date`, `closed_date`, `agency`, `complaint_type`, `borough`, `status`, `resolution_hours`.

## Dashboard contents
| Section | Details |
|---|---|
| KPIs | Total requests, median resolution hours, % closed, still open, top complaint, peak hour |
| Filters | Borough, agency, complaint type, status, date range; click-to-filter on charts |
| Key findings | Auto-written insights that update with every filter |
| Charts | Top 10 complaints, borough volume, hourly pattern, day of week, daily trend with 7-day average, median resolution by agency, status split |

## Design choices
- Median (not mean) is used for resolution time because of strong right skew.
- Agencies appear in the resolution chart only with 20+ closed requests.
- Light and dark mode follow the system setting.

## Tools
HTML, CSS, JavaScript, Chart.js, PapaParse
