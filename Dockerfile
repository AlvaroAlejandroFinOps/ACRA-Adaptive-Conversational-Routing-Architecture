# Multi-stage production-grade Dockerfile for ACRA Architecture
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests
COPY pyproject.toml /app/

# Install Python packages
RUN pip install --upgrade pip && \
    pip install .[dev,benchmark]

# Copy project files
COPY . /app/

# Non-root user for security hardening
RUN useradd -m -u 1001 acrauser && \
    chown -R acrauser:acrauser /app
USER acrauser

EXPOSE 8000

# Default entrypoint runs reproducibility verification and tests
CMD ["python", "scripts/verify_reproducibility.py"]
