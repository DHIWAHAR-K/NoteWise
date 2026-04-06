# --- build stage ---
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- runtime stage ---
FROM python:3.12-slim

# Non-root user
RUN useradd --create-home notewise
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source and migrations
COPY app/ ./app/
COPY alembic.ini .
COPY alembic/ ./alembic/

USER notewise

# Cloud Run passes PORT env; default to 8000 for local dev
ENV PORT=8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
