"""Clean a sample of the public NYC 311 Service Requests dataset.

Usage:
    python clean_nyc311.py                  # downloads 50,000 raw rows
    python clean_nyc311.py path/to/raw.csv  # uses a local copy
Requires: pandas
"""
import re
import sys
import pandas as pd

RAW_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.csv?$limit=50000"
log = []


def note(msg):
    print(msg)
    log.append(msg)


def has(col):
    return col in df.columns


def unify_case(series):
    """Map spelling variants (case/whitespace) to the most frequent spelling."""
    s = series.astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    key = s.str.lower()
    best = s.groupby(key).agg(lambda x: x.value_counts().index[0])
    changed = (s.notna() & (s != key.map(best))).sum()
    return key.map(best), int(changed)


src = sys.argv[1] if len(sys.argv) > 1 else RAW_URL
df = pd.read_csv(src, dtype=str, low_memory=False)
df.to_csv("nyc311_raw.csv", index=False)
note(f"Loaded raw data: {df.shape[0]} rows, {df.shape[1]} columns")

# 1. Column names
df.columns = [re.sub(r"\W+", "_", c.strip().lower()).strip("_") for c in df.columns]

# 2. Profile before cleaning
miss = (df.isna().mean() * 100).round(1)
note("Percent missing per column BEFORE cleaning:\n" + miss.sort_values(ascending=False).to_string())
note(f"Exact duplicate rows: {df.duplicated().sum()}")
if has("unique_key"):
    note(f"Duplicate unique_key values: {df['unique_key'].duplicated().sum()}")

# 3. Duplicates
n = len(df)
df = df.drop_duplicates()
if has("unique_key"):
    df = df.drop_duplicates(subset="unique_key")
note(f"Removed {n - len(df)} duplicate rows")

# 4. Drop columns that are almost entirely empty
sparse = [c for c in df.columns if df[c].isna().mean() > 0.90]
df = df.drop(columns=sparse)
note(f"Dropped {len(sparse)} columns with more than 90% missing: {sparse}")

# 5. Placeholder text -> real missing values
placeholders = {"unspecified", "unknown", "n/a", "na", "none", "null", "", "-"}
text_cols = df.columns  # everything was read as text
fixed = 0
for c in text_cols:
    s = df[c].str.strip()
    mask = s.str.lower().isin(placeholders)
    fixed += int(mask.sum())
    df[c] = s.mask(mask)
note(f"Converted {fixed} placeholder values (Unspecified, N/A, blanks...) to missing")

# 6. Inconsistent spelling/case in categorical columns
for c in ["agency", "agency_name", "complaint_type", "descriptor", "location_type",
          "borough", "city", "status", "street_name", "community_board"]:
    if has(c):
        df[c], changed = unify_case(df[c])
        note(f"{c}: unified {changed} inconsistent spellings")
if has("borough"):
    df["borough"] = df["borough"].str.upper()
if has("city"):
    df["city"] = df["city"].str.upper()

# 7. Data types
for c in ["created_date", "closed_date", "due_date", "resolution_action_updated_date"]:
    if has(c):
        df[c] = pd.to_datetime(df[c], errors="coerce")
for c in ["latitude", "longitude"]:
    if has(c):
        df[c] = pd.to_numeric(df[c], errors="coerce")
if has("unique_key"):
    df["unique_key"] = pd.to_numeric(df["unique_key"], errors="coerce").astype("int64")
note("Parsed date columns to datetime, coordinates to float, unique_key to int")

# 8. Invalid values
if has("incident_zip"):
    z = df["incident_zip"].str.extract(r"^(\d{5})")[0]
    bad = (df["incident_zip"].notna() & z.isna()).sum()
    df["incident_zip"] = z
    note(f"incident_zip: standardised to 5 digits, {bad} invalid values set to missing")
if has("latitude") and has("longitude"):
    out = ~(df["latitude"].between(40.4, 41.0) & df["longitude"].between(-74.3, -73.6))
    out &= df["latitude"].notna() | df["longitude"].notna()
    df.loc[out, ["latitude", "longitude"]] = pd.NA
    note(f"Set {int(out.sum())} coordinates outside the NYC bounding box to missing")
if has("created_date") and has("closed_date"):
    bad = df["closed_date"] < df["created_date"]
    df.loc[bad, "closed_date"] = pd.NaT
    note(f"Set {int(bad.sum())} closed_date values earlier than created_date to missing")
    df["resolution_hours"] = (df["closed_date"] - df["created_date"]).dt.total_seconds() / 3600

# 9. Remaining missing values
for c in ["borough", "city", "location_type"]:
    if has(c):
        df[c] = df[c].fillna("UNKNOWN" if c != "location_type" else "Unknown")
note("Filled missing borough/city/location_type with 'Unknown'. Coordinates, zip and "
     "closed_date are left missing on purpose (open requests have no closed_date; "
     "guessing locations would add false data)")

# 10. Compact categorical types
for c in ["agency", "borough", "status", "complaint_type"]:
    if has(c):
        df[c] = df[c].astype("category")

miss_after = (df.isna().mean() * 100).round(1)
note("Percent missing per column AFTER cleaning:\n" + miss_after.sort_values(ascending=False).to_string())
df.to_csv("nyc311_cleaned.csv", index=False)
note(f"Saved nyc311_cleaned.csv: {df.shape[0]} rows, {df.shape[1]} columns")
with open("cleaning_log.txt", "w") as f:
    f.write("\n\n".join(log))
