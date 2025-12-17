from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import DownloadStatus
from app.services.download_service import DownloadService


class DownloadRequest(BaseModel):
    url: HttpUrl


class DownloadResponse(BaseModel):
    id: UUID
    url: str
    status: DownloadStatus

    model_config = {"from_attributes": True}


class DownloadProgressResponse(BaseModel):
    id: UUID
    url: str
    filename: str | None
    status: DownloadStatus
    progress: float
    error_message: str | None = None

    model_config = {"from_attributes": True}


class CancelResponse(BaseModel):
    success: bool
    message: str


downloads_router = APIRouter(prefix="/downloads", tags=["downloads"])


@downloads_router.post("", response_model=DownloadResponse)
async def create_download(
    request: DownloadRequest,
    db: AsyncSession = Depends(get_db),
) -> DownloadResponse:
    """Start a new video download.

    Args:
        request: The download request containing the video URL.

    Returns:
        DownloadResponse: The created download with its ID.
    """
    service = DownloadService(db)
    download = await service.create_download(str(request.url))
    return DownloadResponse.model_validate(download)


@downloads_router.get("/{download_id}", response_model=DownloadProgressResponse)
async def get_download_progress(
    download_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> DownloadProgressResponse:
    """Get the progress of a download.

    Args:
        download_id: The UUID of the download.

    Returns:
        DownloadProgressResponse: The current progress of the download.
    """
    service = DownloadService(db)
    download = await service.get_download(download_id)
    if not download:
        raise HTTPException(status_code=404, detail="Download not found")
    return DownloadProgressResponse.model_validate(download)


@downloads_router.post("/{download_id}/cancel", response_model=CancelResponse)
async def cancel_download(
    download_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> CancelResponse:
    """Cancel a download.

    Args:
        download_id: The UUID of the download.

    Returns:
        CancelResponse: Whether the cancellation was successful.
    """
    service = DownloadService(db)
    success = await service.cancel_download(download_id)
    if success:
        return CancelResponse(success=True, message="Download cancelled successfully")
    return CancelResponse(success=False, message="Could not cancel download")


@downloads_router.get("", response_model=list[DownloadProgressResponse])
async def list_downloads(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> list[DownloadProgressResponse]:
    """List all downloads with pagination.

    Args:
        limit: Maximum number of downloads to return.
        offset: Number of downloads to skip.

    Returns:
        List of downloads.
    """
    service = DownloadService(db)
    downloads = await service.list_downloads(limit=limit, offset=offset)
    return [DownloadProgressResponse.model_validate(d) for d in downloads]
