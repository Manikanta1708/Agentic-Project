import pandas as pd
import os

BASE = "corpus/curriculum"

evolution = pd.read_csv(
    os.path.join(BASE, "R22_R25_skill_evolution_summary.csv")
)

r25 = pd.read_csv(
    os.path.join(BASE, "R25_course_skill_mapping.csv")
)

emerging = evolution[evolution["status"] == "Emerging"].copy()

result = emerging.merge(
    r25[["branch", "course_title", "skill"]],
    on=["branch", "skill"],
    how="left"
)

result = result[
    ["branch", "skill", "r25_count", "course_title"]
].drop_duplicates()

output = os.path.join(
    BASE,
    "R25_emerging_skill_validation.csv"
)

result.to_csv(output, index=False)

print("Emerging skill validation created!")
print()
print(result.to_string(index=False))
print()
print("Total emerging skill records:", len(result))
print("Saved to:", output)