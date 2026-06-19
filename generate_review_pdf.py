from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, "YT-Agent Project Code Review", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, "Generated: June 16, 2026", align="C", new_x="LMARGIN", new_y="NEXT")
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
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(20, 80, 160)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        self.set_text_color(30, 30, 30)

    def body_text(self, text, bold=False):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B" if bold else "", 9)
        self.set_text_color(30, 30, 30)
        self.multi_cell(190, 5.5, text)
        self.ln(1)

    def code_text(self, text):
        self.set_x(self.l_margin)
        self.set_font("Courier", "", 8)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(40, 40, 40)
        self.multi_cell(190, 5, text, fill=True)
        self.ln(1)

    def table_header(self, cols, widths):
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(230, 237, 255)
        self.set_text_color(20, 20, 20)
        for col, w in zip(cols, widths):
            self.cell(w, 7, col, border=1, fill=True)
        self.ln()

    def table_row(self, cols, widths, fill=False):
        self.set_font("Helvetica", "", 8)
        self.set_fill_color(250, 250, 250)
        self.set_text_color(30, 30, 30)
        h = 6
        x_start = self.get_x()
        y_start = self.get_y()
        x = x_start
        for col, w in zip(cols, widths):
            self.set_xy(x, y_start)
            self.multi_cell(w, h, str(col), border=1, fill=fill)
            x += w
        max_y = self.get_y()
        self.set_xy(x_start, max_y)

    def severity_badge(self, text, severity):
        colors = {
            "Medium": (220, 100, 0),
            "Low":    (80, 140, 60),
        }
        r, g, b = colors.get(severity, (100, 100, 100))
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(r, g, b)
        self.cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(30, 30, 30)


pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# ── SECTION 1: Issues Found ──────────────────────────────────────────────────
pdf.section_title("Issues Found")

issues = [
    ("#", "File", "Line", "Issue", "Sev."),
]
data = [
    ("1", "agents/error_classifier.py", "22",
     '"rate" in msg too broad - matches "bitrate","framerate" etc. Could misclassify errors as RATE_LIMIT.',
     "Medium"),
    ("2", "agents/planner_agent.py", "125",
     'dict | None syntax requires Python 3.10+. Breaks locally on Python 3.9.',
     "Medium"),
    ("3", "agents/transcript_agent.py", "16",
     "RETRYABLE_FOR_FORMAT imported but never used.",
     "Low"),
    ("4", "agents/transcript_agent.py", "90",
     "error_type=ErrorType.DURATION_EXCEEDED passes enum object instead of .value. Inconsistent with all other StepLog calls.",
     "Low"),
    ("5", "ui/app.py", "72-73",
     "orig_t_log and orig_p_log assigned but never read or restored.",
     "Low"),
    ("6", "nixpacks.toml", "4-5",
     '[start] cmd says "No web server yet" - stale/misleading, railway.toml overrides it.',
     "Low"),
]

widths = [8, 52, 12, 88, 18]
headers = ["#", "File", "Line", "Issue", "Sev."]
pdf.table_header(headers, widths)
for i, row in enumerate(data):
    pdf.table_row(row, widths, fill=(i % 2 == 0))

pdf.ln(4)

# ── SECTION 2: Cross-Check Results ──────────────────────────────────────────
pdf.section_title("Cross-Check Results - All Passing")

checks = [
    ("ui/app.py imports from agents/orchestrator.py", "PASS"),
    ("orchestrator.py imports TranscriptAgent and PlannerAgent", "PASS"),
    ("transcript_agent.py imports from agents/error_classifier.py", "PASS"),
    ("transcript_agent.py imports from core/download_engine.py", "PASS"),
    ("transcript_agent.py imports from core/transcribe_engine.py", "PASS"),
    ("planner_agent.py imports from agents/base.py", "PASS"),
    ("PYTHONPATH=/app resolves agents/ and core/ imports", "PASS"),
    ("requirements.txt has streamlit, groq, yt-dlp, python-dotenv, pydub", "PASS"),
    ("railway.toml has correct startCommand with PYTHONPATH=/app", "PASS"),
    ("nixpacks.toml installs ffmpeg", "PASS"),
    ("No relative imports that break on Railway", "PASS"),
    ("No Windows-only hardcoded paths", "PASS"),
    ("sys.path in ui/app.py set correctly (redundant but harmless)", "PASS"),
    ("Missing agents (publisher, research, reviewer, writer) - not imported anywhere", "PASS - safe"),
]

pdf.table_header(["Check", "Result"], [160, 28])
for i, (check, result) in enumerate(checks):
    pdf.table_row([check, result], [160, 28], fill=(i % 2 == 0))

pdf.ln(4)

# ── SECTION 3: Priority Fix List ────────────────────────────────────────────
pdf.section_title("Priority Fix List")

fixes = [
    ("1", "Medium", "agents/error_classifier.py", "22",
     "Tighten the rate-limit classifier",
     'if "429" in msg or "rate limit" in msg or "ratelimit" in msg or "too many requests" in msg:'),
    ("2", "Medium", "agents/planner_agent.py", "125",
     "Replace dict | None with Optional[dict] for Python 3.9 compatibility",
     "def _parse_response(self, raw: str) -> Optional[dict]:"),
    ("3", "Low", "agents/transcript_agent.py", "16",
     "Remove unused import RETRYABLE_FOR_FORMAT",
     "Delete:  RETRYABLE_FOR_FORMAT,  from the import block"),
    ("4", "Low", "agents/transcript_agent.py", "90",
     "Use .value on enum for StepLog consistency",
     "error_type=ErrorType.DURATION_EXCEEDED.value"),
    ("5", "Low", "ui/app.py", "72-73",
     "Remove unused variables orig_t_log and orig_p_log",
     "Delete the two orig_*_log = ... assignment lines"),
    ("6", "Low", "nixpacks.toml", "4-5",
     "Remove stale [start] section - railway.toml controls the start command",
     "Delete the [start] section entirely from nixpacks.toml"),
]

for num, sev, file_, line, desc, fix in fixes:
    pdf.set_font("Helvetica", "B", 9)
    sev_color = (200, 80, 0) if sev == "Medium" else (60, 120, 50)
    pdf.set_text_color(*sev_color)
    pdf.cell(0, 6, f"Fix {num} - {sev}  |  {file_}  (line {line})", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(190, 5.5, desc)
    pdf.code_text(fix)
    pdf.ln(1)

# ── SECTION 4: Files Not Yet Created ────────────────────────────────────────
pdf.section_title("Files Not Yet Created (Future Stages)")

pdf.set_font("Helvetica", "", 9)
pdf.set_text_color(30, 30, 30)
missing = [
    "agents/publisher_agent.py  - Stage 6",
    "agents/research_agent.py   - Stage 3",
    "agents/reviewer_agent.py   - Stage 5",
    "agents/writer_agent.py     - Stage 4",
]
for m in missing:
    pdf.cell(5)
    pdf.cell(0, 6, f"  {m}  (not imported anywhere - safe to add later)", new_x="LMARGIN", new_y="NEXT")

pdf.ln(4)
pdf.set_font("Helvetica", "I", 9)
pdf.set_text_color(100, 100, 100)
pdf.set_x(pdf.l_margin)
pdf.multi_cell(190, 5.5,
    "None of the missing agent files are imported anywhere in the current codebase. "
    "The Orchestrator holds None placeholders for them. No breaking issues at this stage.")

out_path = r"c:\Users\user\Downloads\yt-agent\yt_agent_code_review.pdf"
pdf.output(out_path)
print(f"PDF saved to: {out_path}")
