# NYC 311 Service Requests: Data Cleaning

## Dataset
NYC Open Data, "311 Service Requests from 2010 to Present". This project cleans a 50,000-row sample pulled directly from the public API:
https://data.cityofnewyork.us/resource/erm2-nwe9.csv?$limit=50000

Source page: https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9

## Files
| File | Purpose |
|---|---|
| `nyc311_raw.csv` | Untouched downloaded sample |
| `clean_nyc311.py` | Python (pandas) cleaning script |
| `nyc311_cleaned.csv` | Cleaned output |
| `cleaning_log.txt` | Exact counts of every problem found and fixed |

Run: `pip install pandas` then `python clean_nyc311.py`
(The API returns rows in no fixed order, so counts may differ slightly between runs. Use the supplied `nyc311_raw.csv` with `python clean_nyc311.py nyc311_raw.csv` to reproduce my numbers exactly.)

## Issues found and how they were fixed
| Problem type | Example in this data | Fix |
|---|---|---|
| Missing values | Many columns mostly empty (bridge/highway, taxi, vehicle fields); `closed_date`, `incident_zip`, coordinates partly missing | Dropped columns over 90% empty; filled borough/city/location_type with "Unknown"; left zip, coordinates and `closed_date` missing because open requests legitimately have no close date and guessing locations would invent data |
| Placeholder values | "Unspecified", "N/A", blank strings stored as real text | Converted to true missing values, then handled as above |
| Duplicate records | Repeated rows or repeated `unique_key` | Removed (count in log) |
| Incorrect data types | Every column loads as text; dates are strings | Dates to datetime, coordinates to float, `unique_key` to integer, low-cardinality columns to category |
| Inconsistent values | Same category in different case or spacing (e.g. "Noise - Residential" vs "NOISE - RESIDENTIAL "), mixed-case borough/city | Trimmed and collapsed whitespace, mapped variants to the most common spelling, upper-cased borough and city |
| Invalid values | ZIP codes like "11201-1234" or letters; coordinates of 0,0 or outside NYC; `closed_date` before `created_date` | ZIP reduced to 5 digits or set missing; bad coordinates and impossible close dates set to missing |
| New helper column | none | `resolution_hours` = closed minus created, ready for analysis |

## Assumptions
- NYC bounding box used for coordinate checks: latitude 40.4 to 41.0, longitude -74.3 to -73.6.
- Text variants are merged by lowercase match, so genuinely different categories are never merged.
