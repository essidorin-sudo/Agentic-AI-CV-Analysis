#!/usr/bin/env python3
"""
Shared test setup and utilities for CV Parser Agent

Provides centralized test configuration, cleanup, and common utilities
following GL-Testing-Guidelines standards.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from contextlib import contextmanager
from typing import Dict, Any, Optional


class CVParserTestSetup:
    """Centralized test setup for CV Parser Agent"""
    
    def __init__(self):
        self.temp_files = []
        self.mocks = []
        self.original_env = {}
        
    def setup_test_environment(self):
        """Setup clean test environment with proper isolation"""
        # Save original environment
        self.original_env = dict(os.environ)
        
        # Use production API key for testing (as authorized by user)
        os.environ['ANTHROPIC_API_KEY'] = 'test-api-key-for-testing'
        os.environ['ENV'] = 'test'
        
        return self
        
    def cleanup(self):
        """Clean up test environment and temporary resources"""
        # Clean up temp files
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception:
                pass
        
        # Stop all mocks
        for mock in self.mocks:
            if hasattr(mock, 'stop'):
                mock.stop()
        
        # Restore environment
        os.environ.clear()
        os.environ.update(self.original_env)
        
        # Clear lists
        self.temp_files.clear()
        self.mocks.clear()
        
    def create_temp_file(self, content: str, suffix: str = '.txt') -> str:
        """Create temporary file for testing"""
        fd, path = tempfile.mkstemp(suffix=suffix)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)
        except Exception:
            os.close(fd)
            raise
        
        self.temp_files.append(path)
        return path
        
    def mock_anthropic_client(self, response_data: Dict[str, Any]):
        """Create mock for Anthropic client"""
        mock_client = Mock()
        mock_client.call_text_api.return_value = response_data
        mock_client.call_file_api.return_value = response_data
        mock_client.is_available.return_value = True
        
        mock_patch = patch('llm_integration.anthropic_client.AnthropicClient', return_value=mock_client)
        self.mocks.append(mock_patch)
        return mock_patch.start()
        
    @contextmanager
    def assert_no_exceptions(self):
        """Context manager to ensure no exceptions are raised"""
        try:
            yield
        except Exception as e:
            self.fail(f"Unexpected exception raised: {e}")


def setup_test():
    """
    Factory function for test setup following GL-Testing-Guidelines
    
    Returns:
        CVParserTestSetup: Configured test setup instance
    """
    return CVParserTestSetup().setup_test_environment()


class CVParserTestCase(unittest.TestCase):
    """Base test case class with shared setup and teardown"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.test_setup = setup_test()
        
    def tearDown(self):
        """Clean up after each test"""
        self.test_setup.cleanup()