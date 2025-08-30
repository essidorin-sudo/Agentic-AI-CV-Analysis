#!/usr/bin/env python3
"""
Unit tests for CVParsingService following GL-Testing-Guidelines

Tests the core business logic service using TDD methodology.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, Mock

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from test.utils import setup_test, create_mock_cv_data, create_mock_file_content
from test.mocks import AnthropicMockFactory, mock_successful_cv_parsing
from cv_parsing_service import CVParsingService


class TestCVParsingService(unittest.TestCase):
    """Test cases for CVParsingService core business logic"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.test_setup = setup_test()
        self.service = CVParsingService()
        self.mock_cv_data = create_mock_cv_data()
        
    def tearDown(self):
        """Clean up after each test"""
        self.test_setup.cleanup()
    
    def test_service_initialization(self):
        """Test that CVParsingService initializes with all components"""
        # ACT
        service = CVParsingService()
        
        # ASSERT
        self.assertIsNotNone(service.validator)
        self.assertIsNotNone(service.doc_processor)
        self.assertIsNotNone(service.text_markup)
        self.assertIsNotNone(service.prompt_manager)
        self.assertIsNotNone(service.llm_client)
        self.assertIsNotNone(service.fallback_parser)
        self.assertIsNotNone(service.result_builder)
    
    def test_parse_text_success_with_llm(self):
        """Test successful text parsing using LLM"""
        # ARRANGE
        cv_text = "John Smith\njohn@email.com\n(555) 123-4567"
        
        with mock_successful_cv_parsing(self.mock_cv_data):
            # ACT
            result = self.service.parse_text(cv_text)
            
            # ASSERT
            self.assertTrue(result["success"])
            self.assertIn("result", result)
            result_data = result["result"]
            self.assertEqual(result_data["full_name"], self.mock_cv_data["full_name"])
            self.assertEqual(result_data["email"], self.mock_cv_data["email"])
    
    def test_parse_text_fallback_when_llm_unavailable(self):
        """Test text parsing falls back when LLM is unavailable"""
        # ARRANGE
        cv_text = "John Smith\njohn@email.com\n(555) 123-4567"
        
        with patch.object(self.service.llm_client, 'is_available', return_value=False):
            with patch.object(self.service.fallback_parser, 'parse_text_fallback') as mock_fallback:
                mock_fallback.return_value = self.mock_cv_data
                
                # ACT
                result = self.service.parse_text(cv_text)
                
                # ASSERT
                mock_fallback.assert_called_once()
                self.assertTrue(result["success"])
    
    def test_parse_text_with_invalid_input(self):
        """Test text parsing with invalid input"""
        # ARRANGE
        invalid_text = ""
        
        # ACT
        result = self.service.parse_text(invalid_text)
        
        # ASSERT
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_parse_file_pdf_success(self):
        """Test successful PDF file parsing"""
        # ARRANGE
        file_content = create_mock_file_content("pdf")
        filename = "test_cv.pdf"
        
        with mock_successful_cv_parsing(self.mock_cv_data):
            # ACT
            result = self.service.parse_file(file_content, filename)
            
            # ASSERT
            self.assertTrue(result["success"])
            self.assertIn("result", result)
    
    def test_parse_file_text_file(self):
        """Test parsing text file (.txt)"""
        # ARRANGE
        file_content = create_mock_file_content("txt")
        filename = "test_cv.txt"
        
        with mock_successful_cv_parsing(self.mock_cv_data):
            # ACT
            result = self.service.parse_file(file_content, filename)
            
            # ASSERT
            self.assertTrue(result["success"])
    
    def test_requires_llm_processing_detection(self):
        """Test detection of files requiring LLM processing"""
        # ARRANGE & ACT
        pdf_requires_llm = self.service._requires_llm_processing("document.pdf")
        docx_requires_llm = self.service._requires_llm_processing("document.docx")
        txt_requires_llm = self.service._requires_llm_processing("document.txt")
        
        # ASSERT
        self.assertTrue(pdf_requires_llm)
        self.assertTrue(docx_requires_llm)
        self.assertFalse(txt_requires_llm)
    
    def test_process_file_with_llm_unavailable(self):
        """Test file processing when LLM is unavailable"""
        # ARRANGE
        file_content = create_mock_file_content("pdf")
        filename = "test_cv.pdf"
        
        with patch.object(self.service.llm_client, 'is_available', return_value=False):
            # ACT
            result = self.service._process_file_with_llm(file_content, filename)
            
            # ASSERT
            self.assertFalse(result["success"])
            self.assertIn("LLM processing required but not available", result["error"])
    
    def test_process_with_llm_success(self):
        """Test direct LLM processing of sanitized text"""
        # ARRANGE
        sanitized_text = "John Smith\nSoftware Engineer"
        
        with mock_successful_cv_parsing(self.mock_cv_data):
            # ACT
            result = self.service._process_with_llm(sanitized_text)
            
            # ASSERT
            self.assertEqual(result["full_name"], self.mock_cv_data["full_name"])
    
    def test_text_validation_and_sanitization(self):
        """Test text input validation and sanitization"""
        # ARRANGE
        malicious_text = "John Smith<script>alert('hack')</script>"
        
        with patch.object(self.service.validator, 'validate_text_input') as mock_validate:
            mock_validate.return_value = {
                "is_valid": True,
                "sanitized_text": "John Smith"
            }
            
            with mock_successful_cv_parsing(self.mock_cv_data):
                # ACT
                result = self.service.parse_text(malicious_text)
                
                # ASSERT
                mock_validate.assert_called_once_with(malicious_text)
                self.assertTrue(result["success"])
    
    def test_address_markup_integration(self):
        """Test that address markup is applied to text"""
        # ARRANGE
        cv_text = "John Smith\n123 Main St, San Francisco, CA"
        
        with patch.object(self.service.text_markup, 'add_address_markup') as mock_markup:
            mock_markup.return_value = "John Smith\n<addr>123 Main St, San Francisco, CA</addr>"
            
            with mock_successful_cv_parsing(self.mock_cv_data):
                # ACT
                result = self.service.parse_text(cv_text)
                
                # ASSERT
                mock_markup.assert_called_once()
                self.assertTrue(result["success"])


if __name__ == '__main__':
    unittest.main()