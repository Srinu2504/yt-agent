"""
YT Agent - Production Readiness Review PDF Generator
Run: python generate_review_pdf.py
Output: yt_agent_review.pdf
"""
from fpdf import FPDF
import subprocess

W = 190  # usable page width in mm


class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(20, 60, 140)
        self.cell(0, 9, "YT Agent - Production Readiness Review", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 5, "Generated: June 19, 2026  |  Agents 1-4 built  |  Railway deployment", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        self.set_draw_color(180, 200, 240)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section(self, title, color=(20, 80, 160)):
        self.ln(4)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*color)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*color)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        self.set_text_color(30, 30, 30)

    def subsection(self, title):
        self.ln(2)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(60, 60, 60)
        self.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(30, 30, 30)

    def body(self, text):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        self.multi_cell(W, 5.5, text)
        self.ln(1)

    def code(self, text):
        self.set_x(self.l_margin)
        self.set_font("Courier", "", 8)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(40, 40, 40)
        self.multi_cell(W, 4.8, text, fill=True)
        self.ln(1)

    def thead(self, cols, widths):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(220, 230, 255)
        self.set_text_color(20, 20, 60)
        for col, w in zip(cols, widths):
            self.cell(w, 7, col, border=1, fill=True)
        self.ln()

    def trow(self, cols, widths, fill=False, sev=None):
        self.set_x(self.l_margin)
        h = 5.5
        x0 = self.l_margin
        y0 = self.get_y()
        if sev == "High":
            self.set_fill_color(255, 235, 235)
        elif sev == "Medium":
            self.set_fill_color(255, 248, 235)
        elif fill:
            self.set_fill_color(248, 250, 255)
        else:
            self.set_fill_color(255, 255, 255)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(30, 30, 30)
        x = x0
        for col, w in zip(cols, widths):
            self.set_xy(x, y0)
            self.multi_cell(w, h, str(col), border=1, fill=True)
            x += w
        self.set_xy(x0, self.get_y())

    def checklist_row(self, label, status):
        self.set_x(self.l_margin)
        icon = "YES" if status else "NO"
        color = (0, 130, 0) if status else (180, 0, 0)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        self.cell(155, 6, label)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*color)
        self.cell(25, 6, icon, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(30, 30, 30)


# ─────────────────────────────────────────────────────────────────────────────
pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# ── COVER SUMMARY ─────────────────────────────────────────────────────────────
pdf.section("Executive Summary")
pdf.body(
    "This report covers a full production-readiness review of the yt-agent project "
    "as of June 19, 2026. Agents 1-4 (Transcript, Planner, Research, Writer) are built "
    "and wired. Agents 5-6 (Reviewer, Publisher) are not yet built. "
    "Total issues found: 13 across all categories. "
    "0 High | 2 Medium | 11 Low. "
    "The project is broadly Railway-ready with minor improvements recommended."
)

pdf.set_x(pdf.l_margin)
pdf.set_font("Helvetica", "B", 9)
pdf.set_text_color(20, 80, 160)
pdf.cell(0, 6, "Issue Count by Category:", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(30, 30, 30)

summary = [
    ("Category", "Issues", "High", "Medium", "Low"),
    ("Syntax / Import", "1", "0", "1", "0"),
    ("Logic", "2", "0", "1", "1"),
    ("Railway Compatibility", "2", "0", "0", "2"),
    ("Environment Variables", "1", "0", "0", "1"),
    ("UI Completeness", "2", "0", "0", "2"),
    ("Error Handling", "2", "0", "0", "2"),
    ("Performance", "3", "0", "0", "3"),
    ("TOTAL", "13", "0", "2", "11"),
]
pdf.thead(summary[0], [70, 20, 20, 25, 25])
for i, row in enumerate(summary[1:]):
    pdf.trow(row, [70, 20, 20, 25, 25], fill=(i % 2 == 0))

# ── SECTION 1: SYNTAX AND IMPORTS ────────────────────────────────────────────
pdf.section("Section 1 - Syntax and Import Errors")

pdf.body(
    "All imports resolve correctly. No circular imports. No missing __init__.py. "
    "No match/case syntax. One Python 3.10+ annotation remains in research_agent.py."
)

s1_data = [
    ("agents/research_agent.py", "~100",
     "_research_format return type -> str | None requires Python 3.10+. Works on Railway (python312) but breaks on local Python 3.9.",
     "Medium",
     "def _research_format(self, fmt: str, transcript: str):"),
]
pdf.thead(["File", "Line", "Issue", "Sev.", "Fix"], [50, 12, 72, 16, 40])
for i, row in enumerate(s1_data):
    pdf.trow(row, [50, 12, 72, 16, 40], sev=row[3])

pdf.subsection("Import Chain (no circular dependencies)")
pdf.code(
    "orchestrator -> transcript_agent, planner_agent, research_agent, writer_agent\n"
    "all agents -> agents/base.py\n"
    "all agents -> agents/error_classifier.py (where needed)\n"
    "transcript_agent -> core/download_engine, core/transcribe_engine"
)

# ── SECTION 2: LOGIC ERRORS ───────────────────────────────────────────────────
pdf.add_page()
pdf.section("Section 2 - Logic Errors")

pdf.body(
    "Data flows correctly through all 4 stages. StepLog fields populated correctly. "
    "One UI patching gap for live log display. One optional float formatting concern."
)

s2_data = [
    ("ui/app.py", "spinner block",
     "research_agent._log and writer_agent._log not patched for UI live log. Users see no R+W progress in the live log panel.",
     "Medium",
     "Add: orch.research_agent._log = ui_r_log and orch.writer_agent._log = ui_w_log"),
    ("ui/app.py", "results ~line 100",
     "result.duration_sec is Optional[float] but used with :.1f format. Safe in practice (all return paths set it) but no explicit guard.",
     "Low",
     "Add: if result.duration_sec is not None: before the caption line"),
]
pdf.thead(["File", "Line", "Issue", "Sev.", "Fix"], [45, 20, 72, 16, 37])
for i, row in enumerate(s2_data):
    pdf.trow(row, [45, 20, 72, 16, 37], sev=row[3])

pdf.subsection("Data Flow Verification - All Passing")
checks_flow = [
    ("transcript_result.transcript -> planner_agent.run()", True),
    ("planner_result.formats_chosen -> research_agent.run()", True),
    ("research_result.briefs -> writer_agent.run()", True),
    ("writer_result.failed_formats exists in base.py WriterResult", True),
    ("orchestrator._run_writer_stage accesses writer_result.failed_formats", True),
    ("orchestrator handles research failure (non-fatal, writer uses raw transcript)", True),
    ("All StepLog required fields populated in every agent", True),
]
for label, ok in checks_flow:
    pdf.checklist_row(label, ok)

# ── SECTION 3: RAILWAY COMPATIBILITY ─────────────────────────────────────────
pdf.add_page()
pdf.section("Section 3 - Railway Compatibility")

pdf.body(
    "Project is Railway-ready. All path resolution uses os.path.join with __file__. "
    "PYTHONPATH=/app ensures all imports work. ffmpeg installed via nixpacks. "
    "Two minor documentation issues noted."
)

s3_data = [
    ("CLAUDE.md", "all",
     "Says Agents 3-6 are NOT YET BUILT or stub only. Agents 3 and 4 ARE now built.",
     "Low",
     "Update CLAUDE.md to reflect current build status"),
    (".gitignore", "all",
     "test_writer_result.json is missing from .gitignore. Will be committed accidentally.",
     "Low",
     "Add: test_writer_result.json to .gitignore"),
]
pdf.thead(["File", "Line", "Issue", "Sev.", "Fix"], [40, 12, 80, 16, 42])
for i, row in enumerate(s3_data):
    pdf.trow(row, [40, 12, 80, 16, 42], sev=row[3])

pdf.subsection("Railway Readiness Checklist")
railway_checks = [
    ("PYTHONPATH=/app in railway.toml startCommand", True),
    ("ffmpeg installed via nixpacks.toml", True),
    ("python312 specified in nixpacks.toml", True),
    ("Health check path /_stcore/health set in railway.toml", True),
    ("--server.headless true in startCommand", True),
    ("--server.address 0.0.0.0 in startCommand", True),
    ("--server.port $PORT in startCommand", True),
    ("agents/__init__.py exists", True),
    ("core/__init__.py exists", True),
    ("data/audio/.gitkeep exists", True),
    ("data/exports/.gitkeep exists", True),
    ("PROMPTS_DIR resolves to /app/prompts on Railway", True),
    ("AUDIO_DIR resolves to /app/data/audio on Railway", True),
    ("No hardcoded Windows paths in any runtime code", True),
    ("All required packages in requirements.txt", True),
    (".env excluded from .gitignore", True),
    (".env.example exists for new developers", False),
    ("CLAUDE.md is up to date", False),
]
for label, ok in railway_checks:
    pdf.checklist_row(label, ok)

# ── SECTION 4: ENVIRONMENT VARIABLES ─────────────────────────────────────────
pdf.add_page()
pdf.section("Section 4 - Environment Variables")

pdf.body(
    "All 5 env vars are handled safely. GROQ_API_KEY is explicitly checked before use "
    "in every agent. YOUTUBE_COOKIES returns None gracefully when not set. "
    "One minor pattern issue: GROQ_API_KEY is captured at module import time."
)

s4_data = [
    ("GROQ_API_KEY", "planner, research, writer, transcribe_engine",
     "Required", "Empty string", "No - checked with 'if not GROQ_API_KEY' in every agent"),
    ("YOUTUBE_COOKIES", "core/download_engine.py",
     "Optional", "None (no cookies)", "No - gracefully skipped"),
    ("MAX_VIDEO_DURATION_MINUTES", "core/download_engine.py",
     "Optional", "60", "No"),
    ("WHISPER_MODEL", "core/transcribe_engine.py",
     "Optional", "whisper-large-v3-turbo", "No"),
    ("LLM_MODEL", "planner, research, writer agents",
     "Optional", "llama-3.3-70b-versatile", "No"),
    ("PORT", "railway.toml startCommand",
     "Railway auto-sets", "N/A", "Railway sets automatically"),
]
pdf.thead(["Variable", "Used In", "Required?", "Default", "Crash if missing?"], [40, 50, 22, 38, 40])
for i, row in enumerate(s4_data):
    pdf.trow(row, [40, 50, 22, 38, 40], fill=(i % 2 == 0))

pdf.ln(3)
pdf.subsection("Issue Found")
s4_issues = [
    ("All LLM agents", "module top",
     "GROQ_API_KEY read at import time (os.getenv at module level). Safe on Railway (env vars set before process starts) but could be empty string on weird hot-reload scenarios.",
     "Low",
     "Acceptable risk. No change needed for Railway."),
]
pdf.thead(["File", "Line", "Issue", "Sev.", "Fix"], [35, 16, 76, 16, 47])
for i, row in enumerate(s4_issues):
    pdf.trow(row, [35, 16, 76, 16, 47], sev=row[3])

# ── SECTION 5: UI COMPLETENESS ────────────────────────────────────────────────
pdf.add_page()
pdf.section("Section 5 - UI Completeness")

pdf.subsection("Feature Checklist")
ui_checks = [
    ("Shows transcript: title, word count, duration, channel", True),
    ("Shows full transcript in expandable text area", True),
    ("Shows planner: formats chosen + reasoning", True),
    ("Shows research briefs in expandable section", True),
    ("Shows writer drafts with markdown rendering", True),
    ("Shows per-format TXT download button", True),
    ("Shows per-format Copy button", True),
    ("Shows failed formats with reasons", True),
    ("Shows full agent log (expandable)", True),
    ("Shows pipeline failure with failed stage name", True),
    ("Sidebar correctly shows Agents 1-4 as built", True),
    ("Sidebar correctly shows Agents 5-6 as not built", True),
    ("All st.button/st.download_button keys are unique", True),
    ("GROQ_API_KEY missing check shown to user before running", True),
    ("Empty URL check with st.error + st.stop()", True),
    ("ResearchAgent + WriterAgent log shown in live log panel", False),
]
for label, ok in ui_checks:
    pdf.checklist_row(label, ok)

pdf.ln(3)
pdf.subsection("Issues Found")
s5_issues = [
    ("ui/app.py", "spinner block",
     "research_agent._log and writer_agent._log not patched. Live log shows only Transcript + Planner progress, not R+W.",
     "Medium",
     "Patch orch.research_agent._log and orch.writer_agent._log inside the spinner block"),
    ("ui/app.py", "format_icons",
     "format_icons dict defined twice in same scope (once inside planner block, once outside for R+W). Redundant.",
     "Low",
     "Define format_icons once at the top of the 'if run_btn:' block and reuse it everywhere"),
]
pdf.thead(["File", "Line", "Issue", "Sev.", "Fix"], [40, 22, 72, 16, 40])
for i, row in enumerate(s5_issues):
    pdf.trow(row, [40, 22, 72, 16, 40], sev=row[3])

# ── SECTION 6: ERROR HANDLING ─────────────────────────────────────────────────
pdf.add_page()
pdf.section("Section 6 - Error Handling Gaps")

pdf.subsection("Retry Coverage")
retry_checks = [
    ("TranscriptAgent: rate limit retry with backoff", True),
    ("TranscriptAgent: UNRECOVERABLE errors stop immediately (no wasted retries)", True),
    ("TranscriptAgent: tries 4 audio format candidates on FORMAT_ERROR", True),
    ("PlannerAgent: 3 retries with backoff on any exception", True),
    ("ResearchAgent: rate limit retry with backoff", True),
    ("ResearchAgent: failure is non-fatal (writer uses raw transcript)", True),
    ("WriterAgent: rate limit retry with backoff", True),
    ("WriterAgent: 401 invalid API key detected and returns None immediately", True),
    ("Orchestrator: stops pipeline on critical failures", True),
    ("All agents: GROQ_API_KEY checked before first API call", True),
]
for label, ok in retry_checks:
    pdf.checklist_row(label, ok)

pdf.ln(3)
pdf.subsection("Issues Found")
s6_issues = [
    ("agents/planner_agent.py", "~128",
     "'import time' inside except block (inside retry loop). Python caches imports but it is re-executed syntax each iteration.",
     "Low",
     "Move 'import time' to top of file"),
    ("agents/research_agent.py", "_parse_brief",
     "'import json, re' inside method body. Inefficient but not broken.",
     "Low",
     "Move imports to top of file"),
]
pdf.thead(["File", "Line", "Issue", "Sev.", "Fix"], [45, 20, 75, 16, 34])
for i, row in enumerate(s6_issues):
    pdf.trow(row, [45, 20, 75, 16, 34], sev=row[3])

# ── SECTION 7: PERFORMANCE ────────────────────────────────────────────────────
pdf.add_page()
pdf.section("Section 7 - Performance on Railway Free Tier")

pdf.subsection("API Call Budget (full pipeline, 4 formats)")
perf_rows = [
    ("TranscriptAgent", "1x Groq Whisper", "~10-30s", "~1-5 MB audio"),
    ("PlannerAgent", "1x Groq LLM (256 tokens)", "~2-5s", "Negligible"),
    ("ResearchAgent", "4x Groq LLM (300 tokens)", "~12-20s", "Negligible"),
    ("WriterAgent", "4x Groq LLM (600-3000 tokens)", "~20-60s", "~5-20 KB per draft"),
    ("TOTAL", "10 Groq calls", "~75-175s per run", "~5 MB peak disk"),
]
pdf.thead(["Agent", "API Calls", "Est. Time", "Memory/Disk"], [35, 55, 55, 45])
for i, row in enumerate(perf_rows):
    pdf.trow(row, [35, 55, 55, 45], fill=(i % 2 == 0))

pdf.ln(3)
pdf.body(
    "Groq free tier limit: ~30 requests/minute. 10 calls is well within limits. "
    "Audio file (~5MB for 10-min video at 64kbps) is deleted after transcription. "
    "Railway ephemeral storage is sufficient."
)

pdf.subsection("Issues Found")
s7_issues = [
    ("agents/writer_agent.py", "all LLM calls",
     "Groq client instantiated on every API call: 'client = Groq(api_key=...)' inside retry loop. Minor overhead.",
     "Low",
     "Instantiate Groq client once in __init__ or at module level"),
    ("agents/research_agent.py", "all LLM calls",
     "Same Groq client instantiation per call.",
     "Low",
     "Same fix: move Groq(api_key=GROQ_API_KEY) to __init__"),
    ("agents/planner_agent.py", "all LLM calls",
     "Same Groq client instantiation per call.",
     "Low",
     "Same fix"),
]
pdf.thead(["File", "Line", "Issue", "Sev.", "Fix"], [45, 22, 70, 16, 37])
for i, row in enumerate(s7_issues):
    pdf.trow(row, [45, 22, 70, 16, 37], sev=row[3])

# ── PRIORITY FIX LIST ─────────────────────────────────────────────────────────
pdf.add_page()
pdf.section("Priority Fix List (all 13 issues)")

all_fixes = [
    ("1", "Medium", "ui/app.py",
     "Patch research_agent._log and writer_agent._log for live UI log",
     "Add inside spinner block:\ndef ui_r_log(msg): append_log(f'[Research] {msg}')\ndef ui_w_log(msg): append_log(f'[Writer]   {msg}')\norch.research_agent._log = ui_r_log\norch.writer_agent._log = ui_w_log"),
    ("2", "Medium", "agents/research_agent.py",
     "Remove str | None return annotation from _research_format",
     "def _research_format(self, fmt: str, transcript: str):"),
    ("3", "Low", "ui/app.py",
     "Guard result.duration_sec before .1f format",
     "if result.duration_sec is not None:\n    st.caption(f'Completed in {result.duration_sec:.1f}s')"),
    ("4", "Low", "ui/app.py",
     "Define format_icons once at top of if run_btn: block",
     "Move format_icons dict definition to just after 'if run_btn:' opens"),
    ("5", "Low", ".gitignore",
     "Add test_writer_result.json",
     "Append: test_writer_result.json"),
    ("6", "Low", "CLAUDE.md",
     "Update to show Agents 3 & 4 as built",
     "Change 'NOT YET BUILT' to built for Agents 3 & 4"),
    ("7", "Low", "project root",
     "Create .env.example for new developer onboarding",
     "GROQ_API_KEY=your_key_here\nYOUTUBE_COOKIES=\nMAX_VIDEO_DURATION_MINUTES=60"),
    ("8", "Low", "agents/planner_agent.py",
     "Move 'import time' from inside except block to top of file",
     "Add: import time  at top (line 1-5 area)"),
    ("9", "Low", "agents/research_agent.py",
     "Move 'import json, re' from _parse_brief to top of file",
     "Add: import json, re  at top of file"),
    ("10", "Low", "agents/planner_agent.py",
     "Instantiate Groq client once in __init__ not per API call",
     "self.client = Groq(api_key=GROQ_API_KEY)  in __init__"),
    ("11", "Low", "agents/research_agent.py",
     "Same Groq client fix",
     "self.client = Groq(api_key=GROQ_API_KEY)  in __init__"),
    ("12", "Low", "agents/writer_agent.py",
     "Same Groq client fix",
     "self.client = Groq(api_key=GROQ_API_KEY)  in __init__"),
    ("13", "Low", "agents/writer_agent.py",
     "result.duration_sec Optional[float] formatted directly - safe but fragile",
     "Acceptable risk - all code paths set it. No change required."),
]

for num, sev, file_, desc, fix in all_fixes:
    sev_color = (200, 80, 0) if sev == "Medium" else (60, 120, 50)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*sev_color)
    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 6, f"Fix {num} [{sev}]  {file_}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(40, 40, 40)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(W, 5, desc)
    pdf.code(fix)
    pdf.ln(1)

out_path = r"c:\Users\user\Downloads\yt-agent\yt_agent_review.pdf"
pdf.output(out_path)
print(f"PDF saved to: {out_path}")
