#!/usr/bin/env python3
"""
Data Models and Validation Tests for JD Parser Agent

Tests the data model structures, validation logic, serialization,
and data integrity for ParsedJobDescription and related components.
Follows development guidelines with <200 lines and focused testing.
"""

import unittest
from dataclasses import asdict

# Import data models and utilities
from agent import ParsedJobDescription, JDParserAgent
from data_models import JDParsingConfig
from test_utils import TestUtils, SAMPLE_PARSED_JD


class TestDataModels(unittest.TestCase):
    """Test data model functionality and validation"""
    
    def setUp(self):
        """Set up test environment"""
        TestUtils.setup_test_environment()
    
    def test_parsed_job_description_creation(self):
        """Test ParsedJobDescription creation with all fields"""
        jd = ParsedJobDescription(
            job_title="Software Engineer",
            company_name="Tech Corp",
            location="San Francisco, CA",
            job_summary=["Build great software"],
            required_skills=["Python", "JavaScript"],
            preferred_skills=["React", "Docker"],
            required_experience=["3+ years development"],
            required_education=["Bachelor's degree"],
            required_qualifications=["Problem solving"],
            preferred_qualifications=["Leadership"],
            key_responsibilities=["Write code", "Review code"],
            work_environment=["Remote friendly"],
            company_info=["Growing startup"],
            team_info=["Agile team"],
            benefits=["Health insurance", "401k"],
            confidence_score=0.9,
            parsing_notes=["High quality parse"],
            raw_text="Original job text"
        )
        
        # Test all fields are set correctly
        self.assertEqual(jd.job_title, "Software Engineer")
        self.assertEqual(jd.company_name, "Tech Corp")
        self.assertEqual(jd.location, "San Francisco, CA")
        self.assertEqual(jd.confidence_score, 0.9)
        self.assertIsInstance(jd.required_skills, list)
        self.assertIsInstance(jd.key_responsibilities, list)
    
    def test_parsed_job_description_defaults(self):
        """Test ParsedJobDescription with minimal fields"""
        jd = ParsedJobDescription(
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
            confidence_score=0.5,
            parsing_notes=[]
        )
        
        self.assertEqual(jd.job_title, "Test Job")
        self.assertEqual(jd.raw_text, "")  # Default value
        self.assertEqual(len(jd.required_skills), 0)
    
    def test_jd_parsing_config(self):
        """Test JDParsingConfig data model"""
        config = JDParsingConfig(
            llm_provider="anthropic",
            model_name="claude-3-haiku-20240307",
            temperature=0.1,
            max_tokens=4000
        )
        
        self.assertEqual(config.llm_provider, "anthropic")
        self.assertEqual(config.model_name, "claude-3-haiku-20240307")
        self.assertEqual(config.temperature, 0.1)
        self.assertEqual(config.max_tokens, 4000)
    
    def test_jd_parsing_config_defaults(self):
        """Test JDParsingConfig with default values"""
        config = JDParsingConfig()
        
        self.assertEqual(config.llm_provider, "anthropic")
        self.assertEqual(config.model_name, "claude-3-haiku-20240307")
        self.assertEqual(config.temperature, 0.1)
        self.assertEqual(config.max_tokens, 4000)
    
    def test_data_model_serialization(self):
        """Test data model serialization to dictionary"""
        jd = ParsedJobDescription(
            job_title="Test Position",
            company_name="Test Inc",
            location="Remote",
            job_summary=["Great opportunity"],
            required_skills=["Python"],
            preferred_skills=[],
            required_experience=["2 years"],
            required_education=["Bachelor's"],
            required_qualifications=[],
            preferred_qualifications=[],
            key_responsibilities=["Develop software"],
            work_environment=[],
            company_info=[],
            team_info=[],
            benefits=["Healthcare"],
            confidence_score=0.85,
            parsing_notes=[]
        )
        
        jd_dict = asdict(jd)
        
        self.assertIsInstance(jd_dict, dict)
        self.assertEqual(jd_dict['job_title'], "Test Position")
        self.assertEqual(jd_dict['confidence_score'], 0.85)
        self.assertIn('required_skills', jd_dict)
    
    def test_data_validation_structure(self):
        """Test data structure validation using TestUtils"""
        valid_data = SAMPLE_PARSED_JD
        is_valid = TestUtils.validate_parsed_jd_structure(valid_data)
        self.assertTrue(is_valid)
        
        # Test invalid structure
        invalid_data = {"job_title": "Test", "missing_fields": True}
        is_valid = TestUtils.validate_parsed_jd_structure(invalid_data)
        self.assertFalse(is_valid)
    
    def test_confidence_score_validation(self):
        """Test confidence score validation"""
        # Test valid confidence scores
        valid_scores = [0.0, 0.5, 0.95, 1.0]
        for score in valid_scores:
            data = {**SAMPLE_PARSED_JD, 'confidence_score': score}
            is_valid = TestUtils.validate_parsed_jd_structure(data)
            self.assertTrue(is_valid, f"Score {score} should be valid")
        
        # Test invalid confidence scores (non-numeric)
        invalid_data = {**SAMPLE_PARSED_JD, 'confidence_score': "high"}
        is_valid = TestUtils.validate_parsed_jd_structure(invalid_data)
        self.assertFalse(is_valid)
    
    def test_list_field_validation(self):
        """Test validation of list fields"""
        list_fields = [
            'job_summary', 'required_skills', 'preferred_skills',
            'required_experience', 'required_education', 'key_responsibilities',
            'benefits', 'parsing_notes'
        ]
        
        for field in list_fields:
            # Test valid list
            data = {**SAMPLE_PARSED_JD, field: ["item1", "item2"]}
            is_valid = TestUtils.validate_parsed_jd_structure(data)
            self.assertTrue(is_valid, f"Field {field} with list should be valid")
            
            # Test invalid non-list
            data = {**SAMPLE_PARSED_JD, field: "not a list"}
            is_valid = TestUtils.validate_parsed_jd_structure(data)
            self.assertFalse(is_valid, f"Field {field} with non-list should be invalid")
    
    def test_string_field_validation(self):
        """Test validation of string fields"""
        string_fields = ['job_title', 'company_name', 'location']
        
        for field in string_fields:
            # Test valid string
            data = {**SAMPLE_PARSED_JD, field: "valid string"}
            is_valid = TestUtils.validate_parsed_jd_structure(data)
            self.assertTrue(is_valid, f"Field {field} with string should be valid")
    
    def test_agent_validation_method(self):
        """Test agent's validate_parsed_data method"""
        agent = JDParserAgent()
        
        # Test complete valid data
        validation = agent.validate_parsed_data(SAMPLE_PARSED_JD)
        self.assertTrue(validation['is_valid'])
        self.assertEqual(validation['score'], 1.0)
        self.assertEqual(len(validation['warnings']), 0)
        
        # Test data missing critical fields
        incomplete_data = {
            'job_title': '',
            'company_name': '',
            'required_skills': []
        }
        validation = agent.validate_parsed_data(incomplete_data)
        self.assertFalse(validation['is_valid'])
        self.assertLess(validation['score'], 0.5)
        self.assertGreater(len(validation['warnings']), 0)
    
    def test_empty_requirements_validation(self):
        """Test validation when no requirements are found"""
        agent = JDParserAgent()
        
        data_no_requirements = {
            **SAMPLE_PARSED_JD,
            'required_skills': [],
            'required_qualifications': []
        }
        
        validation = agent.validate_parsed_data(data_no_requirements)
        self.assertTrue(any("No requirements found" in warning for warning in validation['warnings']))
        self.assertLess(validation['score'], 1.0)
    
    def test_data_model_immutability(self):
        """Test that data models maintain data integrity"""
        original_data = SAMPLE_PARSED_JD.copy()
        
        jd = ParsedJobDescription(**{
            k: v for k, v in original_data.items()
            if k != 'raw_text'  # raw_text has default value
        })
        
        # Modify the dataclass
        jd.job_title = "Modified Title"
        
        # Original data should remain unchanged
        self.assertEqual(original_data['job_title'], "Senior Software Engineer - Full Stack")
        self.assertEqual(jd.job_title, "Modified Title")
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Test valid configs
        valid_configs = [
            {'llm_provider': 'anthropic', 'temperature': 0.1},
            {'llm_provider': 'openai', 'model_name': 'gpt-4'},
            {'temperature': 0.5, 'max_tokens': 3000}
        ]
        
        for config in valid_configs:
            agent = JDParserAgent(config)
            self.assertIsNotNone(agent.config)
    
    def test_edge_case_data_values(self):
        """Test edge cases in data values"""
        # Test with very long strings
        long_title = "Very " * 100 + "Long Job Title"
        
        jd = ParsedJobDescription(
            job_title=long_title,
            company_name="Test",
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
            confidence_score=0.0,
            parsing_notes=[]
        )
        
        self.assertEqual(jd.job_title, long_title)
        
        # Test with special characters
        special_title = "Software Engineer (AI/ML) - Senior Level [Remote] @Company"
        jd.job_title = special_title
        self.assertEqual(jd.job_title, special_title)


if __name__ == '__main__':
    unittest.main()