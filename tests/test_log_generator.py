#!/usr/bin/env python3
"""Tests for loggen module."""

import json
import pytest
from loggen.main import generate_log_entry, pick_error_level, pick_status_code


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
        
        # Check for expected fields including message for VictoriaLogs
        expected_fields = [
            'message', 'remote_addr', 'remote_user', 'time_local', 'request',
            'status', 'body_bytes_sent', 'http_referer', 
            'http_user_agent', 'country', 'request_time'
        ]
        for field in expected_fields:
            assert field in parsed
        
        # Check types
        assert isinstance(parsed['status'], int)
        assert isinstance(parsed['body_bytes_sent'], int)
        assert isinstance(parsed['request_time'], float)
        assert isinstance(parsed['message'], str)
        
        # Verify message field contains expected log components
        message = parsed['message']
        assert parsed['remote_addr'] in message
        assert str(parsed['status']) in message
        assert parsed['country'] in message
    
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


if __name__ == '__main__':
    pytest.main([__file__])
