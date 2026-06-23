import os
import re
from agents.base import (
    PublisherResult,
    StepLog,
    STATUS_SUCCESS,
    STATUS_FAILED,
)
from core.database import init_db, save_video, save_content
from core.export_engine import export_txt, export_pdf, export_docx


class PublisherAgent:

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        init_db()

    def _log(self, msg: str):
        if self.verbose:
            print(f"[PublisherAgent] {msg}")

    def run(
        self,
        video_id:        str,
        youtube_url:     str,
        title:           str,
        channel:         str,
        duration_sec:    int,
        transcript:      str,
        approved_content: dict,
    ) -> PublisherResult:
        result = PublisherResult(status=STATUS_FAILED)

        # Step 1 — Save video to SQLite
        try:
            db_id = save_video(
                youtube_url  = youtube_url,
                youtube_id   = video_id,
                title        = title,
                channel      = channel,
                duration_sec = duration_sec or 0,
                transcript   = transcript or "",
            )
            result.video_db_id = db_id
            result.logs.append(StepLog(
                agent="publisher_agent",
                step="save_video",
                detail=title,
                outcome="success",
                message=f"db_id={db_id}"
            ))
            self._log(f"Video saved to DB: {db_id}")
        except Exception as e:
            result.logs.append(StepLog(
                agent="publisher_agent",
                step="save_video",
                detail=title,
                outcome="error",
                message=str(e)
            ))
            self._log(f"DB save failed: {e}")

        # Step 2 — Save content + export files per format
        exports = {}

        for fmt, content in approved_content.items():
            self._log(f"Publishing {fmt}...")
            fmt_exports = {}
            safe_title  = self._safe_filename(title)
            filename    = f"{safe_title}_{fmt}"

            # Save to SQLite
            try:
                if result.video_db_id:
                    save_content(result.video_db_id, fmt, content)
                    self._log(f"{fmt} saved to DB")
            except Exception as e:
                self._log(f"{fmt} DB save failed: {e}")

            # Export TXT
            try:
                txt_path = export_txt(content, filename)
                fmt_exports["txt"] = txt_path
                self._log(f"{fmt} TXT exported")
            except Exception as e:
                self._log(f"{fmt} TXT failed: {e}")

            # Export PDF
            try:
                pdf_path = export_pdf(content, title, filename)
                fmt_exports["pdf"] = pdf_path
                self._log(f"{fmt} PDF exported")
            except Exception as e:
                self._log(f"{fmt} PDF failed: {e}")

            # Export DOCX
            try:
                docx_path = export_docx(content, title, filename)
                fmt_exports["docx"] = docx_path
                self._log(f"{fmt} DOCX exported")
            except Exception as e:
                self._log(f"{fmt} DOCX failed: {e}")

            exports[fmt] = fmt_exports

            result.logs.append(StepLog(
                agent="publisher_agent",
                step="export_format",
                detail=fmt,
                outcome="success",
                message=f"exports={list(fmt_exports.keys())}"
            ))

        result.exports = exports
        result.status  = STATUS_SUCCESS
        self._log(f"Publishing complete — {len(exports)} formats")
        return result

    def _safe_filename(self, title: str) -> str:
        safe = re.sub(r"[^\w\s-]", "", title)
        safe = re.sub(r"\s+", "_", safe.strip())
        return safe[:40]
