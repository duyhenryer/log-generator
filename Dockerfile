FROM python:3.11-slim

LABEL org.opencontainers.image.title="log-generator"
LABEL org.opencontainers.image.description="A continuous log generator for testing and benchmarking log pipelines"
LABEL org.opencontainers.image.vendor="duyhenryer"
LABEL org.opencontainers.image.source="https://github.com/duyhenryer/log-generator"

# Set working directory
WORKDIR /app

# Install uv for faster dependency management
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml ./
COPY loggen/ ./loggen/

# Install dependencies and the package
RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python --no-cache-dir -e .

# Create non-root user
RUN groupadd -r loggen && useradd -r -g loggen -s /bin/false loggen
RUN chown -R loggen:loggen /app /opt/venv
USER loggen

# Use virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD log-generator --count 1 --format json > /dev/null || exit 1

# Set default command
ENTRYPOINT ["log-generator"]
CMD ["--help"]
