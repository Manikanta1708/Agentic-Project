import pandas as pd
import os

BASE = "corpus/curriculum"

branch_files = {
    "AIML": "R25_AIML_syllabus.csv",
    "CIVIL": "R25_CIVIL_syllabus.csv",
    "CSE": "R25_CSE_syllabus.csv",
    "DS": "R25_AIDS_syllabus.csv",
    "ECE": "R25_ECE_syllabus.csv",
    "EEE": "R25_EEE_syllabus.csv",
    "IT": "R25_CSIT_syllabus.csv",
    "MECH": "R25_ME_syllabus.csv"
}

rows = []

for branch, filename in branch_files.items():

    path = os.path.join(BASE, branch, filename)

    if not os.path.exists(path):
        print(f"File not found: {path}")
        continue

    df = pd.read_csv(path)

    for _, r in df.iterrows():
        rows.append({
            "branch": branch,
            "year_semester": r["year_semester"],
            "course_code": r["course_code"],
            "course_title": r["course_title"],
            "skill": ""
        })

result = pd.DataFrame(rows)

output_path = os.path.join(BASE, "R25_course_skill_mapping.csv")

result.to_csv(output_path, index=False)

print("R25 skill mapping created successfully!")
print("Total courses:", len(result))
print("Saved to:", output_path)