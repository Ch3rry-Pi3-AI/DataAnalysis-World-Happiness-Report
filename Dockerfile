# Dockerfile
FROM python:3.13-slim

# Basic environment settings
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install build tools (needed if a package has to compile)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install uv in the container (isolated from host)
RUN python -m pip install --upgrade pip && pip install uv

# Copy dependency files first (better layer caching)
COPY pyproject.toml uv.lock /app/

# Export a frozen requirements file from the lock
RUN uv export --format requirements-txt --no-editable --frozen -o requirements.lock

# Install dependencies into system site-packages
RUN uv pip install --system -r requirements.lock

# Copy the rest of the project
COPY . /app

# Ensure src/ is importable
ENV PYTHONPATH=/app

# Expose Dash port
EXPOSE 8050

# Run pipeline + dashboard
CMD ["python", "app.py"]
