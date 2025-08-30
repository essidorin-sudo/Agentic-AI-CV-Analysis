#!/usr/bin/env python3
"""
Anthropic API mock factories for CV Parser Agent testing

Provides centralized mocking for Anthropic Claude API calls
following GL-Testing-Guidelines standards.
"""

from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Optional, List
import json


class AnthropicMockFactory:
    """Factory for creating Anthropic API mocks"""
    
    @staticmethod
    def create_success_mock(response_data: Dict[str, Any]) -> Mock:
        """
        Create mock for successful Anthropic API response
        
        Args:
            response_data: The data to return from API call
            
        Returns:
            Mock client configured for success scenario
        """
        mock_client = Mock()
        mock_client.call_text_api.return_value = response_data
        mock_client.call_file_api.return_value = response_data
        mock_client.is_available.return_value = True
        mock_client.model_name = "claude-3-5-sonnet-20241022"
        mock_client.version = "2.0.0"
        
        return mock_client
    
    @staticmethod
    def create_cv_parsing_mock(cv_data: Dict[str, Any]) -> Mock:
        """
        Create mock specifically for CV parsing responses
        
        Args:
            cv_data: Expected CV data structure
            
        Returns:
            Mock client configured for CV parsing
        """
        mock_client = AnthropicMockFactory.create_success_mock(cv_data)
        
        # Add specific parsing behavior
        mock_client.call_text_api.return_value = cv_data
        mock_client.call_file_api.return_value = cv_data
        
        return mock_client
    
    @staticmethod
    def create_error_mock(error_message: str, error_type: Exception = Exception) -> Mock:
        """
        Create mock for API error scenarios
        
        Args:
            error_message: Error message to raise
            error_type: Type of exception to raise
            
        Returns:
            Mock client configured to raise errors
        """
        mock_client = Mock()
        mock_client.call_text_api.side_effect = error_type(error_message)
        mock_client.call_file_api.side_effect = error_type(error_message)
        mock_client.is_available.return_value = True
        mock_client.model_name = "claude-3-5-sonnet-20241022"
        mock_client.version = "2.0.0"
        
        return mock_client
    
    @staticmethod
    def create_unavailable_mock() -> Mock:
        """
        Create mock for when Anthropic API is unavailable
        
        Returns:
            Mock client configured as unavailable
        """
        mock_client = Mock()
        mock_client.is_available.return_value = False
        mock_client.model_name = "claude-3-5-sonnet-20241022"
        mock_client.version = "2.0.0"
        
        return mock_client
    
    @staticmethod
    def create_malformed_response_mock() -> Mock:
        """
        Create mock for malformed API responses
        
        Returns:
            Mock client that returns malformed data
        """
        malformed_data = {
            "invalid": "response",
            "missing_fields": True
        }
        
        return AnthropicMockFactory.create_success_mock(malformed_data)
    
    @staticmethod
    def create_rate_limit_mock() -> Mock:
        """
        Create mock for API rate limiting scenarios
        
        Returns:
            Mock client that simulates rate limiting
        """
        return AnthropicMockFactory.create_error_mock(
            "Rate limit exceeded", 
            Exception
        )
    
    @staticmethod
    def create_timeout_mock() -> Mock:
        """
        Create mock for API timeout scenarios
        
        Returns:
            Mock client that simulates timeouts
        """
        return AnthropicMockFactory.create_error_mock(
            "Request timeout", 
            Exception
        )
    
    @staticmethod
    def create_partial_response_mock(cv_data: Dict[str, Any]) -> Mock:
        """
        Create mock for partial/incomplete API responses
        
        Args:
            cv_data: Partial CV data with missing fields
            
        Returns:
            Mock client with incomplete response
        """
        # Remove some fields to simulate partial response
        partial_data = cv_data.copy()
        partial_data.pop('email', None)
        partial_data.pop('phone', None)
        partial_data['key_skills'] = cv_data.get('key_skills', [])[:3]  # Partial skills
        
        return AnthropicMockFactory.create_success_mock(partial_data)


class ResponseProcessorMockFactory:
    """Factory for mocking response processor components"""
    
    @staticmethod
    def create_json_parsing_mock(parsed_data: Dict[str, Any]) -> Mock:
        """
        Create mock for JSON response parsing
        
        Args:
            parsed_data: Data to return after parsing
            
        Returns:
            Mock response processor
        """
        mock_processor = Mock()
        mock_processor.parse_json_response.return_value = parsed_data
        mock_processor.validate_response_structure.return_value = parsed_data
        
        return mock_processor
    
    @staticmethod
    def create_json_error_mock(error_message: str) -> Mock:
        """
        Create mock for JSON parsing errors
        
        Args:
            error_message: Error to simulate
            
        Returns:
            Mock processor that raises JSON errors
        """
        mock_processor = Mock()
        mock_processor.parse_json_response.side_effect = json.JSONDecodeError(
            error_message, "mock json", 0
        )
        
        return mock_processor


# Context manager for patching Anthropic client
class MockAnthropicClient:
    """Context manager for mocking Anthropic client"""
    
    def __init__(self, mock_client: Mock):
        self.mock_client = mock_client
        self.patcher = None
    
    def __enter__(self):
        self.patcher = patch('llm_integration.anthropic_client.AnthropicClient')
        mock_class = self.patcher.start()
        mock_class.return_value = self.mock_client
        return self.mock_client
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.patcher:
            self.patcher.stop()


# Convenience functions for common mocking scenarios
def mock_successful_cv_parsing(cv_data: Dict[str, Any]):
    """Context manager for successful CV parsing"""
    mock_client = AnthropicMockFactory.create_cv_parsing_mock(cv_data)
    return MockAnthropicClient(mock_client)


def mock_anthropic_unavailable():
    """Context manager for unavailable Anthropic API"""
    mock_client = AnthropicMockFactory.create_unavailable_mock()
    return MockAnthropicClient(mock_client)


def mock_anthropic_error(error_message: str):
    """Context manager for Anthropic API errors"""
    mock_client = AnthropicMockFactory.create_error_mock(error_message)
    return MockAnthropicClient(mock_client)