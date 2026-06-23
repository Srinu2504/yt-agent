# Project: YT Agent — Agentic YouTube AI

## What this project does
Takes a YouTube URL as input. Six specialized agents handle everything automatically:
1. TranscriptAgent — downloads audio, classifies errors, transcribes via Groq Whisper
2. PlannerAgent — decides which content formats are worth generating
3. ResearchAgent — finds best angle and tone per format (NOT YET BUILT)
4. WriterAgent — drafts each format using research brief (NOT YET BUILT)
5. ReviewerAgent — scores and revises drafts (NOT YET BUILT)
6. PublisherAgent — exports and saves to DB (NOT YET BUILT)
7. Orchestrator — coordinates all agents in sequence

## Stack
- Language: Python 3.12
- UI: Streamlit (ui/app.py)
- Transcription: Groq Whisper large-v3-turbo (free tier)
- LLM: Groq Llama 3.3 70B (free tier)
- Audio download: yt-dlp
- Audio processing: pydub + ffmpeg
- Deployment: Railway
- Config: python-dotenv

## Project structure
agents/
  base.py              — shared dataclasses and contracts for all agents
  error_classifier.py  — classifies yt-dlp/API errors into categories
  orchestrator.py      — coordinates all 6 agents in sequence
  transcript_agent.py  — Agent 1: download + transcribe with error reasoning
  planner_agent.py     — Agent 2: LLM decides which formats to generate
  research_agent.py    — Agent 3: BUILT — one Groq call per format, returns brief dict
  writer_agent.py      — Agent 4: BUILT — format loop, Approach 3, partial success supported
  reviewer_agent.py    — Agent 5: stub only, not yet built
  publisher_agent.py   — Agent 6: stub only, not yet built

core/
  download_engine.py   — yt-dlp wrapper, single-attempt per format
  transcribe_engine.py — Groq Whisper wrapper, auto-chunks large files

ui/
  app.py               — Streamlit UI, live agent log, results display

data/
  audio/               — temp audio files (deleted after transcription)
  exports/             — generated export files

## Key files to understand first
1. agents/base.py — understand the data contracts before touching anything else
2. agents/error_classifier.py — the perception/reasoning layer
3. agents/transcript_agent.py — the most complete agent, reference implementation
4. agents/orchestrator.py — how agents hand off to each other

## How to run locally
cd C:\Users\user\Downloads\yt-agent
venv\Scripts\activate
python -m streamlit run ui/app.py

## IMPORTANT — requirements.txt rule
NEVER run pip freeze > requirements.txt in this project.
pip freeze captures ALL globally installed packages including 
Windows-only packages (pywin32, tensorflow, mediapipe) that 
break Railway Linux builds.

The requirements.txt must only contain these 7 packages:
groq
yt-dlp
python-dotenv
pydub
streamlit
fpdf2
requests

To add a new package: manually add it to requirements.txt with its version.
To find version: pip show package-name

## How to test individual agents
python test_transcript_agent.py "https://www.youtube.com/watch?v=jNQXAC9IVRw"
python test_planner_agent.py
python test_orchestrator.py "https://www.youtube.com/watch?v=jNQXAC9IVRw"

## Environment variables
GROQ_API_KEY              — required, get free at console.groq.com
YOUTUBE_COOKIES           — optional, Netscape cookie format for bot bypass
MAX_VIDEO_DURATION_MINUTES — optional, default 60
WHISPER_MODEL             — optional, default whisper-large-v3-turbo
LLM_MODEL                 — optional, default llama-3.3-70b-versatile

## Railway deployment
- Builder: NIXPACKS
- ffmpeg installed via nixpacks.toml
- PYTHONPATH=/app set in start command
- Start: cd /app && PYTHONPATH=/app python -m streamlit run ui/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
- Health check: /_stcore/health

## Key design decisions
1. Orchestrator built as skeleton first — defines contracts before agents exist
2. Each agent returns a typed dataclass (not dict) — no guessing field names
3. Error classifier separates perception from action — agent decides based on category
4. download_engine has single-attempt function — agent owns the retry loop
5. Orchestrator stops immediately on critical failure — no wasted agent calls
6. ResearchAgent failure is non-fatal — Writer falls back to raw transcript

## What agents currently do when called
- transcript_agent: downloads audio, classifies errors, transcribes
- planner_agent: one LLM call, returns formats_chosen list
- research_agent: one LLM call per format, returns briefs dict
- writer_agent: one LLM call per format using brief, returns drafts dict
- reviewer_agent: raises NotImplementedError (stub — not yet built)
- publisher_agent: raises NotImplementedError (stub — not yet built)
- orchestrator stages 1-4: fully live
- orchestrator stages 5-6: skip silently with log message

## Known issues
- 502 Bad Gateway on Railway — likely PYTHONPATH or import error on startup
- YouTube bot detection on Railway datacenter IP — needs YOUTUBE_COOKIES env var
- ui/app.py uses sys.path.insert() for local dev — may conflict with Railway PYTHONPATH

## Next agents to build
3. ResearchAgent — one Groq LLM call per format, returns brief dict
4. WriterAgent — uses transcript + brief, returns drafts dict
5. ReviewerAgent — scores drafts, revision loop max 2 iterations
6. PublisherAgent — saves to SQLite, generates TXT/PDF/DOCX exports
