import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-large-v3-turbo")


class TranscriptionError(Exception):
    pass


def transcribe_audio(audio_path: str) -> str:
    if not GROQ_API_KEY:
        raise TranscriptionError("GROQ_API_KEY not set.")

    if not os.path.exists(audio_path):
        raise TranscriptionError(f"Audio file not found: {audio_path}")

    size_mb = os.path.getsize(audio_path) / (1024 * 1024)

    if size_mb > 24:
        return _transcribe_large(audio_path)

    client = Groq(api_key=GROQ_API_KEY)
    with open(audio_path, "rb") as f:
        try:
            result = client.audio.transcriptions.create(
                file=(os.path.basename(audio_path), f),
                model=WHISPER_MODEL,
                response_format="text",
                temperature=0.0,
            )
            return str(result).strip()
        except Exception as e:
            raise TranscriptionError(str(e))


def _transcribe_large(audio_path: str) -> str:
    try:
        from pydub import AudioSegment
    except ImportError:
        raise TranscriptionError("pydub required: pip install pydub")

    audio  = AudioSegment.from_mp3(audio_path)
    chunk  = 10 * 60 * 1000
    parts  = [audio[i:i + chunk] for i in range(0, len(audio), chunk)]
    base   = os.path.splitext(audio_path)[0]
    texts  = []

    for i, part in enumerate(parts):
        path = f"{base}_chunk_{i}.mp3"
        part.export(path, format="mp3", bitrate="64k")
        try:
            texts.append(transcribe_audio(path))
        finally:
            if os.path.exists(path):
                os.remove(path)

    return " ".join(texts)
