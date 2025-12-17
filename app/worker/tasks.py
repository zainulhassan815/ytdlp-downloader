import logging
import os
import uuid

from celery import Task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from yt_dlp import YoutubeDL

from app.config import settings
from app.db.models import Download
from app.models import DownloadStatus
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)

# Sync database URL for Celery (uses psycopg2)
database_url = settings.database_url
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

sync_engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=sync_engine)


class DownloadTask(Task):
    """Base task with database session management."""

    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


class YtDlpLogger:
    """Custom logger for yt-dlp."""

    def debug(self, msg):
        if msg.startswith("[debug] "):
            logger.debug(msg)
        else:
            self.info(msg)

    def info(self, msg):
        logger.info(msg)

    def warning(self, msg):
        logger.warning(msg)

    def error(self, msg):
        logger.error(msg)


def update_download_status(
    db_session,
    download_id: uuid.UUID,
    status: str,
    progress: float = None,
    filename: str = None,
    file_path: str = None,
    file_size: int = None,
    error_message: str = None,
):
    """Update download record in database."""
    download = db_session.query(Download).filter(Download.id == download_id).first()
    if download:
        download.status = status
        if progress is not None:
            download.progress = progress
        if filename is not None:
            download.filename = filename
        if file_path is not None:
            download.file_path = file_path
        if file_size is not None:
            download.file_size = file_size
        if error_message is not None:
            download.error_message = error_message
        db_session.commit()


@celery_app.task(bind=True, base=DownloadTask, name="download_video")
def download_video(self, download_id: str, url: str):
    """Download a video using yt-dlp."""
    download_uuid = uuid.UUID(download_id)
    db = self.db

    # Update status to InProgress
    update_download_status(db, download_uuid, DownloadStatus.InProgress, progress=0.0)

    # Ensure download directory exists
    os.makedirs(settings.download_dir, exist_ok=True)

    # Track progress
    def progress_hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            if total > 0:
                progress = (downloaded / total) * 100
                update_download_status(
                    db, download_uuid, DownloadStatus.InProgress, progress=progress
                )
        elif d["status"] == "finished":
            update_download_status(
                db, download_uuid, DownloadStatus.InProgress, progress=100.0
            )

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
        "outtmpl": os.path.join(settings.download_dir, "%(title)s.%(ext)s"),
        "progress_hooks": [progress_hook],
        "logger": YtDlpLogger(),
        "noplaylist": True,
        "merge_output_format": "mp4",
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        ],
        # Use ios client to work around YouTube SABR streaming restrictions
        "extractor_args": {
            "youtube": {
                "player_client": ["ios", "web"],
            }
        },
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # Extract info and download
            info = ydl.extract_info(url, download=True)

            # Get the final filename after any post-processing
            if info:
                filename = ydl.prepare_filename(info)
                # Handle potential extension change from post-processing
                base, _ = os.path.splitext(filename)
                final_filename = f"{base}.mp4"
                if not os.path.exists(final_filename):
                    final_filename = filename

                file_size = (
                    os.path.getsize(final_filename)
                    if os.path.exists(final_filename)
                    else None
                )

                # Update to completed
                update_download_status(
                    db,
                    download_uuid,
                    DownloadStatus.Completed,
                    progress=100.0,
                    filename=os.path.basename(final_filename),
                    file_path=final_filename,
                    file_size=file_size,
                )

                return {
                    "status": "completed",
                    "download_id": download_id,
                    "filename": os.path.basename(final_filename),
                    "file_path": final_filename,
                }

    except Exception as e:
        logger.exception(f"Download failed for {url}")
        update_download_status(
            db,
            download_uuid,
            DownloadStatus.Failed,
            error_message=str(e),
        )
        raise
