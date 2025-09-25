from prometheus_client import start_http_server, Counter, Gauge
import threading
import os

# Metrics definitions
METRIC_LOGS_TOTAL = Counter("logs_generated_total", "Total logs generated")
METRIC_LOGS_ERROR = Counter("logs_error_total", "Total error logs generated")
METRIC_ERROR_RATE = Gauge("logs_error_rate", "Current error rate")
METRIC_LATENCY = Gauge("log_latency_seconds", "Latest log latency in seconds")
METRIC_UPTIME = Gauge("log_generator_uptime", "Log generator process start time (unix epoch)")


def start_metrics_server():
    metrics_port = int(os.environ.get("METRICS_PORT", "8000"))
    threading.Thread(target=start_http_server, args=(metrics_port,), daemon=True).start()
    METRIC_UPTIME.set_to_current_time()


def update_metrics(error_level, request_time):
    METRIC_LOGS_TOTAL.inc()
    if error_level != "ok":
        METRIC_LOGS_ERROR.inc()
    total = METRIC_LOGS_TOTAL._value.get()
    errors = METRIC_LOGS_ERROR._value.get()
    METRIC_ERROR_RATE.set(errors / total if total > 0 else 0)
    METRIC_LATENCY.set(request_time)
