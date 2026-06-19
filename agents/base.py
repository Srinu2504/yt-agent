from dataclasses import dataclass, field
from typing import Optional, List

STATUS_SUCCESS = "success"
STATUS_FAILED  = "failed"
STATUS_SKIPPED = "skipped"

@dataclass
class StepLog:
    agent: str
    step: str
    detail: str
    outcome: str
    error_type: Optional[str] = None
    message: Optional[str] = None

@dataclass
class TranscriptResult:
    status: str
    url: str
    video_id: Optional[str]    = None
    title: Optional[str]       = None
    channel: Optional[str]     = None
    duration_sec: Optional[int] = None
    transcript: Optional[str]  = None
    word_count: int            = 0
    error: Optional[str]       = None
    logs: List[StepLog]        = field(default_factory=list)

@dataclass
class PlannerResult:
    status: str
    formats_chosen: List[str]  = field(default_factory=list)
    reasoning: Optional[str]   = None
    error: Optional[str]       = None
    logs: List[StepLog]        = field(default_factory=list)

@dataclass
class ResearchResult:
    status: str
    briefs: dict               = field(default_factory=dict)
    error: Optional[str]       = None
    logs: List[StepLog]        = field(default_factory=list)

@dataclass
class WriterResult:
    status: str
    drafts: dict               = field(default_factory=dict)
    failed_formats: dict       = field(default_factory=dict)
    error: Optional[str]       = None
    logs: List[StepLog]        = field(default_factory=list)

@dataclass
class ReviewResult:
    status: str
    approved: dict             = field(default_factory=dict)
    revision_counts: dict      = field(default_factory=dict)
    error: Optional[str]       = None
    logs: List[StepLog]        = field(default_factory=list)

@dataclass
class PublisherResult:
    status: str
    video_db_id: Optional[str] = None
    exports: dict              = field(default_factory=dict)
    error: Optional[str]       = None
    logs: List[StepLog]        = field(default_factory=list)

@dataclass
class OrchestratorResult:
    status: str
    url: str
    transcript_result: Optional[TranscriptResult] = None
    planner_result:    Optional[PlannerResult]    = None
    research_result:   Optional[ResearchResult]   = None
    writer_result:     Optional[WriterResult]     = None
    review_result:     Optional[ReviewResult]     = None
    publisher_result:  Optional[PublisherResult]  = None
    approved_content:  dict                       = field(default_factory=dict)
    failed_at_stage:   Optional[str]              = None
    full_log:          List[StepLog]              = field(default_factory=list)
    duration_sec:      Optional[float]            = None
