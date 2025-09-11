# Async Video Downloader API 🎥⚡

A simple **asynchronous API** built with **FastAPI** that uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) to download videos from various platforms.  
This project is meant for learning **asynchronous system design**, **task queues**, and **containerized deployments**.

---

## ✅ TODO List (Features to Implement)

- [ ] **FastAPI Endpoints**
  - [ ] `POST /download` → submit video URL for download
  - [ ] `GET /status/{job_id}` → check progress of a job
  - [ ] `GET /result/{job_id}` → retrieve download result (file link or path)

- [ ] **Asynchronous Jobs**
  - [ ] Implement simple background tasks using FastAPI
  - [ ] Later migrate to **Celery + Redis** for scalable async jobs

- [ ] **Metadata & Progress Tracking**
  - [ ] Store job states (`PENDING`, `IN_PROGRESS`, `DONE`, `FAILED`)
  - [ ] Keep live progress percentage
  - [ ] Use Redis for ephemeral state
  - [ ] (Optional) Add PostgreSQL for persistent job history

- [ ] **Storage**
  - [ ] Save downloaded files to a local volume
  - [ ] Add support for S3/MinIO for cloud storage

- [ ] **Deployment**
  - [ ] Create Dockerfile for FastAPI + yt-dlp + ffmpeg
  - [ ] Add docker-compose with API + Worker + Redis
  - [ ] Enable volume mounts for downloads
  - [ ] Prepare for Kubernetes deployment (optional)

- [ ] **Enhancements (Future)**
  - [ ] Real-time progress updates via WebSockets
  - [ ] Authentication & user-based download history
  - [ ] Advanced yt-dlp options (audio extraction, subtitles, format selection)
  - [ ] Rate limiting & job expiration

---

## 🏗️ Basic Architecture

**Flow of a video download request:**

1. **Client (UI / API consumer)**  
   - Calls `POST /download` with video URL.  
   - Polls `/status/{job_id}` for progress.  
   - Retrieves file using `/result/{job_id}` once complete.  

2. **FastAPI Service (API layer)**  
   - Accepts requests and returns a Job ID.  
   - Submits download task asynchronously.  
   - Provides status & result endpoints.  

3. **Task Queue + Worker**  
   - Worker pulls jobs from queue (BackgroundTask or Celery).  
   - Executes `yt-dlp` to download video.  
   - Updates job status in Redis/DB.  

4. **Storage**  
   - **Redis** → short-term job state + progress.  
   - **Filesystem / S3** → stores actual video files.  
   - **PostgreSQL (optional)** → long-term persistent job history.  

---

## 📦 Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/) → API framework  
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) → video downloader  
- [Redis](https://redis.io/) → async job state + queue  
- [Celery](https://docs.celeryq.dev/) → distributed task queue (future upgrade)  
- [Docker](https://www.docker.com/) → containerized deployment  
- [PostgreSQL](https://www.postgresql.org/) (optional) → persistent metadata  

---

## 📄 License

MIT License.  
This project uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) under its respective license.

