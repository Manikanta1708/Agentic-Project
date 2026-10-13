"""
=========================================================
Knowledge Graph Schema
Agentic Curriculum Intelligence Framework
=========================================================
"""

# =========================================================
# Node Types
# =========================================================

NODE_TYPES = {

    "BRANCH": "Branch",

    "SKILL": "Skill",

    "INDUSTRY": "Industry",

    "RESEARCH": "Research",

    "RECOMMENDATION": "Recommendation"

}

# =========================================================
# Relationship Types
# =========================================================

EDGE_TYPES = {

    "HAS_SKILL": "HAS_SKILL",

    "JOB_DEMAND": "JOB_DEMAND",

    "RESEARCH_TREND": "RESEARCH_TREND",

    "MISSING_SKILL": "MISSING_SKILL",

    "RECOMMENDED_SKILL": "RECOMMENDED_SKILL",

    "RELATED_SKILL": "RELATED_SKILL"

}
# =========================================================
# Print Schema
# =========================================================

if __name__ == "__main__":

    print("\n========== NODE TYPES ==========\n")

    for node in NODE_TYPES.values():
        print(node)

    print("\n========== EDGE TYPES ==========\n")

    for edge in EDGE_TYPES.values():
        print(edge)