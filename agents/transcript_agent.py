import os
import time

from agents.base import (
    TranscriptResult,
    StepLog,
    STATUS_SUCCESS,
    STATUS_FAILED,
)
from agents.error_classifier import (
    classify,
    ErrorType,
    USER_MESSAGES,
    UNRECOVERABLE,
    RETRYABLE_WITH_BACKOFF,
)
from core.download_engine import (
    extract_youtube_id,
    get_video_info,
    download_audio_attempt,
    DownloadError,
)
from core.transcribe_engine import (
    transcribe_audio,
    TranscriptionError,
)

AUDIO_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "audio"
)

FORMAT_CANDIDATES = [
    "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best",
    "bestaudio/best",
    "worstaudio/bestaudio/best",
    "best",
]


class TranscriptAgent:

    def __init__(self, max_retries: int = 3, verbose: bool = True):
        self.max_retries = max_retries
        self.verbose     = verbose

    def _log(self, msg: str):
        if self.verbose:
            print(f"[TranscriptAgent] {msg}")

    def run(self, url: str) -> TranscriptResult:
        result = TranscriptResult(status=STATUS_FAILED, url=url)

        # Stage A — extract video ID
        try:
            video_id      = extract_youtube_id(url)
            result.video_id = video_id
            result.logs.append(StepLog(
                agent="transcript_agent", step="extract_id",
                detail=url, outcome="success"
            ))
        except DownloadError as e:
            result.logs.append(StepLog(
                agent="transcript_agent", step="extract_id",
                detail=url, outcome="error", message=str(e)
            ))
            result.error = str(e)
            return result

        # Stage B — fetch video metadata
        info = self._fetch_info(result, url)
        if info is None:
            return result

        result.title        = info["title"]
        result.channel      = info["channel"]
        result.duration_sec = info["duration_sec"]

        from core.download_engine import MAX_VIDEO_DURATION_MINUTES
        if info["duration_sec"] / 60 > MAX_VIDEO_DURATION_MINUTES:
            msg = (
                f"Video is {info['duration_sec']//60} min. "
                f"Max: {MAX_VIDEO_DURATION_MINUTES} min."
            )
            result.error = msg
            result.logs.append(StepLog(
                agent="transcript_agent", step="duration_check",
                detail=msg, outcome="error",
                error_type=ErrorType.DURATION_EXCEEDED.value
            ))
            return result

        # Stage C — download audio
        audio_path = self._download(result, url, video_id)
        if audio_path is None:
            return result

        # Stage D — transcribe
        transcript = self._transcribe(result, audio_path)
        if transcript is None:
            return result

        # Clean up audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)

        result.status     = STATUS_SUCCESS
        result.transcript = transcript
        result.word_count = len(transcript.split())
        self._log(f"Done — {result.word_count} words")
        return result

    # ── Stage B ───────────────────────────────────────────────────────

    def _fetch_info(self, result: TranscriptResult, url: str):
        for attempt in range(1, self.max_retries + 1):
            try:
                self._log(f"Fetching info attempt {attempt}")
                info = get_video_info(url)
                result.logs.append(StepLog(
                    agent="transcript_agent", step="fetch_info",
                    detail=f"attempt {attempt}", outcome="success"
                ))
                return info
            except DownloadError as e:
                err_type = classify(str(e))
                result.logs.append(StepLog(
                    agent="transcript_agent", step="fetch_info",
                    detail=f"attempt {attempt}", outcome="error",
                    error_type=err_type.value, message=str(e)
                ))
                self._log(f"fetch_info error: {err_type.value}")

                if err_type in UNRECOVERABLE:
                    result.error = USER_MESSAGES[err_type]
                    return None

                if err_type in RETRYABLE_WITH_BACKOFF and attempt < self.max_retries:
                    wait = 2 ** attempt
                    self._log(f"Backing off {wait}s")
                    time.sleep(wait)
                    continue

                result.error = USER_MESSAGES.get(err_type, str(e))
                return None

        result.error = "Fetch info failed after max retries."
        return None

    # ── Stage C ───────────────────────────────────────────────────────

    def _download(self, result: TranscriptResult, url: str, video_id: str):
        out_path = os.path.join(AUDIO_DIR, f"{video_id}.mp3")
        if os.path.exists(out_path):
            result.logs.append(StepLog(
                agent="transcript_agent", step="download",
                detail="cached", outcome="success"
            ))
            return out_path

        for fmt in FORMAT_CANDIDATES:
            for attempt in range(1, self.max_retries + 1):
                try:
                    self._log(f"Download fmt='{fmt}' attempt {attempt}")
                    path = download_audio_attempt(url, video_id, fmt)
                    result.logs.append(StepLog(
                        agent="transcript_agent", step="download",
                        detail=fmt, outcome="success"
                    ))
                    return path

                except DownloadError as e:
                    err_type = classify(str(e))
                    result.logs.append(StepLog(
                        agent="transcript_agent", step="download",
                        detail=f"{fmt} attempt {attempt}",
                        outcome="error",
                        error_type=err_type.value,
                        message=str(e)
                    ))
                    self._log(f"Download error: {err_type.value}")

                    if err_type in UNRECOVERABLE:
                        result.error = USER_MESSAGES[err_type]
                        return None

                    if err_type in RETRYABLE_WITH_BACKOFF and attempt < self.max_retries:
                        wait = 2 ** attempt
                        self._log(f"Backing off {wait}s")
                        time.sleep(wait)
                        continue

                    break  # try next format

        result.error = "All audio formats failed."
        return None

    # ── Stage D ───────────────────────────────────────────────────────

    def _transcribe(self, result: TranscriptResult, audio_path: str):
        for attempt in range(1, self.max_retries + 1):
            try:
                self._log(f"Transcribing attempt {attempt}")
                text = transcribe_audio(audio_path)
                result.logs.append(StepLog(
                    agent="transcript_agent", step="transcribe",
                    detail=f"attempt {attempt}", outcome="success"
                ))
                return text
            except TranscriptionError as e:
                err_type = classify(str(e))
                result.logs.append(StepLog(
                    agent="transcript_agent", step="transcribe",
                    detail=f"attempt {attempt}", outcome="error",
                    error_type=err_type.value, message=str(e)
                ))
                self._log(f"Transcribe error: {err_type.value}")

                if err_type in RETRYABLE_WITH_BACKOFF and attempt < self.max_retries:
                    wait = 2 ** attempt
                    self._log(f"Backing off {wait}s")
                    time.sleep(wait)
                    continue

                result.error = USER_MESSAGES.get(err_type, str(e))
                return None

        result.error = "Transcription failed after max retries."
        return None
