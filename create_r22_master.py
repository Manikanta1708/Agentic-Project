import pandas as pd
import os

BASE = "corpus/curriculum"

branches = ["AIML", "CIVIL", "CSE", "DS", "ECE", "EEE", "IT", "MECH"]

all_data = []

for branch in branches:
    path = os.path.join(BASE, branch, "course_skill_mapping.csv")

    df = pd.read_csv(path)
    df["branch"] = branch

    all_data.append(df)

result = pd.concat(all_data, ignore_index=True)

result = result[["branch", "course_name", "skill"]]

output = os.path.join(BASE, "R22_course_skill_mapping.csv")

result.to_csv(output, index=False)

print("R22 master mapping created successfully!")
print("Total mappings:", len(result))
print("Branches:", result["branch"].nunique())
print("Unique courses:", result["course_name"].nunique())
print("Unique skills:", result["skill"].nunique())
print("Saved to:", output)