#!/usr/bin/env python3
"""
A configurable log generator for testing and benchmarking log pipelines.
Generates random logs in webserver-style format for demos and testing.
"""

import json
import random
import secrets
import sys
import time
from datetime import datetime, timedelta

import click

# Sample data for random generation
HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]
HTTP_PATHS = [
    "/",
    "/api/users",
    "/api/orders",
    "/login",
    "/logout",
    "/products",
    "/health",
    "/metrics",
]
HTTP_VERSIONS = ["HTTP/1.1", "HTTP/2"]
USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/15.1 Safari/605.1.15"
    ),
    "curl/7.68.0",
    "PostmanRuntime/7.28.4",
]
REFERERS = [
    "-",
    "https://google.com/search?q=loggen",
    "https://github.com/",
    "https://example.com/",
]
COUNTRY_CODES = ["US", "FR", "DE", "IN", "CN", "BR", "GB", "RU", "JP", "AU"]

# HTTP status code pools
HTTP_CODES = {
    "ok": [200, 201, 202, 204],
    "client_error": [400, 401, 403, 404, 429],
    "server_error": [500, 502, 503, 504],
}


def random_ip():
    """Generate a random IP address."""
    return ".".join(str(secrets.randbelow(255) + 1) for _ in range(4))


def random_time():
    """Generate random time in the last 30 days."""
    now = datetime.now()
    offset = -secrets.randbelow(60 * 60 * 24 * 30 + 1)
    dt = now + timedelta(seconds=offset)
    return dt.strftime("%d/%b/%Y:%H:%M:%S +0000")


def random_request():
    """Generate a random HTTP request."""
    method = secrets.choice(HTTP_METHODS)
    path = secrets.choice(HTTP_PATHS)
    version = secrets.choice(HTTP_VERSIONS)
    return f"{method} {path} {version}"


def random_bytes():
    """Generate random response size."""
    return secrets.randbelow(5000 - 100 + 1) + 100


def random_request_time():
    """Simulate request time between 0.200 and 1.500 seconds."""
    return round(random.uniform(0.2, 1.5), 3)  # nosec


def pick_error_level(error_rate):
    """Pick error level based on error rate."""
    r = secrets.randbelow(10**9) / 10**9
    if r < error_rate / 2:
        return "client_error"
    elif r < error_rate:
        return "server_error"
        else:
        return "ok"


def pick_status_code(error_type):
    """Pick status code based on error type."""
    return secrets.choice(HTTP_CODES[error_type])


def generate_log_entry(error_rate, output_format, latency=0.0):
    """Generate a single log entry."""
    error_level = pick_error_level(error_rate)
    remote_addr = random_ip()
    remote_user = "-"
    time_local = random_time()
    request = random_request()
    status = pick_status_code(error_level)
    body_bytes_sent = random_bytes()
    http_referer = secrets.choice(REFERERS)
    http_user_agent = secrets.choice(USER_AGENTS)
    country = secrets.choice(COUNTRY_CODES)
    request_time = round(random_request_time() + latency, 3)

    if output_format == "raw":
        return (
            f"{remote_addr} {remote_user} [{time_local}] \"{request}\" "
            f"{status} {body_bytes_sent} \"{http_referer}\" "
            f"\"{http_user_agent}\" \"{country}\" {request_time}"
        )
    else:  # json
        log_dict = {
            "remote_addr": remote_addr,
            "remote_user": remote_user,
            "time_local": time_local,
            "request": request,
            "status": status,
            "body_bytes_sent": body_bytes_sent,
            "http_referer": http_referer,
            "http_user_agent": http_user_agent,
            "country": country,
            "request_time": request_time,
        }
        return json.dumps(log_dict)


@click.command()
@click.option(
    "--sleep",
    type=float,
    default=0,
    help="Seconds to sleep between logs (default: 0)",
)
@click.option(
    "--error-rate",
    type=float,
    default=0.1,
    help="Fraction of logs that are errors (default: 0.1)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["raw", "json"]),
    default="raw",
    help="Log output format (raw or json)",
)
@click.option(
    "--count",
    type=int,
    default=0,
    help="Number of logs to generate (default: 0 for infinite)",
)
@click.option(
    "--latency",
    type=float,
    default=0.0,
    help="Additional latency (in seconds) to add to request_time (default: 0)",
)
def main(sleep, error_rate, output_format, count, latency):
    """Continuous log generator."""
    try:
        i = 0
        while count == 0 or i < count:
            log_entry = generate_log_entry(error_rate, output_format, latency)
            print(log_entry, flush=True)
            if sleep > 0:
                time.sleep(sleep)
            i += 1
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
