# Multi-stage build for optimized image size
FROM python:3.12.10-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies if needed (e.g., for C extensions)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final stage
FROM python:3.12.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user
RUN useradd --create-home --uid 10001 appuser

# Set working directory
WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Configure listener and database via environment variables
# This leverages the refactoring in main.py to avoid fragile sed patching
ENV HOST="0.0.0.0" \
    SESSION_DB_URL="sqlite:////data/sessions.db"

# Create data directory and ensure appuser owns it and the app directory
RUN mkdir /data && chown appuser:appuser /data \
    && mkdir -p /app/.adk && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Declare volume for persistence
VOLUME ["/data"]

# Run the application
CMD ["python", "main.py"]
