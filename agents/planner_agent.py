import os
import json
import time
from groq import Groq
from dotenv import load_dotenv

from agents.base import (
    PlannerResult,
    StepLog,
    STATUS_SUCCESS,
    STATUS_FAILED,
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL    = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

ALL_FORMATS = [
    "linkedin_post",
    "linkedin_article",
    "twitter_thread",
    "blog_post",
]

SYSTEM_PROMPT = """You are a content strategist who decides which content 
formats are worth creating from a YouTube video transcript.

Given a transcript, video title, and duration, return a JSON object with:
{
  "formats_chosen": ["format1", "format2"],
  "reasoning": "one sentence explaining why"
}

Available formats: linkedin_post, linkedin_article, twitter_thread, blog_post

Rules:
- linkedin_post: always include if transcript has any useful insight
- twitter_thread: include if content has multiple distinct points
- linkedin_article: only if video is over 3 minutes AND has depth
- blog_post: only if video is over 5 minutes AND is educational/tutorial
- If transcript has no useful content (music, silence, gibberish): 
  return empty formats_chosen list
- Return ONLY valid JSON. No explanation outside the JSON.
"""


class PlannerAgent:

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.client  = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

    def _log(self, msg: str):
        if self.verbose:
            print(f"[PlannerAgent] {msg}")

    def run(
        self,
        transcript: str,
        title: str,
        duration_sec: int
    ) -> PlannerResult:
        result = PlannerResult(status=STATUS_FAILED)

        if not GROQ_API_KEY:
            result.error = "GROQ_API_KEY not set."
            return result

        duration_min = duration_sec / 60

        user_message = (
            f"Video title: {title}\n"
            f"Duration: {duration_min:.1f} minutes\n\n"
            f"Transcript:\n{transcript[:8000]}"
        )

        self._log(f"Planning formats for: {title} ({duration_min:.1f} min)")

        for attempt in range(1, 4):
            try:
                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": user_message},
                    ],
                    max_tokens=256,
                    temperature=0.0,
                )

                raw = response.choices[0].message.content.strip()
                self._log(f"LLM raw response: {raw}")

                parsed = self._parse_response(raw)

                if parsed is None:
                    raise ValueError(f"Could not parse JSON from: {raw}")

                formats_chosen = [
                    f for f in parsed.get("formats_chosen", [])
                    if f in ALL_FORMATS
                ]
                reasoning = parsed.get("reasoning", "")

                result.status         = STATUS_SUCCESS
                result.formats_chosen = formats_chosen
                result.reasoning      = reasoning
                result.logs.append(StepLog(
                    agent="planner_agent",
                    step="plan_formats",
                    detail=f"attempt {attempt}",
                    outcome="success",
                    message=f"chose: {formats_chosen}"
                ))

                self._log(f"Chose: {formats_chosen}")
                self._log(f"Reason: {reasoning}")
                return result

            except Exception as e:
                self._log(f"Attempt {attempt} failed: {e}")
                result.logs.append(StepLog(
                    agent="planner_agent",
                    step="plan_formats",
                    detail=f"attempt {attempt}",
                    outcome="error",
                    message=str(e)
                ))

                if attempt < 3:
                    time.sleep(2 ** attempt)
                    continue

        result.error = "PlannerAgent failed after 3 attempts."
        return result

    def _parse_response(self, raw: str):
        raw = raw.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            lines = raw.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            raw = "\n".join(lines).strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON object from text
            import re
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    return None
        return None
