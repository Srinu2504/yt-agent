import os
import time
import json
import re
from groq import Groq
from dotenv import load_dotenv

from agents.base import (
    ReviewResult,
    StepLog,
    STATUS_SUCCESS,
    STATUS_FAILED,
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL    = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

MAX_REVISIONS = 2


# ── Scoring rules per format ──────────────────────────────────────────────────

RULES = {
    "linkedin_post": {
        "max_chars":     1300,
        "min_words":     30,
        "needs_hashtags": True,
        "filler_phrases": [
            "in today's world", "it's no secret", "dive deep",
            "in this post", "i watched", "in this video"
        ],
    },
    "twitter_thread": {
        "max_tweet_chars": 280,
        "min_tweets":      3,
        "needs_numbering": True,
    },
    "linkedin_article": {
        "min_words":      400,
        "needs_headings": True,
    },
    "blog_post": {
        "min_words":      500,
        "needs_headings": True,
        "needs_title":    True,
    },
}

REVIEW_SYSTEM_PROMPT = """You are a strict content quality reviewer.

Given a piece of content and its format, evaluate if it meets quality standards.

Return ONLY this JSON:
{
  "passed": true or false,
  "score": 1-10,
  "feedback": "specific one-sentence fix if failed, empty string if passed"
}

Be strict but fair. Focus on:
- Hook quality (first line must grab attention)
- Clarity and readability
- Appropriate tone for platform
- No generic filler phrases

Return ONLY valid JSON. No explanation outside JSON.
"""


class ReviewerAgent:

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.client  = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

    def _log(self, msg: str):
        if self.verbose:
            print(f"[ReviewerAgent] {msg}")

    def run(
        self,
        drafts: dict,
        formats_chosen: list
    ) -> ReviewResult:
        result = ReviewResult(status=STATUS_FAILED)

        if not drafts:
            result.error = "No drafts to review."
            return result

        approved        = {}
        revision_counts = {}
        warnings        = {}

        for fmt in formats_chosen:
            if fmt not in drafts:
                self._log(f"{fmt} — no draft found, skipping")
                continue

            draft = drafts[fmt]
            self._log(f"Reviewing {fmt}...")

            final_draft, revisions, warning = self._review_format(
                fmt, draft
            )

            approved[fmt]        = final_draft
            revision_counts[fmt] = revisions
            if warning:
                warnings[fmt] = warning

            result.logs.append(StepLog(
                agent="reviewer_agent",
                step="review_format",
                detail=fmt,
                outcome="success",
                message=f"revisions={revisions} warning={bool(warning)}"
            ))

        result.approved        = approved
        result.revision_counts = revision_counts
        result.warnings        = warnings
        result.status          = STATUS_SUCCESS if approved else STATUS_FAILED

        if not approved:
            result.error = "No formats were approved."

        return result

    # ── Core review loop ──────────────────────────────────────────────────────

    def _review_format(self, fmt: str, draft: str):
        revisions = 0
        warning   = ""

        for attempt in range(MAX_REVISIONS):
            # Step 1 — Python rule checks (fast, free)
            rule_issues = self._check_rules(fmt, draft)

            if rule_issues:
                self._log(f"{fmt} rule issues: {rule_issues}")
                if attempt < MAX_REVISIONS - 1:
                    draft     = self._request_revision(fmt, draft, rule_issues)
                    revisions += 1
                    continue
                else:
                    warning = f"Rule issues after {MAX_REVISIONS} attempts: {rule_issues}"
                    break

            # Step 2 — LLM quality check (one call)
            llm_result = self._llm_review(fmt, draft)

            if llm_result and not llm_result.get("passed", True):
                feedback = llm_result.get("feedback", "")
                self._log(f"{fmt} LLM feedback: {feedback}")

                if attempt < MAX_REVISIONS - 1 and feedback:
                    draft     = self._request_revision(fmt, draft, feedback)
                    revisions += 1
                    continue
                else:
                    warning = f"Quality warning: {feedback}"
                    break
            else:
                self._log(f"{fmt} approved ✅ (revisions={revisions})")
                break

        return draft, revisions, warning

    # ── Python rule checks ────────────────────────────────────────────────────

    def _check_rules(self, fmt: str, draft: str) -> str:
        rules  = RULES.get(fmt, {})
        issues = []

        if "max_chars" in rules:
            if len(draft) > rules["max_chars"]:
                issues.append(
                    f"Too long: {len(draft)} chars (max {rules['max_chars']})"
                )

        if "min_words" in rules:
            words = len(draft.split())
            if words < rules["min_words"]:
                issues.append(
                    f"Too short: {words} words (min {rules['min_words']})"
                )

        if "needs_hashtags" in rules and rules["needs_hashtags"]:
            if "#" not in draft:
                issues.append("Missing hashtags")

        if "filler_phrases" in rules:
            draft_lower = draft.lower()
            for phrase in rules["filler_phrases"]:
                if phrase in draft_lower:
                    issues.append(f"Contains filler phrase: '{phrase}'")
                    break

        if "needs_numbering" in rules and rules["needs_numbering"]:
            if "1/" not in draft and "1." not in draft:
                issues.append("Missing tweet numbering (1/ or 1.)")

        if "max_tweet_chars" in rules:
            tweets = [t.strip() for t in draft.split("\n") if t.strip()]
            for i, tweet in enumerate(tweets):
                if len(tweet) > rules["max_tweet_chars"]:
                    issues.append(
                        f"Tweet {i+1} too long: {len(tweet)} chars"
                    )
                    break

        if "min_tweets" in rules:
            tweets = [t.strip() for t in draft.split("\n") if t.strip()]
            if len(tweets) < rules["min_tweets"]:
                issues.append(
                    f"Too few tweets: {len(tweets)} (min {rules['min_tweets']})"
                )

        if "needs_headings" in rules and rules["needs_headings"]:
            if "##" not in draft:
                issues.append("Missing ## section headings")

        if "needs_title" in rules and rules["needs_title"]:
            if not draft.strip().startswith("#"):
                issues.append("Missing # title at start")

        return "; ".join(issues)

    # ── LLM quality check ─────────────────────────────────────────────────────

    def _llm_review(self, fmt: str, draft: str):
        if not self.client:
            return None

        user_msg = (
            f"Format: {fmt}\n\n"
            f"Content to review:\n{draft[:2000]}"
        )

        for attempt in range(1, 3):
            try:
                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
                        {"role": "user",   "content": user_msg},
                    ],
                    max_tokens=150,
                    temperature=0.0,
                )
                raw    = response.choices[0].message.content.strip()
                parsed = self._parse_json(raw)
                return parsed

            except Exception as e:
                self._log(f"LLM review attempt {attempt} failed: {e}")
                if "429" in str(e) or "rate limit" in str(e).lower():
                    time.sleep(2 ** attempt)
                    continue
                return None

        return None

    # ── Revision request ──────────────────────────────────────────────────────

    def _request_revision(self, fmt: str, draft: str, feedback: str) -> str:
        if not self.client:
            return draft

        self._log(f"Requesting revision for {fmt}: {feedback}")

        system = (
            f"You are a content editor. Fix the following {fmt} based on "
            f"this specific feedback: {feedback}\n\n"
            f"Return ONLY the revised content. No explanation."
        )

        for attempt in range(1, 3):
            try:
                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user",   "content": draft},
                    ],
                    max_tokens=1500,
                    temperature=0.5,
                )
                revised = response.choices[0].message.content.strip()
                if revised:
                    self._log(f"Revision received: {len(revised.split())} words")
                    return revised
            except Exception as e:
                self._log(f"Revision attempt {attempt} failed: {e}")
                if "429" in str(e) or "rate limit" in str(e).lower():
                    time.sleep(2 ** attempt)
                    continue

        return draft

    # ── JSON parser ───────────────────────────────────────────────────────────

    def _parse_json(self, raw: str):
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
