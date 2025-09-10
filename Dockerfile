# syntax=docker/dockerfile:1

# ---- Base image ----
FROM python:3.11-slim AS base

LABEL org.opencontainers.image.title="log-generator"
LABEL org.opencontainers.image.description="A continuous log generator for testing and benchmarking log pipelines"
LABEL org.opencontainers.image.vendor="duyhenryer"
LABEL org.opencontainers.image.authors="Duy nè <hello@duyne.me>"
LABEL org.opencontainers.image.source="https://github.com/duyhenryer/log-generator"

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---- Development image ----
FROM base AS development
RUN pip install --upgrade pip && pip install uv
COPY . .
RUN uv venv
RUN . .venv/bin/activate && uv pip install --editable ".[dev,test]"
USER 10001:10001
CMD [".venv/bin/log-generator"]

# ---- Production image ----
FROM base AS production
RUN pip install --upgrade pip && pip install uv
COPY loggen/ ./loggen/
COPY pyproject.toml ./
RUN uv pip install --system .
USER 10001:10001
ENTRYPOINT ["log-generator"]