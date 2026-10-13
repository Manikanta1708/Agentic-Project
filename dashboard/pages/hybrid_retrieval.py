

import streamlit as st

import pandas as pd



from retrieval.hybrid_retriever import hybrid_retrieve





# ==========================================================

# PAGE CONFIG

# ==========================================================



st.set_page_config(

    page_title="Hybrid Retrieval",

    page_icon="🔍",

    layout="wide"

)





# ==========================================================

# HEADER

# ==========================================================



st.title("🔍 Hybrid Retrieval")



st.caption(

    "Combines semantic retrieval with knowledge-graph evidence "

    "for curriculum analysis."

)



st.divider()





# ==========================================================

# ACADEMIC BRANCH SELECTION

# ==========================================================



branches = [

    "AIML",

    "CSE",

    "DS",

    "IT",

    "ECE",

    "EEE",

    "MECH",

    "CIVIL"

]



branch = st.selectbox(

    "Academic Branch",

    branches

)



# Keep the existing retrieval configuration unchanged.

year = 1

semester = 1





# ==========================================================

# RETRIEVAL PIPELINE

# ==========================================================



st.info(

    "Hybrid Retrieval integrates semantic curriculum evidence "

    "with Knowledge Graph relationships to identify relevant "

    "skills, curriculum gaps and graph-based recommendations."

)





# ==========================================================

# SESSION STATE

# ==========================================================



if "hybrid_result" not in st.session_state:

    st.session_state.hybrid_result = None





# ==========================================================

# RUN RETRIEVAL

# ==========================================================



if st.button(

    "Run Hybrid Retrieval",

    width="stretch"

):



    # Clear previous results before starting a new retrieval.

    st.session_state.hybrid_result = None



    with st.spinner(f"Retrieving evidence for {branch}..."):

        try:

            result = hybrid_retrieve(

                branch,

                year,

                semester

            )



            # Verify that the result identifies the requested branch.

            result_branch = str(

                result.get("branch", "")

            ).strip().upper()



            if result_branch != branch.strip().upper():

                st.error(

                    "The retrieval result does not match the "

                    "selected branch. Please check the retrieval "

                    "function's branch filtering."

                )

            else:

                st.session_state.hybrid_result = result



        except Exception as e:

            st.session_state.hybrid_result = None

            st.error(f"Hybrid Retrieval failed: {e}")





# ==========================================================

# SHOW RESULTS ONLY FOR THE CURRENT BRANCH

# ==========================================================



result = st.session_state.hybrid_result



if (

    result is None

    or str(result.get("branch", "")).strip().upper()

    != branch.strip().upper()

):

    st.info(

        "Select a branch and click "

        "\*\*Run Hybrid Retrieval\*\* to view results for that branch."

    )

    st.stop()





st.success(

    f"Hybrid retrieval completed successfully for {branch}."

)





# ==========================================================

# EXTRACT RESULTS

# ==========================================================



vector_results = result.get("vector_results", [])



graph_results = result.get("graph_results", {})



missing = graph_results.get("missing_skills", [])



recommended = graph_results.get("recommended_skills", [])





# ==========================================================

# SUMMARY

# ==========================================================



st.divider()

st.subheader("Retrieval Summary")



c1, c2, c3 = st.columns(3)



with c1:

    st.metric("Vector Results", len(vector_results))



with c2:

    st.metric("Missing Skills", len(missing))



with c3:

    st.metric("Recommended Skills", len(recommended))





# ==========================================================

# VECTOR RETRIEVAL

# ==========================================================



st.divider()

st.subheader("📄 Vector Retrieval")



st.caption(

    "Curriculum evidence retrieved using semantic similarity."

)



if not vector_results:

    st.warning("No vector retrieval results found.")



else:

    try:

        vector_df = pd.DataFrame(vector_results)



        hidden_columns = [

    "embedding",

    "vector",

    "metadata",

    "industry_demand",

    "industry_count",

    "research_count",

    "research_demand",

    "job_count",

    "priority_score",

    "r29_priority_score"

]



        vector_df = vector_df.drop(

            columns=[

                col for col in hidden_columns

                if col in vector_df.columns

            ],

            errors="ignore"

        )



        # Display distance as a numeric value.

        if "distance" in vector_df.columns:

            vector_df["distance"] = pd.to_numeric(

                vector_df["distance"],

                errors="coerce"

            ).round(4)



        # Display only results belonging to the selected branch

        # when branch labels are available.

        if "branch" in vector_df.columns:

            vector_df["branch"] = (

                vector_df["branch"]

                .astype(str)

                .str.strip()

                .str.upper()

            )



            vector_df = vector_df[

                vector_df["branch"] == branch.strip().upper()

            ]



        if vector_df.empty:

            st.warning(

                "No vector results belong to the selected branch. "

                "Check the branch filter in the vector search module."

            )

        else:

            preferred_columns = [

                "branch",

                "year_semester",

                "course_code",

                "course_title",

                "course_name",

                "skill",

                "distance",

                "score"

            ]



            available_columns = [

                col for col in preferred_columns

                if col in vector_df.columns

            ]



            remaining_columns = [

                col for col in vector_df.columns

                if col not in available_columns

            ]



            vector_df = vector_df[

                available_columns + remaining_columns

            ]



            st.dataframe(

                vector_df,

                width="stretch",

                hide_index=True

            )



    except Exception as e:

        st.warning(f"Unable to format vector results: {e}")

        st.write(vector_results)





# ==========================================================

# KNOWLEDGE GRAPH RESULTS

# ==========================================================



st.divider()

st.subheader("🕸️ Knowledge Graph Evidence")



st.caption(

    "Graph relationships are used to identify curriculum "

    "skill gaps and graph-supported recommendations."

)



tab1, tab2 = st.tabs(

    ["Missing Skills", "Recommended Skills"]

)





# ==========================================================

# MISSING SKILLS

# ==========================================================



with tab1:

    if not missing:

        st.success(

            "No missing skills identified for the selected branch."

        )

    else:

        try:

            missing_df = pd.DataFrame(missing)



            # Remove only the requested display columns.

            missing_df = missing_df.drop(

                columns=[

                    "industry_demand",

                    "industry_count",

                    "research_count",

                    "research_demand",
                    "job_count",
                    "priority_score"

                ],

                errors="ignore"

            )



            st.dataframe(

                missing_df,

                width="stretch",

                hide_index=True

            )



        except Exception:

            st.write(missing)





# ==========================================================

# RECOMMENDED SKILLS

# ==========================================================



with tab2:

    if not recommended:

        st.info("No recommended skills available.")

    else:

        try:

            recommended_df = pd.DataFrame(recommended)



            # Remove only the requested display columns.

            recommended_df = recommended_df.drop(

                columns=[

                    "industry_demand",

                    "industry_count",

                    "research_count",

                    "research_demand",
                    "job_count",
                    "priority_score"

                ],

                errors="ignore"

            )



            st.dataframe(

                recommended_df,

                width="stretch",

                hide_index=True

            )



        except Exception:

            st.write(recommended)





# ==========================================================

# HOW HYBRID RETRIEVAL WORKS

# ==========================================================



st.divider()

st.subheader("🔄 How Hybrid Retrieval Works")



st.markdown(

    """

\*\*1. Curriculum Retrieval\*\*



Relevant curriculum information is retrieved using semantic

similarity.



\*\*2. Knowledge Graph Analysis\*\*



Graph relationships are used to examine connections between

curriculum entities and skills.



\*\*3. Skill Gap Identification\*\*



Skills that are not represented in the selected branch,

year and semester can be identified from the retrieved evidence.



\*\*4. Graph-Supported Recommendations\*\*



Relevant skills connected through the Knowledge Graph are

returned as recommendation candidates.

"""

)





# ==========================================================

# INTERPRETATION

# ==========================================================



st.divider()

st.subheader("Interpretation")



st.markdown(

    f"""

\*\*Selected Branch:\*\* \`{branch}\`



\- \*\*Vector retrieval:\*\* {len(vector_results)} curriculum results retrieved.

\- \*\*Knowledge Graph:\*\* {len(missing)} skill gaps identified.

\- \*\*Graph recommendations:\*\* {len(recommended)} recommendation candidates returned.



The purpose of Hybrid Retrieval is to combine complementary

retrieval evidence instead of depending on a single retrieval

method. The retrieved evidence is subsequently available for

the later evidence-fusion and recommendation stages.

"""

)





# ==========================================================

# STATUS

# ==========================================================



st.success(

    f"Hybrid Retrieval completed — "

    f"{len(vector_results)} vector results, "

    f"{len(missing)} missing skills and "

    f"{len(recommended)} recommendation candidates."

)
