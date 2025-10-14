# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11

# ---- Development image ----
FROM ghcr.io/duyhenryer/wolfi-images/python:${PYTHON_VERSION}-dev AS development

LABEL org.opencontainers.image.title="log-generator-dev"
LABEL org.opencontainers.image.description="Log generator with development tools"
LABEL org.opencontainers.image.vendor="duyhenryer"
LABEL org.opencontainers.image.authors="Duy nè <hello@duyne.me>"
LABEL org.opencontainers.image.source="https://github.com/duyhenryer/log-generator"

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . .
RUN uv sync --extra dev --extra test && \
    uv pip install --editable .
USER 10001:10001
ENTRYPOINT ["/app/.venv/bin/log-generator"]

# ---- Builder stage (install to system) ----
FROM ghcr.io/duyhenryer/wolfi-images/python:${PYTHON_VERSION}-dev AS builder

ARG PYTHON_VERSION
WORKDIR /app
COPY pyproject.toml ./
COPY loggen/ ./loggen/
RUN uv pip install --system --no-cache .

# ---- Production image (minimal, distroless) ----
FROM ghcr.io/duyhenryer/wolfi-images/python:${PYTHON_VERSION} AS production

ARG PYTHON_VERSION
LABEL org.opencontainers.image.title="log-generator"
LABEL org.opencontainers.image.description="Log generator for testing and benchmarking log pipelines"
LABEL org.opencontainers.image.vendor="duyhenryer"
LABEL org.opencontainers.image.authors="Duy nè <hello@duyne.me>"
LABEL org.opencontainers.image.source="https://github.com/duyhenryer/log-generator"

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy installed packages from builder
COPY --from=builder /usr/lib/python${PYTHON_VERSION}/site-packages /usr/lib/python${PYTHON_VERSION}/site-packages
COPY --from=builder /usr/bin/log-generator /usr/bin/log-generator

USER 10001:10001
ENTRYPOINT ["log-generator"]