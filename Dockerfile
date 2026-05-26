# Stage 1: Builder
FROM python:3.14-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./
COPY src/ src/

# Install dependencies and build wheel
RUN uv sync --frozen --no-dev && \
    uv build

# Stage 2: Runtime
FROM python:3.14-slim

# Build metadata arguments
ARG BUILD_DATE=unknown
ARG GIT_COMMIT_SHA=unknown

# Set as environment variables
ENV BUILD_DATE=${BUILD_DATE}
ENV GIT_COMMIT_SHA=${GIT_COMMIT_SHA}
ENV MODE=prod
ENV PORT=50051

WORKDIR /app

# Copy wheel artifact from builder
COPY --from=builder /app/dist/*.whl /tmp/

# Install the wheel using the system Python's pip (avoid relying on a copied venv)
RUN python -m pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl

# Expose gRPC port
EXPOSE 50051

# Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# No venv copied into the runtime image; use the system Python

CMD ["python", "-m", "petstore_grpc"]
