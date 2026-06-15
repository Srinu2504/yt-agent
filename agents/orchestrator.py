import time
from agents.base import (
    OrchestratorResult,
    STATUS_SUCCESS,
    STATUS_FAILED,
)
from agents.transcript_agent import TranscriptAgent
from agents.planner_agent import PlannerAgent


class Orchestrator:

    def __init__(self, verbose: bool = True):
        self.transcript_agent = TranscriptAgent(verbose=verbose)
        self.planner_agent    = PlannerAgent(verbose=verbose)
        self.research_agent   = None
        self.writer_agent     = None
        self.reviewer_agent   = None
        self.publisher_agent  = None
        self.verbose          = verbose

    def _log(self, msg: str):
        if self.verbose:
            print(f"[Orchestrator] {msg}")

    def run(self, url: str) -> OrchestratorResult:
        start_time = time.time()
        result     = OrchestratorResult(status=STATUS_FAILED, url=url)

        self._log(f"Starting pipeline for: {url}")

        # Stage 1 — Transcript
        result = self._run_transcript_stage(result, url)
        if result.status == STATUS_FAILED:
            result.duration_sec = time.time() - start_time
            self._log("Pipeline stopped at transcript stage")
            return result

        # Stage 2 — Planner
        result = self._run_planner_stage(result)
        if result.status == STATUS_FAILED:
            result.duration_sec = time.time() - start_time
            self._log("Pipeline stopped at planner stage")
            return result

        if not result.planner_result.formats_chosen:
            result.status       = "partial"
            result.failed_at_stage = "planner_no_formats"
            result.duration_sec = time.time() - start_time
            self._log("Planner chose no formats — stopping pipeline")
            return result

        # Stages 3-6 — not built yet (placeholders)
        result = self._run_research_stage(result)
        result = self._run_writer_stage(result)
        result = self._run_reviewer_stage(result)
        result = self._run_publisher_stage(result)

        # Mark success if we reached here with transcription + plan
        if result.status != STATUS_FAILED:
            result.status = STATUS_SUCCESS

        result.duration_sec = time.time() - start_time
        self._log(f"Pipeline complete in {result.duration_sec:.1f}s")
        return result

    def _run_transcript_stage(self, result, url):
        self._log("Stage 1 — TranscriptAgent")
        transcript_result = self.transcript_agent.run(url)
        result.transcript_result = transcript_result
        result.full_log.extend(transcript_result.logs)

        if transcript_result.status == STATUS_FAILED:
            result.status          = STATUS_FAILED
            result.failed_at_stage = "transcript"
        else:
            result.status = STATUS_SUCCESS

        return result

    def _run_planner_stage(self, result):
        self._log("Stage 2 — PlannerAgent")
        transcript = result.transcript_result.transcript
        title      = result.transcript_result.title
        duration   = result.transcript_result.duration_sec

        planner_result = self.planner_agent.run(transcript, title, duration)
        result.planner_result = planner_result
        result.full_log.extend(planner_result.logs)

        if planner_result.status == STATUS_FAILED:
            result.status          = STATUS_FAILED
            result.failed_at_stage = "planner"

        return result

    def _run_research_stage(self, result):
        # ResearchAgent not built yet — skip silently
        self._log("Stage 3 — ResearchAgent (not built yet, skipping)")
        return result

    def _run_writer_stage(self, result):
        # WriterAgent not built yet — skip silently
        self._log("Stage 4 — WriterAgent (not built yet, skipping)")
        return result

    def _run_reviewer_stage(self, result):
        # ReviewerAgent not built yet — skip silently
        self._log("Stage 5 — ReviewerAgent (not built yet, skipping)")
        return result

    def _run_publisher_stage(self, result):
        # PublisherAgent not built yet — skip silently
        self._log("Stage 6 — PublisherAgent (not built yet, skipping)")
        return result
