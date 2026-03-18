# ==============================================================================
# Stage 1: Build frontend
# ==============================================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --ignore-scripts

COPY frontend/ ./
RUN npm run build

# ==============================================================================
# Stage 2: Python application
# ==============================================================================
FROM python:3.11-slim AS runner

RUN groupadd --gid 1001 appuser \
    && useradd --uid 1001 --gid 1001 --shell /bin/false appuser

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# Copy backend source
COPY src/ ./src/

# Copy built frontend assets
COPY --from=frontend-builder /app/frontend/dist ./static/

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "src.runtime.app:app", "--host", "0.0.0.0", "--port", "8000"]
