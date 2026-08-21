FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock README.md ./

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy source before installing the project itself
COPY src/ ./src/

# Install dependencies
ENV UV_PROJECT_ENVIRONMENT="/app/.venv"
RUN uv sync --no-dev --frozen

COPY .env.example .env.example

# Expose ports
EXPOSE 8000 8080

# Default command: start MCP server
ENTRYPOINT [".venv/bin/promptctl"]
CMD ["serve"]
