from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, "YT-Agent Project Code Review (v2)", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, "Generated: June 19, 2026  |  Agents 1-4 built", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(20, 80, 160)
        self.ln(3)
        self.set_x(self.l_margin)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(20, 80, 160)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        self.set_text_color(30, 30, 30)

    def code_text(self, text):
        self.set_x(self.l_margin)
        self.set_font("Courier", "", 8)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(40, 40, 40)
        self.multi_cell(190, 5, text, fill=True)
        self.ln(1)

    def table_header(self, cols, widths):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(230, 237, 255)
        self.set_text_color(20, 20, 20)
        for col, w in zip(cols, widths):
            self.cell(w, 7, col, border=1, fill=True)
        self.ln()

    def table_row(self, cols, widths, fill=False):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 8)
        self.set_fill_color(250, 250, 250)
        self.set_text_color(30, 30, 30)
        h = 6
        x_start = self.l_margin
        y_start = self.get_y()
        x = x_start
        for col, w in zip(cols, widths):
            self.set_xy(x, y_start)
            self.multi_cell(w, h, str(col), border=1, fill=fill)
            x += w
        self.set_xy(x_start, self.get_y())


pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# ── SECTION 1: Issues Found ───────────────────────────────────────────────────
pdf.section_title("Issues Found")

data = [
    ("1", "ui/app.py", "all results",
     "Writer drafts, research briefs, and failed_formats are never displayed. Pipeline runs 4 stages but UI only shows 2.",
     "High"),
    ("2", "ui/app.py", "sidebar ~22",
     "Sidebar shows Agents 3 & 4 as not built (checkbox empty) but ResearchAgent and WriterAgent ARE now built.",
     "Medium"),
    ("3", "agents/research_agent.py", "~107",
     "def _parse_brief(...) -> dict | None: uses Python 3.10+ union syntax. Breaks on Python 3.9.",
     "Medium"),
    ("4", "agents/writer_agent.py", "~115",
     "def _write_format(...) -> str | None: uses Python 3.10+ union syntax. Breaks on Python 3.9.",
     "Medium"),
    ("5", "agents/research_agent.py", "~63",
     "failed_briefs dict is created and populated in the loop but never stored in result or returned. Dead variable.",
     "Low"),
    ("6", "agents/writer_agent.py", "~145",
     '"rate" in str(e).lower() uses broad check - inconsistent with the fix applied to error_classifier.py.',
     "Low"),
    ("7", "agents/research_agent.py", "~120",
     "Same broad rate-limit check: \"rate\" in str(e).lower() - should be \"rate limit\".",
     "Low"),
    ("8", "agents/orchestrator.py", "53",
     'Comment says "Stages 3-6 not built yet (placeholders)" - now wrong. Stages 3 and 4 are live.',
     "Low"),
]

widths = [8, 52, 22, 82, 14]
pdf.table_header(["#", "File", "Line", "Issue", "Sev."], widths)
for i, row in enumerate(data):
    pdf.table_row(row, widths, fill=(i % 2 == 0))

pdf.ln(4)

# ── SECTION 2: Cross-Check Results ───────────────────────────────────────────
pdf.section_title("Cross-Check Results")

checks = [
    ("ui/app.py imports from agents/orchestrator.py", "PASS"),
    ("orchestrator.py imports ResearchAgent and WriterAgent", "PASS"),
    ("orchestrator._run_writer_stage() accesses writer_result.failed_formats", "PASS"),
    ("WriterResult.failed_formats exists in base.py", "PASS"),
    ("All prompt files have {brief} placeholder", "PASS"),
    ("PROMPTS_DIR in writer_agent.py correctly points to prompts/", "PASS"),
    ("requirements.txt has streamlit, groq, yt-dlp, python-dotenv, pydub", "PASS"),
    ("railway.toml has PYTHONPATH=/app in start command", "PASS"),
    ("nixpacks.toml installs ffmpeg", "PASS"),
    ("No hardcoded Windows paths that break on Railway Linux", "PASS"),
    ("No relative imports that break on Railway", "PASS"),
    ("research_agent.py uses dict | None (Python 3.10+ only)", "WARN"),
    ("writer_agent.py uses str | None (Python 3.10+ only)", "WARN"),
    ("ui/app.py shows writer drafts to the user", "FAIL"),
    ("ui/app.py sidebar reflects Agents 3 & 4 as built", "FAIL"),
    ("reviewer_agent.py and publisher_agent.py exist", "N/A - safe"),
]

pdf.table_header(["Check", "Result"], [160, 28])
for i, (check, result) in enumerate(checks):
    pdf.table_row([check, result], [160, 28], fill=(i % 2 == 0))

pdf.ln(4)

# ── SECTION 3: Priority Fix List ─────────────────────────────────────────────
pdf.section_title("Priority Fix List")

fixes = [
    ("1", "High", "ui/app.py", "results section",
     "Add display of research briefs, writer drafts, and failed_formats after the planner section.",
     "Add after planner section:\nif result.writer_result and result.writer_result.drafts:\n    for fmt, draft in result.writer_result.drafts.items():\n        with st.expander(f\"{fmt}\"):\n            st.markdown(draft)"),
    ("2", "Medium", "ui/app.py", "sidebar ~22",
     "Update sidebar checkboxes to show Agents 3 & 4 as built.",
     '- checkmark **Agent 3** - Research\n- checkmark **Agent 4** - Writer'),
    ("3", "Medium", "agents/research_agent.py", "~107",
     "Remove dict | None return annotation for Python 3.9 compatibility.",
     "def _parse_brief(self, raw: str):"),
    ("4", "Medium", "agents/writer_agent.py", "~115",
     "Remove str | None return annotation for Python 3.9 compatibility.",
     "def _write_format(self, fmt, transcript, title, brief, config):"),
    ("5", "Low", "agents/research_agent.py", "~63",
     "Remove dead failed_briefs variable (never stored or returned).",
     "Delete:  failed_briefs = {}  and all failed_briefs[fmt] = ... assignments"),
    ("6", "Low", "agents/writer_agent.py", "~145",
     "Tighten inline rate-limit check to match error_classifier fix.",
     'if "429" in str(e) or "rate limit" in str(e).lower():'),
    ("7", "Low", "agents/research_agent.py", "~120",
     "Same inline rate-limit tightening.",
     'if "429" in str(e) or "rate limit" in str(e).lower():'),
    ("8", "Low", "agents/orchestrator.py", "53",
     "Update stale comment.",
     '# Stages 3-4 live; Stages 5-6 not built yet'),
]

for num, sev, file_, line, desc, fix in fixes:
    pdf.set_font("Helvetica", "B", 9)
    sev_color = (180, 30, 30) if sev == "High" else (200, 80, 0) if sev == "Medium" else (60, 120, 50)
    pdf.set_text_color(*sev_color)
    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 6, f"Fix {num} - {sev}  |  {file_}  (line {line})", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(190, 5.5, desc)
    pdf.code_text(fix)
    pdf.ln(1)

# ── SECTION 4: Current Build Status ──────────────────────────────────────────
pdf.section_title("Current Build Status")

status_rows = [
    ("Agent 1", "TranscriptAgent", "agents/transcript_agent.py", "BUILT"),
    ("Agent 2", "PlannerAgent",    "agents/planner_agent.py",    "BUILT"),
    ("Agent 3", "ResearchAgent",   "agents/research_agent.py",   "BUILT"),
    ("Agent 4", "WriterAgent",     "agents/writer_agent.py",     "BUILT"),
    ("Agent 5", "ReviewerAgent",   "agents/reviewer_agent.py",   "NOT YET"),
    ("Agent 6", "PublisherAgent",  "agents/publisher_agent.py",  "NOT YET"),
]

pdf.table_header(["Stage", "Class", "File", "Status"], [20, 40, 90, 28])
for i, row in enumerate(status_rows):
    pdf.table_row(row, [20, 40, 90, 28], fill=(i % 2 == 0))

out_path = r"c:\Users\user\Downloads\yt-agent\yt_agent_code_review.pdf"
pdf.output(out_path)
print(f"PDF saved to: {out_path}")
