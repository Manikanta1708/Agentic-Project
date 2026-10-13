import pandas as pd
import os

BASE = "corpus/curriculum"

r22 = pd.read_csv(os.path.join(BASE, "R22_course_skill_mapping.csv"))
r25 = pd.read_csv(os.path.join(BASE, "R25_course_skill_mapping.csv"))

r22 = r22[r22["skill"].notna() & (r22["skill"].astype(str).str.strip() != "")]
r25 = r25[r25["skill"].notna() & (r25["skill"].astype(str).str.strip() != "")]

r22["skill"] = r22["skill"].astype(str).str.lower().str.strip()
r25["skill"] = r25["skill"].astype(str).str.lower().str.strip()

old = (
    r22.groupby(["branch", "skill"])
    .size()
    .reset_index(name="r22_count")
)

new = (
    r25.groupby(["branch", "skill"])
    .size()
    .reset_index(name="r25_count")
)

result = pd.merge(
    old,
    new,
    on=["branch", "skill"],
    how="outer"
).fillna(0)

result["r22_count"] = result["r22_count"].astype(int)
result["r25_count"] = result["r25_count"].astype(int)

result["change"] = result["r25_count"] - result["r22_count"]

result["percentage_change"] = (
    result["change"] / result["r22_count"].replace(0, float("nan")) * 100
).round(2)

def status(row):
    if row["r22_count"] == 0:
        return "Emerging"
    if row["r25_count"] == 0:
        return "Removed"
    if row["change"] > 0:
        return "Expanded"
    if row["change"] < 0:
        return "Reduced"
    return "Retained"

result["status"] = result.apply(status, axis=1)

result = result.sort_values(
    ["branch", "r25_count"],
    ascending=[True, False]
)

output = os.path.join(
    BASE,
    "R22_R25_skill_evolution_summary.csv"
)

result.to_csv(output, index=False)

print("R22 → R25 skill evolution summary created!")
print()
print(result.head(30).to_string(index=False))
print()
print("Total records:", len(result))
print("Saved to:", output)