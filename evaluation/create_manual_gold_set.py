import pandas as pd
from pathlib import Path

INPUT = Path("evaluation/gold_relevance.csv")
OUTPUT = Path("evaluation/manual_gold_review.csv")

df = pd.read_csv(INPUT)

print("Available columns:")
print(df.columns.tolist())

columns = [
    "branch",
    "skill",
    "r22_count",
    "r25_count",
    "change"
]

review = df[columns].copy()

review["expert_grade"] = ""
review["expert_comment"] = ""

review.to_csv(OUTPUT, index=False)

print("\n" + "=" * 60)
print("MANUAL GOLD SET CREATED")
print("=" * 60)
print(f"Records to review: {len(review)}")
print(f"Saved to: {OUTPUT}")

print("\nGrades:")
print("2 = Clearly relevant")
print("1 = Partially relevant")
print("0 = Not relevant")