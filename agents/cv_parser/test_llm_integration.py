#!/usr/bin/env python3
"""
Unit tests for LLM Integration modules following GL-Testing-Guidelines

Tests Anthropic client, response processing, and prompt management.
"""

import unittest
import sys
import json
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from test.utils import setup_test, create_mock_cv_data
from test.mocks import AnthropicMockFactory
from llm_integration.anthropic_client import AnthropicClient
from llm_integration.response_processor import ResponseProcessor
from llm_integration.prompt_manager import PromptManager


class TestAnthropicClient(unittest.TestCase):
    """Test cases for Anthropic API client"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.test_setup = setup_test()
        self.mock_cv_data = create_mock_cv_data()
        
    def tearDown(self):
        """Clean up after each test"""
        self.test_setup.cleanup()
    
    def test_client_initialization_with_api_key(self):
        """Test client initializes correctly with API key"""
        # ARRANGE & ACT
        client = AnthropicClient()
        
        # ASSERT
        self.assertEqual(client.model_name, "claude-3-5-sonnet-20241022")
        self.assertEqual(client.max_retries, 3)
        self.assertEqual(client.base_delay, 1.0)
        self.assertIsNotNone(client.response_processor)
    
    def test_is_available_with_api_key(self):
        """Test client availability check with valid API key"""
        # ARRANGE & ACT
        client = AnthropicClient()
        is_available = client.is_available()
        
        # ASSERT
        self.assertTrue(is_available)  # Should be true with test API key
    
    @patch.dict('os.environ', {}, clear=True)
    def test_is_available_without_api_key(self):
        """Test client availability check without API key"""
        # ARRANGE & ACT
        client = AnthropicClient()
        is_available = client.is_available()
        
        # ASSERT
        self.assertFalse(is_available)
    
    @patch('requests.post')
    def test_call_text_api_success(self, mock_post):
        """Test successful text API call"""
        # ARRANGE
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": json.dumps(self.mock_cv_data)}]
        }
        mock_post.return_value = mock_response
        
        client = AnthropicClient()
        prompt = "Parse this CV: John Smith, Software Engineer"
        
        # ACT
        result = client.call_text_api(prompt)
        
        # ASSERT
        self.assertEqual(result["full_name"], self.mock_cv_data["full_name"])
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_call_file_api_success(self, mock_post):
        """Test successful file API call"""
        # ARRANGE
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": json.dumps(self.mock_cv_data)}]
        }
        mock_post.return_value = mock_response
        
        client = AnthropicClient()
        file_content = b"Mock PDF content"
        filename = "test_cv.pdf"
        prompt_template = "Parse this CV: {cv_text}"
        
        # ACT
        result = client.call_file_api(file_content, filename, prompt_template)
        
        # ASSERT
        self.assertEqual(result["full_name"], self.mock_cv_data["full_name"])
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_api_call_with_rate_limit(self, mock_post):
        """Test API call handling rate limit errors"""
        # ARRANGE
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'retry-after': '1'}
        mock_response.json.return_value = {"error": {"message": "Rate limit exceeded"}}
        mock_post.return_value = mock_response
        
        client = AnthropicClient()
        
        # ACT & ASSERT
        with self.assertRaises(Exception):
            client.call_text_api("test prompt")
    
    @patch('requests.post')
    def test_api_call_with_timeout(self, mock_post):
        """Test API call handling timeout errors"""
        # ARRANGE
        import requests
        mock_post.side_effect = requests.Timeout("Request timeout")
        
        client = AnthropicClient()
        
        # ACT & ASSERT
        with self.assertRaises(Exception):
            client.call_text_api("test prompt")
    
    def test_get_media_type_pdf(self):
        """Test media type detection for PDF"""
        # ARRANGE
        client = AnthropicClient()
        
        # ACT
        media_type = client._get_media_type("document.pdf")
        
        # ASSERT
        self.assertEqual(media_type, "application/pdf")
    
    def test_get_media_type_docx(self):
        """Test media type detection for DOCX"""
        # ARRANGE
        client = AnthropicClient()
        
        # ACT
        media_type = client._get_media_type("document.docx")
        
        # ASSERT
        self.assertEqual(media_type, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    
    def test_build_file_request_data(self):
        """Test building file request data structure"""
        # ARRANGE
        client = AnthropicClient()
        file_base64 = "dGVzdCBjb250ZW50"  # "test content" in base64
        media_type = "application/pdf"
        prompt_template = "Parse: {cv_text}"
        
        # ACT
        request_data = client._build_file_request_data(file_base64, media_type, prompt_template)
        
        # ASSERT
        self.assertEqual(request_data["model"], "claude-3-5-sonnet-20241022")
        self.assertEqual(request_data["max_tokens"], 8000)
        self.assertIn("messages", request_data)


class TestResponseProcessor(unittest.TestCase):
    """Test cases for LLM response processing"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.test_setup = setup_test()
        self.processor = ResponseProcessor()
        self.mock_cv_data = create_mock_cv_data()
        
    def tearDown(self):
        """Clean up after each test"""
        self.test_setup.cleanup()
    
    def test_processor_initialization(self):
        """Test ResponseProcessor initializes with fallback structure"""
        # ARRANGE & ACT
        processor = ResponseProcessor()
        
        # ASSERT
        self.assertIsNotNone(processor.fallback_structure)
        self.assertIn("full_name", processor.fallback_structure)
        self.assertIn("email", processor.fallback_structure)
    
    def test_parse_json_response_success(self):
        """Test successful JSON response parsing"""
        # ARRANGE
        json_response = json.dumps(self.mock_cv_data)
        
        # ACT
        result = self.processor.parse_json_response(json_response)
        
        # ASSERT
        self.assertEqual(result["full_name"], self.mock_cv_data["full_name"])
        self.assertEqual(result["email"], self.mock_cv_data["email"])
    
    def test_parse_json_response_with_markdown(self):
        """Test parsing JSON response wrapped in markdown"""
        # ARRANGE
        markdown_response = f"```json\n{json.dumps(self.mock_cv_data)}\n```"
        
        # ACT
        result = self.processor.parse_json_response(markdown_response)
        
        # ASSERT
        self.assertEqual(result["full_name"], self.mock_cv_data["full_name"])
    
    def test_parse_json_response_malformed(self):
        """Test parsing malformed JSON response"""
        # ARRANGE
        malformed_json = '{"full_name": "John Smith", "email": incomplete...'
        
        # ACT
        result = self.processor.parse_json_response(malformed_json)
        
        # ASSERT
        self.assertIn("parsing_notes", result)
        self.assertIn("JSON parsing failed", str(result["parsing_notes"]))
    
    def test_clean_json_response_removes_markdown(self):
        """Test JSON cleaning removes markdown formatting"""
        # ARRANGE
        markdown_json = "```json\n{\"key\": \"value\"}\n```"
        
        # ACT
        cleaned = self.processor._clean_json_response(markdown_json)
        
        # ASSERT
        self.assertEqual(cleaned.strip(), '{"key": "value"}')
    
    def test_clean_json_response_removes_extra_text(self):
        """Test JSON cleaning removes extra explanatory text"""
        # ARRANGE
        text_with_json = "Here's the parsed CV:\n{\"full_name\": \"John\"}\nHope this helps!"
        
        # ACT
        cleaned = self.processor._clean_json_response(text_with_json)
        
        # ASSERT
        self.assertIn('{"full_name": "John"}', cleaned)
        self.assertNotIn("Here's the parsed CV", cleaned)
    
    def test_validate_response_structure_complete(self):
        """Test response structure validation with complete data"""
        # ARRANGE
        complete_data = self.mock_cv_data.copy()
        
        # ACT
        validated = self.processor.validate_response_structure(complete_data)
        
        # ASSERT
        self.assertEqual(validated["full_name"], complete_data["full_name"])
        self.assertIsInstance(validated["key_skills"], list)
    
    def test_validate_response_structure_missing_fields(self):
        """Test response structure validation with missing fields"""
        # ARRANGE
        incomplete_data = {"full_name": "John Smith"}
        
        # ACT
        validated = self.processor.validate_response_structure(incomplete_data)
        
        # ASSERT
        self.assertEqual(validated["full_name"], "John Smith")
        self.assertEqual(validated["email"], "")  # Should fill missing fields
        self.assertIsInstance(validated["key_skills"], list)
    
    def test_attempt_json_repair(self):
        """Test JSON repair attempts for malformed responses"""
        # ARRANGE
        malformed_json = '{"full_name": "John Smith", "email": "john@email.com", incomplete'
        
        # ACT
        result = self.processor._attempt_json_repair(malformed_json)
        
        # ASSERT
        self.assertIsInstance(result, dict)
        self.assertIn("full_name", result)
        self.assertIn("parsing_notes", result)


class TestPromptManager(unittest.TestCase):
    """Test cases for prompt management"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.test_setup = setup_test()
        self.temp_dir = Path(self.test_setup.test_setup.create_temp_file("", ".txt")).parent
        self.manager = PromptManager(self.temp_dir)
        
    def tearDown(self):
        """Clean up after each test"""
        self.test_setup.cleanup()
    
    def test_manager_initialization(self):
        """Test PromptManager initializes with proper paths"""
        # ARRANGE & ACT
        manager = PromptManager(self.temp_dir)
        
        # ASSERT
        self.assertEqual(manager.base_path, self.temp_dir)
        self.assertTrue(str(manager.prompt_file).endswith('default_prompt.txt'))
    
    def test_get_current_prompt_loads_default(self):
        """Test getting current prompt loads from file"""
        # ARRANGE & ACT
        prompt = self.manager.get_current_prompt()
        
        # ASSERT
        self.assertIsInstance(prompt, str)
        self.assertIn("specialized AI agent", prompt)
        self.assertIn("JSON object", prompt)
    
    def test_save_custom_prompt(self):
        """Test saving custom prompt to file"""
        # ARRANGE
        custom_prompt = "Custom CV parsing prompt for testing"
        
        # ACT
        success = self.manager.save_custom_prompt(custom_prompt)
        
        # ASSERT
        self.assertTrue(success)
        
        # Verify it was saved
        loaded_prompt = self.manager.get_current_prompt()
        self.assertEqual(loaded_prompt, custom_prompt)
    
    def test_update_prompt_success(self):
        """Test updating the current prompt"""
        # ARRANGE
        new_prompt = "Updated prompt for CV parsing"
        
        # ACT
        success = self.manager.update_prompt(new_prompt)
        
        # ASSERT
        self.assertTrue(success)
        self.assertEqual(self.manager.current_prompt, new_prompt)
    
    def test_reset_to_default_prompt(self):
        """Test resetting prompt to default"""
        # ARRANGE
        custom_prompt = "Temporary custom prompt"
        self.manager.update_prompt(custom_prompt)
        
        # ACT
        success = self.manager.reset_to_default_prompt()
        
        # ASSERT
        self.assertTrue(success)
        self.assertNotEqual(self.manager.current_prompt, custom_prompt)


if __name__ == '__main__':
    unittest.main()