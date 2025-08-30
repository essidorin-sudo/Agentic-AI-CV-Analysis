#!/usr/bin/env python3
"""
Test Utilities for JD Parser Agent

Provides common test utilities, fixtures, and mock data for testing
the JD Parser Agent components following development guidelines.
"""

import json
import os
from unittest.mock import Mock, patch
from typing import Dict, Any, List
from dataclasses import asdict

# Test data fixtures
SAMPLE_JD_TEXT = """Senior Software Engineer - Full Stack
TechCorp Solutions

Join our innovative team as a Senior Software Engineer where you'll build scalable web applications.

Key Responsibilities:
• Design and develop full-stack web applications using React and Node.js
• Lead code reviews and mentor junior developers
• Collaborate with product managers and designers

Required Qualifications:
• Bachelor's degree in Computer Science or related field
• 5+ years of software development experience
• Proficiency in JavaScript, Python, and SQL
• Experience with React, Node.js, and cloud platforms (AWS/Azure)

Preferred Qualifications:
• Master's degree in Computer Science
• Experience with Docker and Kubernetes
• Previous startup experience

We offer competitive salary ($120k-160k), comprehensive health benefits, equity package."""

SAMPLE_PARSED_JD = {
    "job_title": "Senior Software Engineer - Full Stack",
    "company_name": "TechCorp Solutions",
    "location": "",
    "job_summary": ["Join our innovative team as a Senior Software Engineer where you'll build scalable web applications."],
    "required_skills": ["JavaScript", "Python", "SQL", "React", "Node.js"],
    "preferred_skills": ["Docker", "Kubernetes"],
    "required_experience": ["5+ years of software development experience"],
    "required_education": ["Bachelor's degree in Computer Science or related field"],
    "required_qualifications": [],
    "preferred_qualifications": ["Master's degree in Computer Science", "Previous startup experience"],
    "key_responsibilities": [
        "Design and develop full-stack web applications using React and Node.js",
        "Lead code reviews and mentor junior developers",
        "Collaborate with product managers and designers"
    ],
    "work_environment": [],
    "company_info": [],
    "team_info": [],
    "benefits": ["competitive salary ($120k-160k)", "comprehensive health benefits", "equity package"],
    "confidence_score": 0.95,
    "parsing_notes": []
}

SAMPLE_URL_CONTENT = """
<html>
<head><title>Software Engineer Job - Tech Company</title></head>
<body>
<nav>Navigation menu</nav>
<h1>Software Engineer Position</h1>
<div class="job-description">
We are seeking a talented Software Engineer to join our team.
Requirements: 3+ years Python experience, Bachelor's degree.
Responsibilities: Write code, debug applications, collaborate with team.
</div>
<footer>Company footer</footer>
</body>
</html>
"""

class TestUtils:
    """Utility class for common test operations"""
    
    @staticmethod
    def setup_test_environment():
        """Set up test environment variables"""
        os.environ['ANTHROPIC_API_KEY'] = 'test-api-key-12345'
        os.environ['ENV'] = 'test'
    
    @staticmethod
    def create_mock_response(content: str, status_code: int = 200):
        """Create mock HTTP response"""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.text = content
        mock_response.content = content.encode('utf-8')
        mock_response.raise_for_status = Mock()
        return mock_response
    
    @staticmethod
    def create_mock_llm_response(parsed_data: Dict[str, Any]):
        """Create mock LLM API response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": json.dumps(parsed_data)}]
        }
        return mock_response
    
    @staticmethod
    def create_mock_selenium_driver():
        """Create mock Selenium WebDriver"""
        mock_driver = Mock()
        mock_driver.title = "Test Job Page"
        mock_driver.page_source = SAMPLE_URL_CONTENT
        mock_driver.get = Mock()
        mock_driver.quit = Mock()
        
        # Mock find_element methods
        mock_element = Mock()
        mock_element.text = "Sample job content"
        mock_driver.find_element.return_value = mock_element
        mock_driver.find_elements.return_value = [mock_element]
        
        return mock_driver
    
    @staticmethod
    def validate_parsed_jd_structure(parsed_jd: Dict[str, Any]) -> bool:
        """Validate parsed job description has required structure"""
        required_fields = [
            'job_title', 'company_name', 'location', 'job_summary',
            'required_skills', 'preferred_skills', 'required_experience',
            'required_education', 'required_qualifications', 'preferred_qualifications',
            'key_responsibilities', 'work_environment', 'company_info',
            'team_info', 'benefits', 'confidence_score', 'parsing_notes'
        ]
        
        for field in required_fields:
            if field not in parsed_jd:
                return False
        
        # Validate data types
        if not isinstance(parsed_jd['confidence_score'], (int, float)):
            return False
        
        list_fields = [
            'job_summary', 'required_skills', 'preferred_skills', 'required_experience',
            'required_education', 'required_qualifications', 'preferred_qualifications',
            'key_responsibilities', 'work_environment', 'company_info',
            'team_info', 'benefits', 'parsing_notes'
        ]
        
        for field in list_fields:
            if not isinstance(parsed_jd[field], list):
                return False
        
        return True

class MockContextManager:
    """Context manager for mocking external dependencies"""
    
    def __init__(self):
        self.patches = []
    
    def __enter__(self):
        # Mock requests
        self.mock_requests = patch('requests.get')
        self.mock_get = self.mock_requests.start()
        self.patches.append(self.mock_requests)
        
        # Mock Selenium
        self.mock_webdriver = patch('selenium.webdriver.Chrome')
        self.mock_chrome = self.mock_webdriver.start()
        self.patches.append(self.mock_webdriver)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for patch_obj in self.patches:
            patch_obj.stop()
    
    def set_http_response(self, content: str, status_code: int = 200):
        """Set mock HTTP response"""
        self.mock_get.return_value = TestUtils.create_mock_response(content, status_code)
    
    def set_selenium_driver(self, mock_driver=None):
        """Set mock Selenium driver"""
        if mock_driver is None:
            mock_driver = TestUtils.create_mock_selenium_driver()
        self.mock_chrome.return_value = mock_driver

# Test data constants
ERROR_JD_TEXT = "Too short"  # For testing error handling
EMPTY_JD_TEXT = ""
MALFORMED_JD_TEXT = "Not a proper job description with random text and no structure"

# URL test cases
TEST_URLS = {
    'valid_microsoft': 'https://jobs.careers.microsoft.com/global/en/job/1234567/test-job',
    'valid_generic': 'https://example.com/jobs/software-engineer',
    'invalid_url': 'not-a-url',
    'blocked_url': 'https://blocked-site.com/job/123',
    'timeout_url': 'https://slow-site.com/job/456'
}

# Expected parsing results for different scenarios
EXPECTED_RESULTS = {
    'successful_parse': SAMPLE_PARSED_JD,
    'empty_skills': {**SAMPLE_PARSED_JD, 'required_skills': [], 'preferred_skills': []},
    'low_confidence': {**SAMPLE_PARSED_JD, 'confidence_score': 0.3},
    'parsing_error': {
        'job_title': 'Parsing Error',
        'company_name': 'Unknown',
        'confidence_score': 0.0,
        'parsing_notes': ['Parsing failed: Test error']
    }
}