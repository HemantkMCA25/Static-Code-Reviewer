import streamlit as st

from language_registry import LANGUAGES
from review import run_review

st.set_page_config(page_title="Code Reviewer", layout="wide")
st.title("Code Reviewer 🧑‍💻")
st.caption("Static analysis for Python and C++ code")

language = st.selectbox("Choose programming language", list(LANGUAGES), format_func=lambda k: LANGUAGES[k]["label"])
code = st.text_area(f"Paste your {LANGUAGES[language]['label']} code here", height=250)

if st.button("Review Code"):
    if not code.strip():
        st.warning("Please paste some code first.")
    else:
        result = run_review(code, language)

        st.subheader("Score")
        st.metric(label="Score (0-100)", value=result["score"])
        if result["penalties"]:
            st.caption("Points lost: " + ", ".join(
                f"{reason} (-{points})" for reason, points in result["penalties"].items()))

        st.subheader("Metrics")
        metrics = dict(result["metrics"])
        details = metrics.pop("function_details", [])
        st.json(metrics)
        if details:
            st.table(details)

        st.subheader("Feedback")
        for message in result["feedback"]:
            st.write("- " + message)
