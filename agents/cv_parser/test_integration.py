#!/usr/bin/env python3
"""
Integration tests for CV Parser Agent following GL-Testing-Guidelines

Tests complete workflows and component interactions.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from test.utils import setup_test, create_mock_cv_data, create_mock_file_content, SAMPLE_CVS
from test.mocks import mock_successful_cv_parsing
from agent import CVParserAgent
from cv_parsing_service import CVParsingService


class TestCVParserIntegration(unittest.TestCase):
    """Integration tests for complete CV parsing workflows"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.test_setup = setup_test()
        self.mock_cv_data = create_mock_cv_data()
        
    def tearDown(self):
        """Clean up after each test"""
        self.test_setup.cleanup()
    
    def test_end_to_end_text_parsing_workflow(self):
        """Test complete workflow from text input to parsed result"""
        # ARRANGE
        cv_text = """
        John Smith
        Senior Software Engineer
        john.smith@email.com
        (555) 123-4567
        San Francisco, CA
        
        EXPERIENCE:
        - Senior Developer at TechCorp (2020-2024)
        - Built React applications with 100K+ users
        - Led team of 3 developers
        
        SKILLS:
        Python, JavaScript, React, Node.js, PostgreSQL
        
        EDUCATION:
        BS Computer Science - UC Berkeley (2020)
        """
        
        with mock_successful_cv_parsing(self.mock_cv_data):
            agent = CVParserAgent()
            
            # ACT
            result = agent.parse_cv(cv_text)
            
            # ASSERT
            self.assertEqual(result.full_name, self.mock_cv_data["full_name"])
            self.assertEqual(result.email, self.mock_cv_data["email"])
            self.assertEqual(result.phone, self.mock_cv_data["phone"])
            self.assertGreater(len(result.key_skills), 0)
            self.assertGreater(len(result.work_experience), 0)
    
    def test_end_to_end_pdf_parsing_workflow(self):
        """Test complete workflow from PDF file to parsed result"""
        # ARRANGE
        pdf_content = create_mock_file_content("pdf")
        filename = "john_smith_cv.pdf"
        
        with mock_successful_cv_parsing(self.mock_cv_data):
            agent = CVParserAgent()
            
            # ACT
            result = agent.parse_cv_file(pdf_content, filename)
            
            # ASSERT
            self.assertEqual(result.full_name, self.mock_cv_data["full_name"])
            self.assertEqual(result.email, self.mock_cv_data["email"])
    
    def test_service_to_agent_integration(self):
        """Test integration between CVParsingService and CVParserAgent"""
        # ARRANGE
        with mock_successful_cv_parsing(self.mock_cv_data):
            service = CVParsingService()
            agent = CVParserAgent()
            
            cv_text = "John Smith\nSoftware Engineer"
            
            # ACT - Test service directly
            service_result = service.parse_text(cv_text)
            
            # ACT - Test agent using service
            agent_result = agent.parse_cv(cv_text)
            
            # ASSERT - Both should produce consistent results
            self.assertTrue(service_result["success"])
            self.assertEqual(agent_result.full_name, service_result["result"]["full_name"])
    
    def test_fallback_integration_when_llm_unavailable(self):
        """Test integration with fallback parser when LLM is unavailable"""
        # ARRANGE
        cv_text = "John Smith\njohn@email.com\n(555) 123-4567\nPython, JavaScript"
        
        with patch('llm_integration.anthropic_client.AnthropicClient') as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.is_available.return_value = False
            
            agent = CVParserAgent()
            
            # ACT
            result = agent.parse_cv(cv_text)
            
            # ASSERT
            self.assertIsNotNone(result.full_name)
            self.assertIn("FALLBACK MODE", str(result.parsing_notes))
    
    def test_security_integration_workflow(self):
        """Test integration of security validation in parsing workflow"""
        # ARRANGE
        malicious_text = "John Smith<script>alert('xss')</script>\njohn@email.com"
        
        with mock_successful_cv_parsing(self.mock_cv_data):
            agent = CVParserAgent()
            
            # ACT
            result = agent.parse_cv(malicious_text)
            
            # ASSERT
            # Should parse successfully after sanitization
            self.assertEqual(result.full_name, self.mock_cv_data["full_name"])
            self.assertEqual(result.email, self.mock_cv_data["email"])
    
    def test_prompt_management_integration(self):
        """Test integration of prompt management with parsing"""
        # ARRANGE
        custom_prompt = "Extract only name and email from: {cv_text}"
        cv_text = "John Smith\njohn@email.com\nSoftware Engineer"
        
        with mock_successful_cv_parsing(self.mock_cv_data):
            agent = CVParserAgent()
            
            # ACT - Update prompt
            agent.update_prompt(custom_prompt)
            current_prompt = agent.get_prompt()
            
            # Parse with custom prompt
            result = agent.parse_cv(cv_text)
            
            # ASSERT
            self.assertEqual(current_prompt, custom_prompt)
            self.assertEqual(result.full_name, self.mock_cv_data["full_name"])
    
    def test_batch_processing_integration(self):
        """Test processing multiple CVs in sequence"""
        # ARRANGE
        cv_texts = [
            "Alice Johnson\nalice@email.com\nPython Developer",
            "Bob Wilson\nbob@email.com\nJavaScript Developer", 
            "Carol Davis\ncarol@email.com\nJava Developer"
        ]
        
        with mock_successful_cv_parsing(self.mock_cv_data):
            agent = CVParserAgent()
            results = []
            
            # ACT
            for cv_text in cv_texts:
                result = agent.parse_cv(cv_text)
                results.append(result)
            
            # ASSERT
            self.assertEqual(len(results), 3)
            for result in results:
                self.assertIsNotNone(result.full_name)
                self.assertIsNotNone(result.email)
    
    def test_error_handling_integration(self):
        """Test error handling across integrated components"""
        # ARRANGE
        cv_text = "John Smith\njohn@email.com"
        
        with patch('llm_integration.anthropic_client.AnthropicClient') as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.is_available.return_value = True
            mock_client.call_text_api.side_effect = Exception("API Error")
            
            agent = CVParserAgent()
            
            # ACT & ASSERT
            with self.assertRaises(Exception):
                agent.parse_cv(cv_text)
    
    def test_file_type_detection_integration(self):
        """Test file type detection and routing integration"""
        # ARRANGE
        pdf_content = create_mock_file_content("pdf")
        txt_content = create_mock_file_content("txt") 
        
        with mock_successful_cv_parsing(self.mock_cv_data):
            agent = CVParserAgent()
            
            # ACT
            pdf_result = agent.parse_cv_file(pdf_content, "cv.pdf")
            txt_result = agent.parse_cv_file(txt_content, "cv.txt")
            
            # ASSERT
            self.assertEqual(pdf_result.full_name, self.mock_cv_data["full_name"])
            self.assertEqual(txt_result.full_name, self.mock_cv_data["full_name"])
    
    def test_address_markup_integration(self):
        """Test address markup integration in parsing workflow"""
        # ARRANGE
        cv_text = "John Smith\n123 Main St, San Francisco, CA 94105\njohn@email.com"
        
        with mock_successful_cv_parsing(self.mock_cv_data):
            agent = CVParserAgent()
            
            # ACT
            result = agent.parse_cv(cv_text)
            
            # ASSERT
            self.assertEqual(result.full_name, self.mock_cv_data["full_name"])
            # Address markup should be applied in the raw_text field
            self.assertIsNotNone(result.raw_text)


class TestPerformanceIntegration(unittest.TestCase):
    """Performance-focused integration tests"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.test_setup = setup_test()
        
    def tearDown(self):
        """Clean up after each test"""
        self.test_setup.cleanup()
    
    def test_parsing_performance_baseline(self):
        """Test parsing performance meets acceptable baseline"""
        # ARRANGE
        import time
        cv_data = create_mock_cv_data()
        cv_text = "John Smith\njohn@email.com\nSoftware Engineer with Python and JavaScript"
        
        with mock_successful_cv_parsing(cv_data):
            agent = CVParserAgent()
            
            # ACT
            start_time = time.time()
            result = agent.parse_cv(cv_text)
            end_time = time.time()
            
            # ASSERT
            processing_time = end_time - start_time
            self.assertLess(processing_time, 5.0)  # Should complete within 5 seconds
            self.assertIsNotNone(result.full_name)
    
    def test_large_cv_handling(self):
        """Test handling of large CV content"""
        # ARRANGE
        large_cv_text = "John Smith\n" + "Experience: " * 1000 + "\nPython, JavaScript"
        cv_data = create_mock_cv_data()
        
        with mock_successful_cv_parsing(cv_data):
            agent = CVParserAgent()
            
            # ACT & ASSERT
            # Should not raise memory or timeout errors
            result = agent.parse_cv(large_cv_text)
            self.assertIsNotNone(result.full_name)


if __name__ == '__main__':
    unittest.main()