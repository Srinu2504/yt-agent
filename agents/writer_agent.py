import os
import time
from groq import Groq
from dotenv import load_dotenv

from agents.base import (
    WriterResult,
    StepLog,
    STATUS_SUCCESS,
    STATUS_FAILED,
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL    = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

PROMPTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "prompts"
)

FORMAT_CONFIGS = {
    "linkedin_post": {
        "prompt_file": "linkedin_post.txt",
        "max_tokens":  600,
    },
    "linkedin_article": {
        "prompt_file": "linkedin_article.txt",
        "max_tokens":  2500,
    },
    "twitter_thread": {
        "prompt_file": "twitter_thread.txt",
        "max_tokens":  1200,
    },
    "blog_post": {
        "prompt_file": "blog_post.txt",
        "max_tokens":  3000,
    },
}

NO_BRIEF = "No research brief available — use your best judgment."


class WriterAgent:

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.client  = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

    def _log(self, msg: str):
        if self.verbose:
            print(f"[WriterAgent] {msg}")

    def run(
        self,
        transcript: str,
        title:      str,
        formats_chosen: list,
        briefs:     dict
    ) -> WriterResult:
        result = WriterResult(status=STATUS_FAILED)

        if not GROQ_API_KEY:
            result.error = "GROQ_API_KEY not set."
            return result

        drafts         = {}
        failed_formats = {}

        for fmt in formats_chosen:
            self._log(f"Writing {fmt}...")
            config = FORMAT_CONFIGS.get(fmt)

            if not config:
                failed_formats[fmt] = f"Unknown format: {fmt}"
                self._log(f"Unknown format: {fmt} — skipping")
                continue

            brief = briefs.get(fmt, NO_BRIEF)
            draft = self._write_format(
                fmt       = fmt,
                transcript = transcript,
                title      = title,
                brief      = brief,
                config     = config,
            )

            if draft is not None:
                drafts[fmt] = draft
                result.logs.append(StepLog(
                    agent="writer_agent",
                    step="write_format",
                    detail=fmt,
                    outcome="success",
                    message=f"{len(draft.split())} words"
                ))
                self._log(f"{fmt} done — {len(draft.split())} words")
            else:
                failed_formats[fmt] = "Generation failed after 3 attempts"
                result.logs.append(StepLog(
                    agent="writer_agent",
                    step="write_format",
                    detail=fmt,
                    outcome="error",
                    message="Failed after 3 attempts"
                ))
                self._log(f"{fmt} failed — continuing to next format")

        result.drafts         = drafts
        result.failed_formats = failed_formats

        if drafts:
            result.status = STATUS_SUCCESS
        else:
            result.status = STATUS_FAILED
            result.error  = "All formats failed to generate."

        return result

    def _write_format(
        self,
        fmt:        str,
        transcript: str,
        title:      str,
        brief:      str,
        config:     dict,
    ):
        prompt_path = os.path.join(PROMPTS_DIR, config["prompt_file"])

        try:
            with open(prompt_path, encoding="utf-8") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            self._log(f"Prompt file not found: {prompt_path}")
            return None

        system_prompt = system_prompt.replace("{brief}", brief)

        user_message = (
            f"Video title: {title}\n\n"
            f"Transcript:\n{self._truncate(transcript)}"
        )

        for attempt in range(1, 4):
            try:
                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_message},
                    ],
                    max_tokens=config["max_tokens"],
                    temperature=0.7,
                )
                return response.choices[0].message.content.strip()

            except Exception as e:
                self._log(f"{fmt} attempt {attempt} failed: {e}")
                if "429" in str(e) or "rate limit" in str(e).lower():
                    wait = 2 ** attempt
                    self._log(f"Rate limited — waiting {wait}s")
                    time.sleep(wait)
                    continue
                if "401" in str(e):
                    self._log("Invalid API key — stopping")
                    return None
                if attempt == 3:
                    return None

        return None

    def _truncate(self, transcript: str, max_chars: int = 12000) -> str:
        if len(transcript) <= max_chars:
            return transcript
        front = int(max_chars * 0.8)
        back  = max_chars - front
        return (
            transcript[:front]
            + "\n\n[...middle section omitted...]\n\n"
            + transcript[-back:]
        )
