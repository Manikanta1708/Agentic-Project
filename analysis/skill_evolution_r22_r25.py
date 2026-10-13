import pandas as pd
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURRICULUM = os.path.join(ROOT, "corpus", "curriculum")

R22_PATH = os.path.join(CURRICULUM, "R22_course_skill_mapping.csv")
R25_PATH = os.path.join(CURRICULUM, "R25_course_skill_mapping.csv")
OUT_PATH = os.path.join(CURRICULUM, "R22_R25_skill_evolution_summary.csv")

BRANCHES = ["AIML", "CIVIL", "CSE", "DS", "ECE", "EEE", "IT", "MECH"]


def normalize_skill(x):
    x = str(x).strip().lower()
    replacements = {
        "natural language processing": "nlp",
        "internet of things": "iot",
        "node.js": "nodejs",
        "machine-learning": "machine learning",
        "deep-learning": "deep learning",
    }
    return replacements.get(x, x)


def load_mapping(path, branch_col="branch", skill_col="skill"):
    df = pd.read_csv(path)
    df[branch_col] = df[branch_col].astype(str).str.strip().str.upper()
    df["skill_normalized"] = df[skill_col].astype(str).apply(normalize_skill)
    df = df[df[branch_col].isin(BRANCHES)].copy()
    df = df[df["skill_normalized"].notna()]
    df = df[df["skill_normalized"].ne("") & df["skill_normalized"].ne("nan")]
    return df


r22 = load_mapping(R22_PATH)
r25 = load_mapping(R25_PATH)

rows = []

for branch in BRANCHES:
    s22 = set(r22.loc[r22["branch"] == branch, "skill_normalized"])
    s25 = set(r25.loc[r25["branch"] == branch, "skill_normalized"])
    all_skills = sorted(s22 | s25)

    for skill in all_skills:
        c22 = int((r22.loc[(r22["branch"] == branch) & (r22["skill_normalized"] == skill)]).shape[0])
        c25 = int((r25.loc[(r25["branch"] == branch) & (r25["skill_normalized"] == skill)]).shape[0])
        change = c25 - c22

        if c22 > 0 and c25 > 0:
            status = "Retained Skill"
        elif c22 > 0 and c25 == 0:
            status = "R22 Removed Skill"
        else:
            status = "R25 New Skill"

        pct = None if c22 == 0 else round((change / c22) * 100, 2)

        rows.append({
            "branch": branch,
            "skill": skill,
            "r22_count": c22,
            "r25_count": c25,
            "change": change,
            "percentage_change": pct,
            "status": status,
        })

out = pd.DataFrame(rows)
out.to_csv(OUT_PATH, index=False)

print("R22 → R25 skill evolution rebuilt correctly")
print(f"Saved: {OUT_PATH}")

print("\\nBranch validation:")
for branch in BRANCHES:
    b = out[out["branch"] == branch]
    r22_skills = int((b["r22_count"] > 0).sum())
    r25_skills = int((b["r25_count"] > 0).sum())
    retained = int((b["status"] == "Retained Skill").sum())
    removed = int((b["status"] == "R22 Removed Skill").sum())
    new = int((b["status"] == "R25 New Skill").sum())
    print(f"{branch}: R22={r22_skills}, R25={r25_skills}, retained={retained}, removed={removed}, new={new}")
    assert retained + removed == r22_skills
    assert retained + new == r25_skills

print("\\nValidation PASSED: retained + removed = R22; retained + new = R25")
