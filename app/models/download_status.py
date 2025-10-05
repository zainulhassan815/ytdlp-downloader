from enum import StrEnum


class DownloadStatus(StrEnum):
    Queued = "Queued"
    InProgress = "InProgress"
    Completed = "Completed"
    Failed = "Failed"
    Cancelled = "Cancelled"
