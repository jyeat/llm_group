# Simplified Trading Agents - Docker Image
# Multi-stage build for optimized image size

FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt


# Final stage - minimal runtime image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY agent/ ./agent/
COPY tools/ ./tools/
COPY ui/ ./ui/
COPY config.py .
COPY state.py .
COPY trading_graph.py .
COPY main.py .
COPY verify_setup.py .
COPY .env.example .
COPY README_MC_SZ_INTEGRATION.md .
COPY NEWSAPI_SETUP_GUIDE.md .

# Create necessary directories
RUN mkdir -p ui/analysis_cache analysis

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port for web UI
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Default command - run web UI
CMD ["python", "-u", "ui/web_app.py"]
