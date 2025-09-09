#!/usr/bin/env python3
"""Tests for loggen module."""

import json
import pytest
from loggen.main import (
    generate_log_entry,
    pick_error_level,
    pick_status_code,
    random_ip,
    random_time,
    random_request,
    random_bytes,
    random_request_time,
)


class TestLoggen:
    """Test cases for loggen functions."""
    
    def test_generate_log_entry_raw_format(self):
        """Test raw log entry generation."""
        log_entry = generate_log_entry(0.1, "raw", 0.0)
        
        # Check basic format
        assert isinstance(log_entry, str)
        assert len(log_entry) > 0
        
        # Check for expected components
        parts = log_entry.split(' ')
        assert len(parts) >= 8  # Should have IP, user, timestamp, request, etc.
        
        # Check IP format (basic validation)
        ip = parts[0]
        ip_parts = ip.split('.')
        assert len(ip_parts) == 4
        
        # Check timestamp format
        assert '[' in log_entry and ']' in log_entry
        
        # Check HTTP method
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        assert any(method in log_entry for method in methods)
    
    def test_generate_log_entry_json_format(self):
        """Test JSON log entry generation."""
        log_entry = generate_log_entry(0.1, "json", 0.0)
        
        # Check if it's valid JSON
        parsed = json.loads(log_entry)
        assert isinstance(parsed, dict)
        
        # Check for expected fields
        expected_fields = [
            'remote_addr', 'remote_user', 'time_local', 'request',
            'status', 'body_bytes_sent', 'http_referer', 
            'http_user_agent', 'country', 'request_time'
        ]
        for field in expected_fields:
            assert field in parsed
        
        # Check types
        assert isinstance(parsed['status'], int)
        assert isinstance(parsed['body_bytes_sent'], int)
        assert isinstance(parsed['request_time'], float)
    
    def test_pick_error_level(self):
        """Test error level selection."""
        # Test with 0 error rate - should always be ok
        for _ in range(10):
            assert pick_error_level(0.0) == "ok"
        
        # Test with 1.0 error rate - should never be ok
        for _ in range(10):
            assert pick_error_level(1.0) != "ok"
    
    def test_pick_status_code(self):
        """Test status code selection."""
        # Test ok codes
        ok_code = pick_status_code("ok")
        assert ok_code in [200, 201, 202, 204]
        
        # Test client error codes
        client_code = pick_status_code("client_error")
        assert client_code in [400, 401, 403, 404, 429]
        
        # Test server error codes
        server_code = pick_status_code("server_error")
        assert server_code in [500, 502, 503, 504]
    
    def test_latency_addition(self):
        """Test latency is added to request time."""
        log_entry = generate_log_entry(0.1, "json", 1.0)
        parsed = json.loads(log_entry)
        
        # Request time should be at least 1.0 (base latency) + 0.2 (minimum random)
        assert parsed['request_time'] >= 1.2
    
    def test_random_ip(self):
        """Test IP generation."""
        ip = random_ip()
        parts = ip.split('.')
        assert len(parts) == 4
        for part in parts:
            assert 1 <= int(part) <= 255
    
    def test_random_time(self):
        """Test time generation."""
        time_str = random_time()
        assert isinstance(time_str, str)
        assert '+0000' in time_str
        assert '/' in time_str and ':' in time_str
    
    def test_random_request(self):
        """Test HTTP request generation."""
        request = random_request()
        assert isinstance(request, str)
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        assert any(method in request for method in methods)
        assert 'HTTP/' in request
    
    def test_random_bytes(self):
        """Test bytes generation."""
        bytes_val = random_bytes()
        assert isinstance(bytes_val, int)
        assert 100 <= bytes_val <= 5000
    
    def test_random_request_time(self):
        """Test request time generation."""
        req_time = random_request_time()
        assert isinstance(req_time, float)
        assert 0.2 <= req_time <= 1.5


if __name__ == '__main__':
    pytest.main([__file__])
