import os
import re
import tempfile
import yt_dlp
from dotenv import load_dotenv

load_dotenv()

MAX_VIDEO_DURATION_MINUTES = int(os.getenv("MAX_VIDEO_DURATION_MINUTES", "60"))
AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)


class DownloadError(Exception):
    pass


def extract_youtube_id(url: str) -> str:
    patterns = [r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})"]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    raise DownloadError(f"Could not extract YouTube ID from: {url}")


def _get_cookies_file():
    content = os.environ.get("YOUTUBE_COOKIES", "").strip()
    if not content:
        return None
    try:
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        )
        tmp.write(content)
        tmp.flush()
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"Cookie file error: {e}")
        return None


def _base_opts() -> tuple:
    cookies_file = _get_cookies_file()
    opts = {
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
        "retries": 2,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        },
    }
    if cookies_file:
        opts["cookiefile"] = cookies_file
    return opts, cookies_file


def get_video_info(url: str) -> dict:
    opts, cookies_file = _base_opts()
    opts["skip_download"] = True
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "id":           info.get("id"),
                "title":        info.get("title", "Unknown"),
                "channel":      info.get("uploader", "Unknown"),
                "duration_sec": info.get("duration") or 0,
            }
    except Exception as e:
        raise DownloadError(str(e))
    finally:
        if cookies_file and os.path.exists(cookies_file):
            os.remove(cookies_file)


def download_audio_attempt(
    url: str,
    video_id: str,
    fmt: str,
    progress_callback=None
) -> str:
    out_path = os.path.join(AUDIO_DIR, f"{video_id}.mp3")
    if os.path.exists(out_path):
        return out_path

    def _hook(d):
        if progress_callback and d["status"] == "downloading":
            pct = d.get("_percent_str", "").strip()
            progress_callback(f"Downloading: {pct}")

    opts, cookies_file = _base_opts()
    opts.update({
        "format": fmt,
        "outtmpl": os.path.join(AUDIO_DIR, f"{video_id}.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "64",
        }],
        "progress_hooks": [_hook],
        "prefer_free_formats": True,
    })

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    except Exception as e:
        raise DownloadError(str(e))
    finally:
        if cookies_file and os.path.exists(cookies_file):
            os.remove(cookies_file)

    if not os.path.exists(out_path):
        raise DownloadError("Audio file not found after download.")

    return out_path
