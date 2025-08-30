#!/usr/bin/env python3
"""
Core Agent Functionality Tests for JD Parser Agent

Tests the main JDParserAgent class functionality including initialization,
configuration, parsing workflows, and error handling.
Follows development guidelines with <200 lines and focused testing.
"""

import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

# Import agent and test utilities
from agent import JDParserAgent, ParsedJobDescription
from test_utils import TestUtils, SAMPLE_JD_TEXT, SAMPLE_PARSED_JD, MockContextManager


class TestJDParserAgent(unittest.TestCase):
    """Test core JD Parser Agent functionality"""
    
    def setUp(self):
        """Set up test environment before each test"""
        TestUtils.setup_test_environment()
        self.agent = JDParserAgent()
    
    def test_agent_initialization(self):
        """Test agent initializes with correct defaults"""
        self.assertEqual(self.agent.version, "2.0.0")
        self.assertTrue(self.agent.agent_id.startswith("jd_parser_"))
        self.assertEqual(self.agent.llm_provider, "anthropic")
        self.assertEqual(self.agent.model_name, "claude-3-haiku-20240307")
        self.assertIsNotNone(self.agent.parsing_prompt)
    
    def test_agent_initialization_with_config(self):
        """Test agent initialization with custom config"""
        config = {
            'llm_provider': 'openai',
            'model_name': 'gpt-4',
            'temperature': 0.2
        }
        agent = JDParserAgent(config)
        
        self.assertEqual(agent.llm_provider, 'openai')
        self.assertEqual(agent.model_name, 'gpt-4')
        self.assertEqual(agent.temperature, 0.2)
    
    @patch('agent_llm_core.requests.post')
    def test_parse_job_description_success(self, mock_post):
        """Test successful job description parsing"""
        # Mock successful API response
        mock_response = TestUtils.create_mock_llm_response(SAMPLE_PARSED_JD)
        mock_post.return_value = mock_response
        
        result = self.agent.parse_job_description(SAMPLE_JD_TEXT)
        
        self.assertIsInstance(result, ParsedJobDescription)
        self.assertEqual(result.job_title, "Senior Software Engineer - Full Stack")
        self.assertEqual(result.company_name, "TechCorp Solutions")
        self.assertEqual(result.confidence_score, 0.95)
        self.assertTrue(len(result.required_skills) > 0)
    
    def test_parse_job_description_empty_input(self):
        """Test parsing with empty or short input"""
        result = self.agent.parse_job_description("")
        
        self.assertIsInstance(result, ParsedJobDescription)
        self.assertEqual(result.job_title, "Parsing Error")
        self.assertEqual(result.confidence_score, 0.0)
        self.assertTrue(any("too short" in note.lower() for note in result.parsing_notes))
    
    def test_parse_job_description_short_input(self):
        """Test parsing with too short input"""
        short_text = "Job"
        result = self.agent.parse_job_description(short_text)
        
        self.assertEqual(result.job_title, "Parsing Error")
        self.assertEqual(result.confidence_score, 0.0)
    
    @patch('agent_llm_core.requests.post')
    def test_parse_job_description_api_error(self, mock_post):
        """Test handling of API errors"""
        mock_post.side_effect = Exception("API connection failed")
        
        result = self.agent.parse_job_description(SAMPLE_JD_TEXT)
        
        self.assertEqual(result.job_title, "Parsing Error")
        self.assertEqual(result.confidence_score, 0.0)
        self.assertTrue(any("API connection failed" in note for note in result.parsing_notes))
    
    def test_prompt_management(self):
        """Test prompt loading and updating"""
        original_prompt = self.agent.get_prompt()
        self.assertIsInstance(original_prompt, str)
        self.assertTrue(len(original_prompt) > 100)
        
        new_prompt = "Test prompt for job description parsing"
        self.agent.update_prompt(new_prompt)
        
        self.assertEqual(self.agent.get_prompt(), new_prompt)
    
    def test_save_and_load_default_prompt(self):
        """Test saving and loading default prompt"""
        test_prompt = "Custom test prompt for parsing"
        
        # Create temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = Path(f.name)
        
        # Override prompt file path for testing
        original_path = self.agent.prompt_file
        self.agent.prompt_file = temp_path
        
        try:
            # Test saving
            success = self.agent.save_as_default_prompt(test_prompt)
            self.assertTrue(success)
            
            # Test loading
            self.agent.parsing_prompt = self.agent._load_default_prompt()
            self.assertEqual(self.agent.parsing_prompt, test_prompt)
            
        finally:
            # Cleanup
            self.agent.prompt_file = original_path
            if temp_path.exists():
                temp_path.unlink()
    
    def test_get_agent_info(self):
        """Test agent information retrieval"""
        info = self.agent.get_agent_info()
        
        self.assertIsInstance(info, dict)
        self.assertEqual(info['version'], "2.0.0")
        self.assertTrue(info['agent_id'].startswith("jd_parser_"))
        self.assertIn('config', info)
        self.assertEqual(info['status'], 'active')
        self.assertIn('capabilities', info)
    
    def test_validate_parsed_data(self):
        """Test parsed data validation"""
        # Test valid data
        valid_data = {
            'job_title': 'Software Engineer',
            'company_name': 'Test Corp',
            'required_skills': ['Python', 'JavaScript']
        }
        validation = self.agent.validate_parsed_data(valid_data)
        self.assertTrue(validation['is_valid'])
        self.assertEqual(validation['score'], 1.0)
        
        # Test missing critical fields
        invalid_data = {}
        validation = self.agent.validate_parsed_data(invalid_data)
        self.assertFalse(validation['is_valid'])
        self.assertLess(validation['score'], 0.5)
    
    def test_to_dict_conversion(self):
        """Test conversion of ParsedJobDescription to dictionary"""
        # Create test result
        result = ParsedJobDescription(
            job_title="Test Job",
            company_name="Test Company",
            location="Test Location",
            job_summary=["Test summary"],
            required_skills=["Python"],
            preferred_skills=[],
            required_experience=["3 years"],
            required_education=["Bachelor's"],
            required_qualifications=[],
            preferred_qualifications=[],
            key_responsibilities=["Write code"],
            work_environment=[],
            company_info=[],
            team_info=[],
            benefits=[],
            confidence_score=0.9,
            parsing_notes=[],
            raw_text="Test raw text"
        )
        
        result_dict = self.agent.to_dict(result)
        
        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict['job_title'], "Test Job")
        self.assertEqual(result_dict['company_name'], "Test Company")
        self.assertEqual(result_dict['confidence_score'], 0.9)
    
    def test_to_json_conversion(self):
        """Test JSON conversion"""
        result = ParsedJobDescription(
            job_title="Test Job",
            company_name="Test Company",
            location="",
            job_summary=[],
            required_skills=[],
            preferred_skills=[],
            required_experience=[],
            required_education=[],
            required_qualifications=[],
            preferred_qualifications=[],
            key_responsibilities=[],
            work_environment=[],
            company_info=[],
            team_info=[],
            benefits=[],
            confidence_score=0.8,
            parsing_notes=[]
        )
        
        json_str = self.agent.to_json(result)
        self.assertIsInstance(json_str, str)
        self.assertIn('"job_title": "Test Job"', json_str)
        self.assertIn('"confidence_score": 0.8', json_str)


if __name__ == '__main__':
    unittest.main()