import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Download
from app.models import DownloadStatus
from app.worker.tasks import download_video


class DownloadService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_download(self, url: str) -> Download:
        """Create a new download record and queue the task."""
        download = Download(
            url=url,
            status=DownloadStatus.Queued,
            progress=0.0,
        )
        self.db.add(download)
        await self.db.commit()
        await self.db.refresh(download)

        # Queue the Celery task
        task = download_video.delay(str(download.id), url)

        # Store the Celery task ID
        download.celery_task_id = task.id
        await self.db.commit()

        return download

    async def get_download(self, download_id: uuid.UUID) -> Download | None:
        """Get a download by ID."""
        result = await self.db.execute(
            select(Download).where(Download.id == download_id)
        )
        return result.scalar_one_or_none()

    async def cancel_download(self, download_id: uuid.UUID) -> bool:
        """Cancel a download."""
        download = await self.get_download(download_id)
        if not download:
            return False

        # Can only cancel queued or in-progress downloads
        if download.status not in [DownloadStatus.Queued, DownloadStatus.InProgress]:
            return False

        # Revoke the Celery task if it exists
        if download.celery_task_id:
            from app.worker.celery_app import celery_app

            celery_app.control.revoke(download.celery_task_id, terminate=True)

        download.status = DownloadStatus.Cancelled
        await self.db.commit()

        return True

    async def list_downloads(self, limit: int = 50, offset: int = 0) -> list[Download]:
        """List all downloads with pagination."""
        result = await self.db.execute(
            select(Download)
            .order_by(Download.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
