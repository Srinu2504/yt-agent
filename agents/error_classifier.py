from enum import Enum


class ErrorType(str, Enum):
    BOT_DETECTED      = "bot_detected"
    FORMAT_ERROR      = "format_error"
    RATE_LIMIT        = "rate_limit"
    VIDEO_UNAVAILABLE = "video_unavailable"
    NETWORK_ERROR     = "network_error"
    FFMPEG_ERROR      = "ffmpeg_error"
    DURATION_EXCEEDED = "duration_exceeded"
    UNKNOWN           = "unknown"


def classify(error_msg: str) -> ErrorType:
    msg = error_msg.lower()

    if "sign in" in msg or "confirm you're not a bot" in msg or "sign in to confirm" in msg:
        return ErrorType.BOT_DETECTED

    if (
        "requested format is not available" in msg
        or "no video formats" in msg
        or "no formats found" in msg
    ):
        return ErrorType.FORMAT_ERROR

    if "429" in msg or "rate limit" in msg or "too many requests" in msg:
        return ErrorType.RATE_LIMIT

    if any(s in msg for s in [
        "video unavailable", "private video",
        "this video is not available",
        "video has been removed"
    ]):
        return ErrorType.VIDEO_UNAVAILABLE

    if "ffmpeg" in msg or "ffprobe" in msg:
        return ErrorType.FFMPEG_ERROR

    if any(s in msg for s in [
        "timed out", "connection", "network", "resolve host"
    ]):
        return ErrorType.NETWORK_ERROR

    if "duration" in msg or "max allowed" in msg:
        return ErrorType.DURATION_EXCEEDED

    return ErrorType.UNKNOWN


USER_MESSAGES = {
    ErrorType.BOT_DETECTED: (
        "YouTube blocked this request as a bot. "
        "Fix: update YOUTUBE_COOKIES in Railway Variables "
        "with fresh cookies from Chrome on youtube.com."
    ),
    ErrorType.FORMAT_ERROR: (
        "No compatible audio format found for this video "
        "after trying all known formats."
    ),
    ErrorType.RATE_LIMIT: (
        "Rate limited. The agent waited and retried "
        "but the limit persisted. Try again in a few minutes."
    ),
    ErrorType.VIDEO_UNAVAILABLE: (
        "This video is private, deleted, or region-restricted. "
        "It cannot be downloaded."
    ),
    ErrorType.FFMPEG_ERROR: (
        "Audio processing failed — ffmpeg is missing or broken."
    ),
    ErrorType.NETWORK_ERROR: (
        "Network error reaching YouTube or Groq. "
        "Check internet and try again."
    ),
    ErrorType.DURATION_EXCEEDED: (
        "Video exceeds the maximum duration limit."
    ),
    ErrorType.UNKNOWN: (
        "An unexpected error occurred."
    ),
}

RETRYABLE_WITH_BACKOFF = {
    ErrorType.RATE_LIMIT,
    ErrorType.NETWORK_ERROR,
}

RETRYABLE_FOR_FORMAT = {
    ErrorType.FORMAT_ERROR,
    ErrorType.UNKNOWN,
}

UNRECOVERABLE = {
    ErrorType.BOT_DETECTED,
    ErrorType.VIDEO_UNAVAILABLE,
    ErrorType.DURATION_EXCEEDED,
    ErrorType.FFMPEG_ERROR,
}
