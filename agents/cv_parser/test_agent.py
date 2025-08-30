#!/usr/bin/env python3
"""
Unit tests for CVParserAgent following GL-Testing-Guidelines

Tests the main agent interface using TDD methodology with shared infrastructure.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, Mock

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from test.utils import setup_test, create_mock_cv_data, create_mock_parsed_cv_object
from test.mocks import AnthropicMockFactory, mock_successful_cv_parsing
from agent import CVParserAgent
from data_models import ParsedCV


class TestCVParserAgent(unittest.TestCase):
    """Test cases for CVParserAgent following TDD methodology"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.test_setup = setup_test()
        self.mock_cv_data = create_mock_cv_data()
        
    def tearDown(self):
        """Clean up after each test"""
        self.test_setup.cleanup()
    
    def test_agent_initialization(self):
        """Test that CVParserAgent initializes correctly"""
        # ACT
        agent = CVParserAgent()
        
        # ASSERT
        self.assertIsInstance(agent, CVParserAgent)
        self.assertEqual(agent.version, "2.0.0")
        self.assertEqual(agent.model_name, "claude-3-5-sonnet-20241022")
        
    def test_parse_cv_text_success(self):
        """Test successful CV text parsing"""
        # ARRANGE
        cv_text = "John Smith\njohn@email.com\n(555) 123-4567\nSoftware Engineer"
        expected_result = self.mock_cv_data
        
        with mock_successful_cv_parsing(expected_result):
            agent = CVParserAgent()
            
            # ACT
            result = agent.parse_cv(cv_text)
            
            # ASSERT
            self.assertIsInstance(result, ParsedCV)
            self.assertEqual(result.full_name, expected_result["full_name"])
            self.assertEqual(result.email, expected_result["email"])
            self.assertEqual(result.phone, expected_result["phone"])
    
    def test_parse_cv_file_success(self):
        """Test successful CV file parsing"""
        # ARRANGE
        file_content = b"Mock PDF content"
        filename = "test_cv.pdf"
        expected_result = self.mock_cv_data
        
        with mock_successful_cv_parsing(expected_result):
            agent = CVParserAgent()
            
            # ACT
            result = agent.parse_cv_file(file_content, filename)
            
            # ASSERT
            self.assertIsInstance(result, ParsedCV)
            self.assertEqual(result.full_name, expected_result["full_name"])
            self.assertEqual(result.email, expected_result["email"])
    
    def test_parse_cv_with_empty_input(self):
        """Test CV parsing with empty text input"""
        # ARRANGE
        agent = CVParserAgent()
        empty_text = ""
        
        # ACT & ASSERT
        with self.assertRaises(ValueError):
            agent.parse_cv(empty_text)
    
    def test_parse_cv_with_api_error(self):
        """Test CV parsing when API returns error"""
        # ARRANGE
        cv_text = "John Smith\njohn@email.com"
        mock_client = AnthropicMockFactory.create_error_mock("API Error")
        
        with patch('agent.CVParsingService') as mock_service:
            mock_service.return_value.parse_text.side_effect = Exception("API Error")
            agent = CVParserAgent()
            
            # ACT & ASSERT
            with self.assertRaises(Exception):
                agent.parse_cv(cv_text)
    
    def test_to_dict_conversion(self):
        """Test converting parsed CV to dictionary"""
        # ARRANGE
        expected_result = self.mock_cv_data
        
        with mock_successful_cv_parsing(expected_result):
            agent = CVParserAgent()
            cv_text = "John Smith\njohn@email.com"
            result = agent.parse_cv(cv_text)
            
            # ACT
            result_dict = result.to_dict() if hasattr(result, 'to_dict') else result.__dict__
            
            # ASSERT
            self.assertIsInstance(result_dict, dict)
            self.assertIn('full_name', result_dict)
            self.assertIn('email', result_dict)
    
    def test_to_json_conversion(self):
        """Test converting parsed CV to JSON"""
        # ARRANGE
        expected_result = self.mock_cv_data
        
        with mock_successful_cv_parsing(expected_result):
            agent = CVParserAgent()
            cv_text = "John Smith\njohn@email.com"
            result = agent.parse_cv(cv_text)
            
            # ACT
            if hasattr(result, 'to_json'):
                json_result = result.to_json()
                
                # ASSERT
                self.assertIsInstance(json_result, str)
                self.assertIn('"full_name"', json_result)
    
    def test_prompt_management_get_current(self):
        """Test getting current parsing prompt"""
        # ARRANGE
        agent = CVParserAgent()
        
        # ACT
        current_prompt = agent.get_prompt()
        
        # ASSERT
        self.assertIsInstance(current_prompt, str)
        self.assertIn("specialized AI agent", current_prompt)
        self.assertIn("JSON object", current_prompt)
    
    def test_prompt_management_update(self):
        """Test updating parsing prompt"""
        # ARRANGE
        agent = CVParserAgent()
        new_prompt = "Test prompt for CV parsing"
        
        # ACT
        result = agent.update_prompt(new_prompt)
        
        # ASSERT
        self.assertTrue(result)
        updated_prompt = agent.get_prompt()
        self.assertEqual(updated_prompt, new_prompt)


if __name__ == '__main__':
    unittest.main()