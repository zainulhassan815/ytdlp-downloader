# YT-DLP Downloader API

An asynchronous video downloader API built with **FastAPI**, **Celery**, and **yt-dlp**. Downloads videos from YouTube and other platforms with background task processing.

## Features

- **REST API** for submitting and managing downloads
- **Background processing** with Celery + Redis
- **PostgreSQL** for persistent download history
- **Progress tracking** with real-time status updates
- **Docker support** for local development and deployment

## Tech Stack

- **FastAPI** - Async web framework
- **Celery** - Distributed task queue
- **Redis** - Message broker and result backend
- **PostgreSQL** - Persistent storage (Neon for production)
- **yt-dlp** - Video downloader
- **SQLAlchemy** - Async ORM
- **Alembic** - Database migrations
- **Docker** - Containerization

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/downloads` | Submit a video URL for download |
| `GET` | `/downloads` | List all downloads |
| `GET` | `/downloads/{id}` | Get download progress |
| `POST` | `/downloads/{id}/cancel` | Cancel a download |
| `GET` | `/health` | Health check |

## Quick Start

### Local Development with Docker

```bash
# Start all services (API, Worker, PostgreSQL, Redis)
docker-compose up --build

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Local Development without Docker

```bash
# Install dependencies
uv sync

# Start Redis and PostgreSQL locally, then:
export DATABASE_URL=postgresql://user:pass@localhost:5432/ytdlp
export REDIS_URL=redis://localhost:6379

# Run API
uv run uvicorn app.main:app --reload

# Run Celery worker (separate terminal)
uv run celery -A app.worker.celery_app worker --loglevel=info
```

## Deployment

### Prerequisites

1. **Neon PostgreSQL**: Create a database at [neon.tech](https://neon.tech)
2. **Render account**: Sign up at [render.com](https://render.com)

### Deploy to Render

1. Push code to GitHub
2. In Render Dashboard: **New** → **Blueprint**
3. Connect your repository (Render detects `render.yaml`)
4. Set `DATABASE_URL` environment variable with your Neon connection string
5. Deploy

### Services Created

- `ytdlp-api` - FastAPI web service
- `ytdlp-worker` - Celery background worker
- `ytdlp-redis` - Redis instance

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `CELERY_BROKER_URL` | Celery broker URL (defaults to REDIS_URL) | No |
| `CELERY_RESULT_BACKEND` | Celery result backend (defaults to REDIS_URL) | No |
| `DOWNLOAD_DIR` | Directory for downloaded files | No (default: `/tmp/downloads`) |

## Project Structure

```
app/
├── config/          # Settings and configuration
├── db/              # Database models and connection
├── models/          # Pydantic models and enums
├── routes/          # API endpoints
├── services/        # Business logic
└── worker/          # Celery tasks
```

## Usage Example

```bash
# Submit a download
curl -X POST "http://localhost:8000/downloads" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Check progress
curl "http://localhost:8000/downloads/{id}"

# List all downloads
curl "http://localhost:8000/downloads"
```

## License

MIT License. This project uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) under its respective license.
