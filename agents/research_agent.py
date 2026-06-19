import os
import time
from groq import Groq
from dotenv import load_dotenv

from agents.base import (
    ResearchResult,
    StepLog,
    STATUS_SUCCESS,
    STATUS_FAILED,
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL    = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """You are a content strategist who finds the best angle 
for a specific content format.

Given a video transcript and a target format, return a research brief 
in this exact JSON structure:
{
  "hook": "the single best opening line or angle for this format",
  "insight": "the most compelling insight from the transcript",
  "tone": "the right tone for this format and audience",
  "angle": "one sentence describing the overall approach"
}

Rules:
- Be specific — reference actual content from the transcript
- Keep each field under 100 characters
- Return ONLY valid JSON. No explanation outside the JSON.
"""

FORMAT_DESCRIPTIONS = {
    "linkedin_post":    "a short LinkedIn post (max 1300 chars) for professionals",
    "linkedin_article": "a long-form LinkedIn article (1000-1500 words) for thought leadership",
    "twitter_thread":   "a Twitter/X thread with 8-10 numbered tweets for viral sharing",
    "blog_post":        "an SEO-friendly blog post (1200-1800 words) for general readers",
}


class ResearchAgent:

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def _log(self, msg: str):
        if self.verbose:
            print(f"[ResearchAgent] {msg}")

    def run(
        self,
        transcript: str,
        formats_chosen: list
    ) -> ResearchResult:
        result = ResearchResult(status=STATUS_FAILED)

        if not GROQ_API_KEY:
            result.error = "GROQ_API_KEY not set."
            return result

        if not formats_chosen:
            result.status = STATUS_SUCCESS
            result.briefs = {}
            return result

        briefs = {}

        for fmt in formats_chosen:
            self._log(f"Researching angle for: {fmt}")
            brief = self._research_format(fmt, transcript)

            if brief is not None:
                briefs[fmt] = brief
                result.logs.append(StepLog(
                    agent="research_agent",
                    step="research_format",
                    detail=fmt,
                    outcome="success",
                    message=brief[:80]
                ))
            else:
                result.logs.append(StepLog(
                    agent="research_agent",
                    step="research_format",
                    detail=fmt,
                    outcome="error",
                    message="Could not generate brief"
                ))
                self._log(f"Research failed for {fmt} — Writer will use raw transcript")

        result.briefs = briefs

        if briefs:
            result.status = STATUS_SUCCESS
        else:
            result.status  = STATUS_FAILED
            result.error   = "Research failed for all formats."

        return result

    def _research_format(self, fmt: str, transcript: str) -> str | None:
        fmt_desc = FORMAT_DESCRIPTIONS.get(fmt, fmt)
        user_msg = (
            f"Format: {fmt_desc}\n\n"
            f"Transcript:\n{transcript[:6000]}"
        )

        for attempt in range(1, 4):
            try:
                client   = Groq(api_key=GROQ_API_KEY)
                response = client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": user_msg},
                    ],
                    max_tokens=300,
                    temperature=0.3,
                )

                raw    = response.choices[0].message.content.strip()
                parsed = self._parse_brief(raw)

                if parsed:
                    brief = (
                        f"Hook: {parsed.get('hook', '')}\n"
                        f"Insight: {parsed.get('insight', '')}\n"
                        f"Tone: {parsed.get('tone', '')}\n"
                        f"Angle: {parsed.get('angle', '')}"
                    )
                    self._log(f"{fmt} brief: {parsed.get('angle', '')}")
                    return brief

            except Exception as e:
                self._log(f"{fmt} attempt {attempt} failed: {e}")
                if "429" in str(e) or "rate limit" in str(e).lower():
                    wait = 2 ** attempt
                    self._log(f"Rate limited — waiting {wait}s")
                    time.sleep(wait)
                    continue
                if attempt == 3:
                    return None

        return None

    def _parse_brief(self, raw: str):
        import json, re
        raw = raw.strip()
        if raw.startswith("```"):
            lines = [l for l in raw.split("\n") if not l.startswith("```")]
            raw   = "\n".join(lines).strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    return None
        return None
