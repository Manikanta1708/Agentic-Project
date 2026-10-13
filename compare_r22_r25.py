import pandas as pd
import os
import re

BASE = "corpus/curriculum"

r22 = pd.read_csv(os.path.join(BASE, "R22_course_skill_mapping.csv"))
r25 = pd.read_csv(os.path.join(BASE, "R25_course_skill_mapping.csv"))

def normalize(text):
    text = str(text).lower()
    text = text.replace("laboratory", "lab")
    text = text.replace("object oriented", "object-oriented")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())

r22["normalized_course"] = r22["course_name"].apply(normalize)
r25["normalized_course"] = r25["course_title"].apply(normalize)

rows = []

for branch in r22["branch"].unique():

    old = set(r22[r22["branch"] == branch]["normalized_course"])
    new = set(r25[r25["branch"] == branch]["normalized_course"])

    rows.append({
        "branch": branch,
        "r22_courses": len(old),
        "r25_courses": len(new),
        "courses_retained": len(old & new),
        "courses_removed": len(old - new),
        "courses_added": len(new - old)
    })

result = pd.DataFrame(rows)

output = os.path.join(BASE, "R22_R25_comparison.csv")
result.to_csv(output, index=False)

print("Improved R22 vs R25 comparison created!")
print(result.to_string(index=False))
print("Saved to:", output)