FROM python:3.11-slim

LABEL maintainer="OpenBB Deployment"
LABEL description="OpenBB Open Data Platform for DigitalOcean"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV OPENBB_API_HOST=0.0.0.0
ENV OPENBB_API_PORT=6900

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libwebkit2gtk-4.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (required for some OpenBB dependencies)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Create app directory
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Install OpenBB Platform
RUN pip install openbb openbb-cli

# Create OpenBB config directory
RUN mkdir -p /root/.openbb_platform

# Copy configuration files
COPY config/user_settings.json /root/.openbb_platform/user_settings.json

# Expose the API port
EXPOSE 6900

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:6900/api/v1/health || exit 1

# Start OpenBB API server
CMD ["python", "-c", "from openbb import obb; obb.account.login(); import uvicorn; uvicorn.run('openbb_core.api.rest_api:app', host='0.0.0.0', port=6900)"]
