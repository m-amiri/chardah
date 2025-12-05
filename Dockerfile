# Multi-stage Dockerfile for optimized layer caching
# Stage 1: Base image with Python and system dependencies
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies (rarely changes - cached layer)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies installation
FROM base as dependencies

# Copy only requirements file first (changes less frequently than code)
# This allows Docker to cache the pip install layer
COPY requirements.txt .

# Install Python dependencies
# Use --no-cache-dir to reduce image size
# Use --no-deps to avoid unnecessary dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Final production image
FROM base as production

# Copy installed dependencies from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy application code (changes frequently - should be last)
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5014

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5014/health')" || exit 1

# Set environment variables
ENV FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Run the application
CMD ["python", "app.py"]