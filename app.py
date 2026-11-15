"""Academic Pathway Reasoning System - applicant interface (Technical Mono Y2K).

Run with:  streamlit run app.py        (the full 14-page version is app_full.py)
The predicate-logic engine decides eligibility. The AI assistant explains: offline by default, optional Claude mode.
"""
import streamlit as st

st.set_page_config(page_title="Pathway Finder // AI", page_icon="🖥️", layout="wide")

from database import db  # noqa: E402
from ui import common, studio, theme  # noqa: E402

NONE = "+ New student"
P = studio.PAGES
RENDER = dict(zip(P, [studio.page_profile, studio.page_programmes, studio.page_gaps, studio.page_reasoning, studio.page_assistant, studio.page_quality]))


def safe(fn):
    """Show a friendly message instead of an error box. Streamlit's own stop/rerun signals pass through."""
    try:
        fn()
    except Exception as exc:  # noqa: BLE001
        if type(exc).__name__ in ("StopException", "RerunException"):
            raise
        st.warning("Something unexpected happened on this page. Your saved data is safe. Try another page or reload.")
        with st.expander("TECHNICAL DETAIL"):
            st.code(repr(exc))


def sidebar(ids: list, labels: dict) -> None:
    with st.sidebar:
        theme.show("<div class='aps-brand'>&gt; PATHWAY_FINDER.AI</div><div class='aps-brandsub'>know where you stand // see the way in</div>")
        choice = st.selectbox("Student", [NONE] + ids, key="active_student", format_func=lambda i: i if i == NONE else labels[i])
        st.session_state["student_id"] = None if choice == NONE else choice
        st.markdown("**AI ASSISTANT**")
        st.radio("Mode", ["Offline (rules only)", "Claude (online, needs key)"], key="ai_mode_choice", label_visibility="collapsed")
        if st.session_state.get("ai_mode_choice", "").startswith("Claude"):
            st.text_input("Anthropic API key", type="password", key="ai_key", placeholder="sk-ant-...")
            st.text_input("Model", key="ai_model", value="claude-sonnet-5-5")
            st.caption("Sends your marks and the engine's results (not your name) to the Anthropic API. The key is kept in this session only.")
        st.caption("Rule-based, explainable. Sample criteria are illustrative, not official.")


def main():
    theme.inject()
    students = db.list_students(common.get_conn())
    ids = [s["student_id"] for s in students]
    labels = {s["student_id"]: s["student_id"] + (f" - {s['name']}" if s["name"] else "") for s in students}
    pending = st.session_state.pop("_select_student", "__none__")
    if pending != "__none__":
        st.session_state["active_student"] = pending or NONE
        st.session_state["nav_page"] = P[1] if pending else P[0]
    if st.session_state.get("active_student") not in [NONE] + ids:
        st.session_state["active_student"] = NONE
    sidebar(ids, labels)
    if st.session_state.get("nav_page") not in P:
        st.session_state["nav_page"] = P[0]
    page = st.radio("Step", P, key="nav_page", horizontal=True, label_visibility="collapsed")
    safe(RENDER[page])


main()
