import pandas as pd
import os
import re
from difflib import SequenceMatcher

BASE = "corpus/curriculum"

r22 = pd.read_csv(
    os.path.join(BASE, "R22_course_skill_mapping.csv")
)

r25 = pd.read_csv(
    os.path.join(BASE, "R25_course_skill_mapping.csv")
)


def normalize(text):
    text = str(text).lower()

    text = text.replace("laboratory", "lab")

    # Remove curriculum labels/prefixes
    text = re.sub(r"dept\.?\s*core", " ", text)
    text = re.sub(r"\*mc", " ", text)

    # Normalize common separators
    text = text.replace("&", " and ")
    text = text.replace("/", " ")
    text = text.replace("-", " ")

    text = re.sub(r"[^a-z0-9 ]", " ", text)

    return " ".join(text.split())


def similarity(a, b):
    return SequenceMatcher(
        None,
        normalize(a),
        normalize(b)
    ).ratio()


# Explicit mapping for clearly identifiable R25 skills
new_skill_map = {
    "reinforcement learning": "reinforcement learning",
    "generative ai": "generative ai",
    "generative ai lab": "generative ai",
    "big data technologies": "big data",
    "big data spark": "big data",
    "ui design flutter android studio": "mobile app development",
    "data visualization r programming power bi": "data visualization",
    "data analytics and visualization": "data analytics",
    "building information modelling lab": "civil engineering software",
    "gis lab": "geomatics",
    "computational lab iot lab": "internet of things",
    "vlsi design verification lab": "vlsi",
    "45g practical lab robotic lab drone lab": "robotics",
    "smart metering and communication protocols": "smart grid",
    "ev charging infrastructure": "ev charging",
    "robotics and automation lab": "robotics",
    "data analytics and python for engineers": "data analytics",
    "modelling and simulation tools": "simulation",
    "troubleshooting of mechanical systems": "mechanical engineering",
        "electronic devices and circuits": "electronic circuits",
    "algorithms design and analysis": "algorithms",
    "algorithm design and analysis": "algorithms",
    "discrete mathematics": "discrete mathematics",
    "automata theory and compiler design": "compiler design",
    "advanced data structures using python lab": "data structures",
    "mathematical and statistical foundations": "statistics",
    "programming for problem solving lab": "programming languages",
    "data structures": "data structures",
    "data structures lab": "data structures",
    "linux and shell scripting": "scripting",
    "numerical methods and complex variables": "mathematics",
    "risc and microcontroller architectures": "microcontrollers",
    "risc and microcontroller interfacing lab": "microcontrollers",
    "vlsi design verification laboratory": "vlsi",
    "applied physics": "electronics",
    "applied physics laboratory": "electronics",
    "electrical measurements and sensors": "sensors",
    "smart metering and communication protocols": "smart grid",
    "ev charging infrastructure": "ev charging",
    "material science and metallurgy": "material science",
    "data analytics and python for engineers": "data analytics",
    "kinematics and dynamics lab": "kinematics",
}


# Generic/common course mappings
generic_map = {
    "matrices and calculus": "mathematics",
    "ordinary differential equations and vector calculus": "mathematics",
    "computational mathematics lab": "mathematics",
    "probability and statistics": "probability",
    "probability statistics and complex variables": "probability",
    "engineering mechanics for civil engineers": "engineering mechanics",
    "advanced engineering physics": "electronics",
    "advanced engineering physics lab": "electronics",
    "basic electrical engineering": "electrical engineering",
    "basic electrical engineering lab": "electrical engineering",
    "engineering chemistry": "material science",
    "engineering chemistry lab": "material science",
    "chemistry lab for engineers": "material science",
    "applied chemistry": "material science",
    "engineering workshop": "workshop practice",
    "engineering drawing and computer aided drafting": "cad",
    "environmental science": "environmental engineering",
    "project work": "capstone project",
    "work": "capstone project",
}
skill_normalization = {
    "nodejs": "node.js",
    "nlp": "natural language processing",
}


# Group R22 courses by branch
r22_courses = {}

for branch, group in r22.groupby("branch"):
    r22_courses[branch] = group


rows = []


for _, row in r25.iterrows():

    branch = row["branch"]
    course = str(row["course_title"])

    best_course = ""
    best_skill = ""
    best_score = 0

    # Compare R25 course with R22 courses
    # only within the same branch
    if branch in r22_courses:

        for _, old in r22_courses[branch].iterrows():

            score = similarity(
                course,
                old["course_name"]
            )

            if score > best_score:
                best_score = score
                best_course = old["course_name"]
                best_skill = old["skill"]

    key = normalize(course)

    # 1. Explicit R25 skill mapping
    if key in new_skill_map:

        assigned_skill = new_skill_map[key]
        best_score = 1.0

    # 2. Generic/common course mapping
    elif key in generic_map:

        assigned_skill = generic_map[key]

    # 3. Strong R22 course similarity
    elif best_score >= 0.65:

        assigned_skill = best_skill

    # 4. Leave uncertain courses unmapped
    else:

        assigned_skill = ""


    rows.append({
        "branch": branch,
        "year_semester": row["year_semester"],
        "course_code": row["course_code"],
        "course_title": course,
        "skill": assigned_skill,
        "match_score": round(best_score, 3)
    })
    # Normalize equivalent skill names
for row in rows:
    if row["skill"] in skill_normalization:
        row["skill"] = skill_normalization[row["skill"]]


result = pd.DataFrame(rows)


output = os.path.join(
    BASE,
    "R25_course_skill_mapping.csv"
)

result.to_csv(
    output,
    index=False
)


print("R25 skill mapping completed!")
print("Total courses:", len(result))
print("Skills assigned:", result["skill"].ne("").sum())
print("Skills remaining:", result["skill"].eq("").sum())
print("Saved to:", output)