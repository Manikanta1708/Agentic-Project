import pandas as pd
import os
import re

BASE = "corpus/curriculum"

R22_FILE = os.path.join(BASE, "R22_course_skill_mapping.csv")
R25_FILE = os.path.join(BASE, "R25_course_skill_mapping.csv")

OUTPUT_FILE = os.path.join(
    BASE, "R22_R25_skill_evolution_summary.csv"
)


# --------------------------------------------------
# Load datasets
# --------------------------------------------------

r22 = pd.read_csv(R22_FILE)
r25 = pd.read_csv(R25_FILE)


# --------------------------------------------------
# Normalize skill names
# --------------------------------------------------

def normalize_skill(skill):

    skill = str(skill).lower().strip()

    skill = re.sub(
        r"[^a-z0-9. ]",
        " ",
        skill
    )

    skill = " ".join(skill.split())

    skill_map = {
        "nodejs": "node.js",
        "node js": "node.js",

        "nlp": "nlp",
        "natural language processing": "nlp",

        "ev charging infrastructure":
            "ev charging",

        "electric vehicle":
            "electric vehicles",

        "electric vehicle technology":
            "electric vehicles",
    }

    return skill_map.get(
        skill,
        skill
    )


r22["skill"] = (
    r22["skill"]
    .fillna("")
    .apply(normalize_skill)
)

r25["skill"] = (
    r25["skill"]
    .fillna("")
    .apply(normalize_skill)
)


# --------------------------------------------------
# Remove empty skills
# --------------------------------------------------

r22 = r22[r22["skill"] != ""]
r25 = r25[r25["skill"] != ""]


# --------------------------------------------------
# Foundational/common skills
# --------------------------------------------------

common_skills = {
    "mathematics",
    "probability",
    "statistics",
    "material science",
    "electronics",
    "electronic circuits",
    "electrical engineering",
    "environmental engineering",
    "cad",
    "workshop practice",
    "engineering mechanics",
    "computer architecture",
    "computer organization",
    "programming languages",
    "data structures",
    "algorithms",
    "software engineering",
    "computer networks",
    "operating systems",
    "database management",
    "discrete mathematics",
    "data analytics",
    "robotics",
    "scripting",
    "sensors",
    "simulation",
}


# --------------------------------------------------
# Branch-wise skill evolution
# --------------------------------------------------

rows = []

branches = sorted(
    set(r22["branch"].unique()) |
    set(r25["branch"].unique())
)


for branch in branches:

    old = r22[
        r22["branch"] == branch
    ]

    new = r25[
        r25["branch"] == branch
    ]

    old_counts = (
        old["skill"]
        .value_counts()
        .to_dict()
    )

    new_counts = (
        new["skill"]
        .value_counts()
        .to_dict()
    )

    skills = sorted(
        set(old_counts) |
        set(new_counts)
    )


    for skill in skills:

        r22_count = old_counts.get(
            skill,
            0
        )

        r25_count = new_counts.get(
            skill,
            0
        )

        change = r25_count - r22_count


        # --------------------------------------------------
        # Determine status
        # --------------------------------------------------

        if r22_count > 0 and r25_count > 0:

            status = "retained"

        elif r22_count > 0 and r25_count == 0:

            status = "removed"

        elif r22_count == 0 and r25_count > 0:

            if skill in common_skills:

                status = "retained"

            else:

                status = "new"

        else:

            continue


        # --------------------------------------------------
        # Percentage change
        # --------------------------------------------------

        if r22_count > 0:

            percentage_change = round(
                (change / r22_count) * 100,
                2
            )

        else:

            percentage_change = None


        rows.append({
            "branch": branch,
            "skill": skill,
            "r22_count": r22_count,
            "r25_count": r25_count,
            "change": change,
            "percentage_change": percentage_change,
            "status": status
        })


# --------------------------------------------------
# Create dataframe
# --------------------------------------------------

result = pd.DataFrame(rows)


# --------------------------------------------------
# Sort
# --------------------------------------------------

status_order = {
    "new": 0,
    "retained": 1,
    "removed": 2
}

result["_order"] = result["status"].map(
    status_order
)

result = result.sort_values(
    ["branch", "_order", "skill"]
)

result = result.drop(
    columns=["_order"]
)


# --------------------------------------------------
# Save
# --------------------------------------------------

result.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# Summary
# --------------------------------------------------

summary = (
    result
    .groupby(
        ["branch", "status"]
    )
    .size()
    .unstack(fill_value=0)
    .reset_index()
)


print()
print("==========================================")
print("R22 vs R25 Skill Evolution Completed!")
print("==========================================")
print()

print(summary.to_string(index=False))

print()
print(
    "Total skill records:",
    len(result)
)

print(
    "Unique skills:",
    result["skill"].nunique()
)

print()
print(
    "Saved to:",
    OUTPUT_FILE
)
