"""Exploratory data analysis on the cleaned NYC 311 dataset (Task 1 output).

Usage:
    python eda_nyc311.py path/to/nyc311_cleaned.csv
Requires: pandas, matplotlib
Outputs: charts/*.png, summary_statistics.csv, insights.md
"""
import os
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

path = sys.argv[1] if len(sys.argv) > 1 else "nyc311_cleaned.csv"
os.makedirs("charts", exist_ok=True)
plt.rcParams.update({"figure.figsize": (9, 5), "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True,
                     "grid.alpha": 0.3, "font.size": 10})

df = pd.read_csv(path, parse_dates=["created_date", "closed_date"], low_memory=False)
n = len(df)
print(f"Loaded {n} rows, {df.shape[1]} columns")


def save(name):
    plt.tight_layout()
    plt.savefig(f"charts/{name}.png", dpi=150)
    plt.close()


def pct(x):
    return f"{x * 100:.1f}%"


insights = []

# ---------- 1. Overview statistics ----------
df["hour"] = df["created_date"].dt.hour
df["weekday"] = df["created_date"].dt.day_name()
df["date"] = df["created_date"].dt.date
summary = df.describe(include="all")
summary.to_csv("summary_statistics.csv")
print("Date range:", df["created_date"].min(), "to", df["created_date"].max())

# ---------- 2. Top complaint types ----------
top = df["complaint_type"].value_counts()
t10 = top.head(10)
ax = t10.sort_values().plot.barh(color="#2b6cb0")
ax.set_title("Top 10 complaint types")
ax.set_xlabel("Number of requests")
save("01_top_complaint_types")
top3_share = top.head(3).sum() / n
insights.append(
    f"**Complaint types are {'highly concentrated' if top3_share > 0.5 else 'fairly spread out'}.** The top complaint type, '{top.index[0]}', "
    f"accounts for {pct(top.iloc[0] / n)} of all {n:,} requests, and the top 3 types "
    f"({', '.join(top.index[:3])}) together make up {pct(top3_share)}. "
    f"Out of {top.shape[0]} complaint types, "
    + ("a handful drive most of the workload, so focusing resources on them gives the biggest effect."
       if top3_share > 0.5 else "the workload is spread across many categories, so no single fix covers most requests."))

# ---------- 3. Borough ----------
b = df["borough"].value_counts()
ax = b.plot.bar(color="#38a169", rot=30)
ax.set_title("Requests by borough")
ax.set_ylabel("Number of requests")
save("02_requests_by_borough")
known = b.drop("UNKNOWN", errors="ignore")
mix = (df[df["borough"].isin(known.index)]
       .groupby("borough", observed=True)["complaint_type"]
       .agg(lambda s: s.value_counts().index[0]))
mix_txt = "; ".join(f"{k.title()}: {v}" for k, v in mix.items())
insights.append(
    f"**Request volume by borough.** "
    f"{known.index[0].title()} has the most requests ({pct(known.iloc[0] / n)} of the total) and "
    f"{known.index[-1].title()} the fewest ({pct(known.iloc[-1] / n)}). "
    f"The most common complaint per borough is: {mix_txt}. "
    f"Comparing these shows whether local problems differ from the citywide pattern.")

# ---------- 4. Hour of day ----------
h = df["hour"].value_counts().sort_index().reindex(range(24), fill_value=0)
ax = h.plot(marker="o", color="#dd6b20")
ax.set_title("Requests by hour of day (creation time)")
ax.set_xlabel("Hour (0-23)")
ax.set_ylabel("Number of requests")
ax.set_xticks(range(0, 24, 2))
save("03_requests_by_hour")
peak_h, low_h = int(h.idxmax()), int(h.idxmin())
midnight_share = h.loc[0] / n
txt = (f"**Requests follow a daily rhythm.** Volume peaks at {peak_h:02d}:00 "
       f"({pct(h.max() / n)} of requests) and is lowest at {low_h:02d}:00 ({pct(h.min() / n)}).")
if midnight_share > 1.5 / 24:
    txt += (f" Hour 00 holds {pct(midnight_share)} of requests, far above an even 4.2% share, "
            f"which usually means some agencies stamp a default midnight time rather than the true time, "
            f"so hourly analysis should treat midnight with caution.")
insights.append(txt)

# ---------- 5. Day of week ----------
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
w = df["weekday"].value_counts().reindex(order, fill_value=0)
ax = w.plot.bar(color="#805ad5", rot=30)
ax.set_title("Requests by day of week")
ax.set_ylabel("Number of requests")
save("04_requests_by_weekday")
wd_avg = w[order[:5]].mean()
we_avg = w[order[5:]].mean()
insights.append(
    f"**Weekdays are busier than weekends.** {w.idxmax()} is the busiest day ({w.max():,} requests) and "
    f"{w.idxmin()} the quietest ({w.min():,}). The average weekday has "
    f"{(wd_avg / we_avg - 1) * 100:.0f}% {'more' if wd_avg > we_avg else 'fewer'} requests than the average weekend day.")

# ---------- 6. Daily trend and spike anomalies ----------
daily = df.groupby("date").size()
daily.index = pd.to_datetime(daily.index)
daily = daily.sort_index()
spikes = pd.Series(dtype=float)
if len(daily) >= 14:
    med = daily.median()
    mad = (daily - med).abs().median() or 1
    score = 0.6745 * (daily - med) / mad
    spikes = daily[score > 3.5]
    ax = daily.plot(color="#2b6cb0", label="Daily requests")
    daily.rolling(7, min_periods=1).mean().plot(ax=ax, color="#e53e3e", label="7-day average")
    if len(spikes):
        ax.scatter(spikes.index, spikes.values, color="black", zorder=5, label="Anomalous spike")
    ax.set_title("Daily request volume")
    ax.set_ylabel("Number of requests")
    ax.legend()
    save("05_daily_trend")
    if len(spikes):
        d = spikes.idxmax()
        insights.append(
            f"**There are unusual spike days.** {len(spikes)} day(s) are statistical anomalies "
            f"(robust z-score above 3.5). The largest is {d.date()} with {spikes.max():,} requests, "
            f"versus a typical day of about {med:,.0f}. Spikes like this often follow weather events, "
            f"holidays or a single large issue and are worth investigating separately.")
    else:
        insights.append(
            f"**Daily volume is stable.** No day deviates strongly from the typical {med:,.0f} requests, "
            f"so there are no major anomalous spikes in this sample.")

# ---------- 7. Resolution time ----------
res = df["resolution_hours"].dropna() if "resolution_hours" in df.columns else pd.Series(dtype=float)
if len(res) > 0:
    q1, q3 = res.quantile([0.25, 0.75])
    upper = q3 + 1.5 * (q3 - q1)
    outliers = res[res > upper]
    fig, ax = plt.subplots()
    ax.hist(res[res > 0].clip(upper=res.quantile(0.99)), bins=60, color="#319795")
    ax.set_xscale("log") if (res > 0).any() else None
    ax.axvline(res.median(), color="red", linestyle="--", label=f"Median {res.median():.1f} h")
    ax.set_title("Resolution time distribution (hours, log scale, capped at 99th percentile)")
    ax.set_xlabel("Hours to close")
    ax.legend()
    save("06_resolution_distribution")

    ag = (df.dropna(subset=["resolution_hours"]).groupby("agency", observed=True)["resolution_hours"]
          .agg(["median", "count"]))
    ag = ag[ag["count"] >= 100].sort_values("median")
    if len(ag) >= 2:
        sel = pd.concat([ag.head(5), ag.tail(5)]).drop_duplicates()
        ax = sel["median"].plot.barh(color="#d69e2e")
        ax.set_title("Median resolution time by agency (hours, agencies with 100+ closed requests)")
        ax.set_xlabel("Median hours to close")
        save("07_resolution_by_agency")
        fast, slow = ag.index[0], ag.index[-1]
        agency_txt = (f" Among agencies with at least 100 closed requests, {fast} is fastest "
                      f"(median {ag['median'].iloc[0]:.1f} h) and {slow} is slowest "
                      f"(median {ag['median'].iloc[-1]:.1f} h).")
    else:
        agency_txt = ""
    insights.append(
        f"**Resolution times are heavily skewed.** The median request closes in {res.median():.1f} hours, "
        f"but the mean is {res.mean():.1f} hours and the 90th percentile is {res.quantile(0.9):.1f} hours, "
        f"so a minority of slow cases pull the average up. {len(outliers):,} requests "
        f"({pct(len(outliers) / len(res))}) are statistical outliers (above {upper:.1f} h), with a maximum of "
        f"{res.max():,.0f} hours.{agency_txt} The median is a better measure of typical service than the mean.")

# ---------- 8. Status / open requests ----------
if "status" in df.columns:
    st = df["status"].value_counts()
    ax = st.plot.bar(color="#718096", rot=30)
    ax.set_title("Request status")
    ax.set_ylabel("Number of requests")
    save("08_status")
    open_share = df["closed_date"].isna().mean()
    insights.append(
        f"**Status and open cases.** '{st.index[0]}' is the most common status ({pct(st.iloc[0] / n)}), "
        f"and {pct(open_share)} of requests have no closing date, meaning they are still open or were never "
        f"closed in the data. Open cases are a backlog indicator worth tracking.")

# ---------- 9. Correlation-style check: hour vs resolution ----------
if len(res) > 0:
    hr = df.dropna(subset=["resolution_hours"]).groupby("hour")["resolution_hours"].median()
    ax = hr.plot(marker="o", color="#c53030")
    ax.set_title("Median resolution time by creation hour")
    ax.set_xlabel("Hour created")
    ax.set_ylabel("Median hours to close")
    save("09_resolution_by_hour")

# ---------- Write insights ----------
with open("insights.md", "w") as f:
    f.write("# Key insights (auto-generated from the data)\n\n")
    f.write("Numbers below are computed directly from the cleaned dataset. "
            "Review them and add your own interpretation before submitting.\n\n")
    for i, text in enumerate(insights, 1):
        f.write(f"## Insight {i}\n{text}\n\n")
print(f"Done. {len(insights)} insights written to insights.md, charts in charts/")
