import pandas as pd
import os
from scipy.stats import linregress

JOBS_FILE = "corpus/ai_jobs.csv"
SKILLS_FILE = "corpus/skills_demand.csv"
OUTPUT_FILE = "outputs/industry_trend_analysis.csv"

jobs = pd.read_csv(JOBS_FILE)[["job_id", "posted_year"]]
skills = pd.read_csv(SKILLS_FILE)[
    ["job_id", "skill", "skill_category", "skill_level"]
]

df = skills.merge(jobs, on="job_id", how="inner")

df["skill"] = df["skill"].astype(str).str.strip().str.lower()
df["posted_year"] = pd.to_numeric(df["posted_year"], errors="coerce")
df = df.dropna(subset=["skill", "posted_year"])

# Count unique jobs for each skill and year
trend = (
    df.groupby(["posted_year", "skill"])
      .agg(job_count=("job_id", "nunique"))
      .reset_index()
)

# Total jobs per year
total = (
    jobs.groupby("posted_year")["job_id"]
        .nunique()
        .reset_index(name="total_jobs")
)

trend = trend.merge(total, on="posted_year")
trend["demand_share"] = trend["job_count"] / trend["total_jobs"] * 100

results = []

for skill, group in trend.groupby("skill"):
    group = group.sort_values("posted_year")

    first = group.iloc[0]["job_count"]
    last = group.iloc[-1]["job_count"]

    percentage_change = (
        (last - first) / first * 100
        if first != 0 else 0
    )

    slope, _, _, _, _ = linregress(
        group["posted_year"],
        group["job_count"]
    )

    if percentage_change >= 5 and slope > 0:
        direction = "Increasing"
    elif percentage_change <= -5 and slope < 0:
        direction = "Decreasing"
    else:
        direction = "Stable"

    results.append({
        "skill": skill,
        "2020_demand": first,
        "2026_demand": last,
        "absolute_change": last - first,
        "percentage_change": round(percentage_change, 2),
        "trend_slope": round(slope, 4),
        "trend_direction": direction
    })

summary = pd.DataFrame(results)

# Add yearly demand information
trend = trend.merge(summary, on="skill", how="left")

os.makedirs("outputs", exist_ok=True)

trend.to_csv(OUTPUT_FILE, index=False)

print("\nIndustry trend analysis completed!")
print("Skills:", trend["skill"].nunique())
print("Years:", sorted(trend["posted_year"].unique()))
print("Saved to:", OUTPUT_FILE)

print("\nTrend Summary:")
print(
    summary.sort_values(
        "percentage_change",
        ascending=False
    ).to_string(index=False)
)