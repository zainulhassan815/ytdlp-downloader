from fastapi import APIRouter
from models import DownloadStatus
from pydantic import BaseModel


class DownloadProgressResponse(BaseModel):
    url: str
    filename: str
    status: DownloadStatus
    progress: float


downloads_router = APIRouter()


@downloads_router.post("/downloads")
def download_video(url: str):
    """Download a video from a URL.

    Args:
        url (str): The URL of the video to download.

    Returns:
        str: The ID of the download.
    """
    pass


@downloads_router.get("/downloads/{id}")
def get_download_progress(id: str):
    """Get download progress of a video.

    Args:
        id (str): The ID of the download.

    Returns:
        DownloadProgressResponse: The progress of the download.
    """
    pass


@downloads_router.get("/downloads/{id}/cancel")
def cancel_download(id: str):
    """Cancel a download.

    Args:
        id (str): The ID of the download.

    Returns:
        bool: True if the download was cancelled, False otherwise.
    """
    pass
