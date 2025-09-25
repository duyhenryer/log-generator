import requests
import pytest

def test_metrics_endpoint():
    resp = requests.get("http://localhost:8000/metrics")
    assert resp.status_code == 200
    assert "logs_generated_total" in resp.text
