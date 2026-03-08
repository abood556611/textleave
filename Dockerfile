# TextLeaf - Match Cut Video Generator
# Multi-stage Docker build for production

# Stage 1: Base image with dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Stage 2: Production image
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libpng16-16 \
    libjpeg62-turbo \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /app/uploads /app/output && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy Python packages from base stage
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Copy application files
COPY --chown=appuser:appuser . .

# Create necessary directories with proper permissions
RUN mkdir -p uploads output static/backgrounds static/audio && \
    chown -R appuser:appuser uploads output static && \
    chmod -R 777 uploads output static

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/calculate', json={'duration': 10})" || exit 1

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "300", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
