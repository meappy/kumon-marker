# Multi-stage Dockerfile for Kumon Marker

# Build argument for version (can be set during docker build)
ARG VERSION=0.2.0

# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

ARG VERSION
WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy source and build with version
COPY frontend/ ./
# Update package.json version before build
RUN sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"${VERSION}\"/" package.json
RUN npm run build

# Stage 2: Python backend with frontend static files
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS runtime

ARG VERSION
WORKDIR /app

# Install system dependencies for PyMuPDF and Tesseract OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmupdf-dev \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY backend/pyproject.toml ./
COPY backend/app ./app

# Install Python dependencies with uv
RUN uv pip install --system -e .

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create data directories
RUN mkdir -p /app/data/scans /app/data/marked /app/data/reports /app/data/results

# Environment
ENV DATA_DIR=/app/data
ENV PYTHONUNBUFFERED=1
ENV APP_VERSION=${VERSION}

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
