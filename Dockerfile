FROM python:3.13-slim

# Install system dependencies for yt-dlp
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container
COPY . /app

# Install the application dependencies
WORKDIR /app
RUN uv sync --frozen --no-cache

# Create downloads directory
RUN mkdir -p /tmp/downloads

# Expose port
EXPOSE 8000

# Run the application
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
