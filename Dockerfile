# Stage 1: Builder
FROM python:3.14-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*


# Copy dependency files
COPY pyproject.toml uv.lock ./
COPY src/ src/

# Install dependencies and build wheel
RUN uv sync --frozen --no-dev && \
    uv build

# Stage 2: Runtime — Python app + Envoy managed by supervisord
FROM python:3.14-slim

# Build metadata arguments
ARG BUILD_DATE=unknown
ARG GIT_COMMIT_SHA=unknown

ENV BUILD_DATE=${BUILD_DATE}
ENV GIT_COMMIT_SHA=${GIT_COMMIT_SHA}
ENV MODE=prod
ENV PORT=50051

# Install supervisord; copy Envoy binary from the official image
RUN apt-get update && apt-get install -y --no-install-recommends supervisor \
    && rm -rf /var/lib/apt/lists/*

COPY --from=envoyproxy/envoy:v1.31-latest /usr/local/bin/envoy /usr/local/bin/envoy

WORKDIR /app

# Copy wheel artifact from builder
COPY --from=builder /app/dist/*.whl /tmp/

# Install the wheel using the system Python's pip (avoid relying on a copied venv)
RUN python -m pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl

COPY envoy.yaml /etc/envoy/envoy.yaml
COPY fly/supervisord.conf /etc/supervisor/conf.d/petstore.conf

EXPOSE 50051 8080

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/petstore.conf"]
