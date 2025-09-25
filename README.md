# Log Generator

![CI](https://github.com/duyhenryer/log-generator/workflows/CI/badge.svg)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

A configurable log generator for testing and benchmarking log pipelines. It generates random logs in webserver-style format, making it ideal for demos and testing with logging solutions such as Loki, VictoriaLogs, and more.

## Features

- 🚀 **High Performance**: Generate thousands of logs per second
- 🎯 **Realistic Data**: Weighted error rates, realistic IPs, user agents
- 💻 **Simple CLI**: Clean command-line interface with Click
- 🐳 **Docker Ready**: Containerized deployment
- ⚡ **Rate Control**: Sleep-based timing control
- 🔒 **Secure Random**: Uses `secrets` module for cryptographically secure randomness

## Prerequisites

- **Python** `>=3.11,<3.14`
- **uv** `>=0.5.0` (recommended)

## Installation

### Using uv (Recommended)
```bash
# Install uv 
curl -LsSf https://astral.sh/uv/install.sh | sh

# clone repo
git clone https://github.com/duyhenryer/log-generator.git
cd log-generator

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install --editable .
```
## Quick Start

### Basic Usage
```bash
# Generate webserver logs (default - infinite)
log-generator --sleep 0.5 --error-rate 0.2

# Generate JSON logs
log-generator --format json --sleep 1 --count 100

# High-rate generation for stress testing
log-generator --sleep 0.1 --count 10000

# Add latency simulation
log-generator --sleep 1 --latency 0.5 --error-rate 0.3
```

### Example Output

**Raw Format:**
```
192.168.1.45 - [09/Sep/2025:14:30:15 ] "GET /api/users HTTP/2" 200 1247 "https://github.com/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" "US" 0.845
10.0.0.123 - [09/Sep/2025:14:30:16 ] "POST /api/orders HTTP/1.1" 201 856 "-" "curl/7.68.0" "CN" 1.234
```

**JSON Format:**
```json
{"remote_addr": "192.168.1.45", "remote_user": "-", "time_local": "09/Sep/2025:14:30:15 ", "request": "GET /api/users HTTP/2", "status": 200, "body_bytes_sent": 1247, "http_referer": "https://github.com/", "http_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "country": "US", "request_time": 0.845}
```

## Configuration

### Command Line Options
```bash
log-generator --help

Options:
  --sleep FLOAT          Seconds to sleep between logs (default: 0)
  --error-rate FLOAT     Fraction of logs that are errors (default: 0.1)
  --format [raw|json]    Log output format (default: raw)
  --count INTEGER        Number of logs to generate (default: 0 for infinite)
  --latency FLOAT        Additional latency in seconds (default: 0.0)
  --help                 Show this message and exit
```

## Use Cases

### 1. Testing Loki/Grafana
```bash
# Generate logs and pipe to Promtail
log-generator --sleep 0.01 | promtail --config.file=promtail.yaml
```

### 2. VictoriaLogs Testing
```bash
# Generate JSON logs for VictoriaLogs
log-generator --format json --sleep 0.005 > /var/log/app.log
```

### 3. Load Testing
```bash
# High-rate generation for stress testing
log-generator --sleep 0.001 --count 100000 > stress_test.log
```

### 4. Demo Data
```bash
# Generate sample data for demos
log-generator --sleep 1 --count 500 --error-rate 0.3
```

## Development

### Setup Development Environment
```bash
# Install package with dev dependencies
make install

# Or manually with uv
uv venv
source .venv/bin/activate
uv pip install --editable ".[dev,test]"
```

### Available Make Commands
```bash
# Show all available commands
make help

# Development workflow
make install    # Install package with dev/test dependencies
make test       # Run tests with pytest
make lint       # Run linting (ruff + mypy)
make format     # Format code with ruff
make clean      # Clean up build artifacts and cache
make examples   # Run sample log generation examples

# Docker commands
make docker-build      # Build production Docker image
make docker-run        # Run production container
make docker-build-dev  # Build development Docker image
make docker-run-dev    # Run development container
```

## Deployment with Helm Chart

You can deploy Log Generator using the Helm chart. This is the recommended way to run in Kubernetes environments.

### Prerequisites
- [Helm](https://helm.sh/) installed.
- Source Helm charts are published at: [duyhenryer/charts](https://github.com/duyhenryer/charts)

### Install with Helm
```bash
helm install log-generator duyhenryer/log-generator
```

This will deploy Log Generator with default settings. You can customize values using the `--set` flag or a custom values file:
```bash
helm install log-generator duyhenryer/log-generator \
  --set sleep=0.5,errorRate=0.2,format=json
```

For more configuration options, refer to the chart documentation or use:
```bash
helm show values duyhenryer/log-generator
```

### Upgrade or Uninstall
```bash
# Upgrade release
helm upgrade log-generator duyhenryer/log-generator

# Uninstall release
helm uninstall log-generator
```
