from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.base import Base, engine
from app.routes.downloads import downloads_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="YT-DLP Downloader API",
    description="Asynchronous Video Downloader API with FastAPI + yt-dlp",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(downloads_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
