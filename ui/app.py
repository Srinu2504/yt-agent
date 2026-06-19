import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from agents.orchestrator import Orchestrator

st.set_page_config(
    page_title="YT Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🤖 YT Agent")
    st.caption("Agentic YouTube content pipeline")
    st.divider()

    st.markdown("### Agents")
    st.markdown("""
    - ✅ **Agent 1** — Transcript
    - ✅ **Agent 2** — Planner  
    - ⬜ Agent 3 — Research
    - ⬜ Agent 4 — Writer
    - ⬜ Agent 5 — Reviewer
    - ⬜ Agent 6 — Publisher
    """)

    st.divider()

    api_status = "✅ Set" if os.environ.get("GROQ_API_KEY") else "❌ Missing"
    st.caption(f"Groq API Key: {api_status}")
    st.caption("Groq Whisper + Llama 3.3 70B")

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("🤖 YT Agentic Pipeline")
st.caption(
    "Paste a YouTube URL — agents handle download, "
    "transcription, and content planning automatically."
)

st.divider()

url_input = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="collapsed",
)

run_btn = st.button("Run agents ✨", type="primary", use_container_width=False)

st.divider()

# ── Pipeline ──────────────────────────────────────────────────────────────────
if run_btn:
    if not url_input.strip():
        st.error("Please enter a YouTube URL.")
        st.stop()

    if not os.environ.get("GROQ_API_KEY"):
        st.error("GROQ_API_KEY is not set. Add it in Railway → Variables.")
        st.stop()

    url = url_input.strip()

    # Normalise URL
    import re
    match = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})", url)
    if match:
        url = f"https://www.youtube.com/watch?v={match.group(1)}"

    st.info(f"Running pipeline on: `{url}`")

    # Live agent log shown in UI
    log_area  = st.empty()
    log_lines = []

    def append_log(msg: str):
        log_lines.append(msg)
        log_area.code("\n".join(log_lines), language=None)

    with st.spinner("Agents running..."):
        orch   = Orchestrator(verbose=False)

        # Patch agents to report to UI
        def ui_t_log(msg):
            append_log(f"[Transcript] {msg}")

        def ui_p_log(msg):
            append_log(f"[Planner]    {msg}")

        orch.transcript_agent._log = ui_t_log
        orch.planner_agent._log    = ui_p_log

        result = orch.run(url)

    st.divider()

    # ── Results ───────────────────────────────────────────────────────────────
    status_icon = "✅" if result.status == "success" else "❌"
    st.subheader(f"{status_icon} Pipeline result — {result.status.upper()}")
    st.caption(f"Completed in {result.duration_sec:.1f}s")

    if result.transcript_result and result.transcript_result.status == "success":
        t = result.transcript_result
        col1, col2, col3 = st.columns(3)
        col1.metric("Words", t.word_count)
        col2.metric("Duration", f"{t.duration_sec}s")
        col3.metric("Status", "✅ Done")

        st.subheader(f"📹 {t.title}")
        st.caption(f"Channel: {t.channel}")

        with st.expander("📝 Full transcript", expanded=False):
            st.text_area(
                "Transcript",
                t.transcript,
                height=250,
                label_visibility="collapsed"
            )
            st.caption(f"{t.word_count} words · {len(t.transcript)} characters")

    elif result.transcript_result and result.transcript_result.status == "failed":
        st.error(f"Transcript Agent failed: {result.transcript_result.error}")

    if result.planner_result and result.planner_result.status == "success":
        p = result.planner_result
        st.subheader("📋 Planner decision")

        if p.formats_chosen:
            format_icons = {
                "linkedin_post":    "💼 LinkedIn Post",
                "linkedin_article": "📝 LinkedIn Article",
                "twitter_thread":   "🐦 Twitter Thread",
                "blog_post":        "📖 Blog Post",
            }
            cols = st.columns(len(p.formats_chosen))
            for i, fmt in enumerate(p.formats_chosen):
                cols[i].success(format_icons.get(fmt, fmt))
            st.caption(f"Reasoning: {p.reasoning}")
        else:
            st.warning("Planner chose no formats for this video.")
            st.caption(p.reasoning)

    elif result.planner_result and result.planner_result.status == "failed":
        st.error(f"Planner Agent failed: {result.planner_result.error}")

    # ── Full agent log ─────────────────────────────────────────────────────
    if result.full_log:
        with st.expander("🔍 Full agent log", expanded=False):
            for log in result.full_log:
                icon = "✅" if log.outcome == "success" else "❌"
                st.markdown(
                    f"{icon} `[{log.agent}]` **{log.step}** "
                    f"— {log.detail}"
                    + (f" — `{log.error_type}`" if log.error_type else "")
                )

    if result.status == "failed" and result.failed_at_stage:
        st.error(f"Pipeline failed at stage: **{result.failed_at_stage}**")
