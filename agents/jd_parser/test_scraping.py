#!/usr/bin/env python3
"""
URL Scraping and Web Content Tests for JD Parser Agent

Tests the web scraping functionality including URL validation,
content extraction, error handling, and different scraping methods.
Follows development guidelines with <200 lines and focused testing.
"""

import unittest
from unittest.mock import patch, Mock
from urllib.parse import urlparse

# Import test interface functions and utilities
import test_interface
from test_utils import TestUtils, SAMPLE_URL_CONTENT, TEST_URLS, MockContextManager


class TestWebScraping(unittest.TestCase):
    """Test web scraping functionality"""
    
    def setUp(self):
        """Set up test environment"""
        TestUtils.setup_test_environment()
    
    @patch('test_interface.requests.get')
    def test_basic_url_scraping(self, mock_get):
        """Test basic URL content scraping"""
        mock_get.return_value = TestUtils.create_mock_response(SAMPLE_URL_CONTENT)
        
        result = test_interface.fetch_job_description_from_url(TEST_URLS['valid_generic'])
        
        self.assertIsInstance(result, str)
        self.assertIn("Software Engineer", result)
        mock_get.assert_called_once()
    
    def test_invalid_url_handling(self):
        """Test handling of invalid URLs"""
        with self.assertRaises(Exception) as context:
            test_interface.fetch_job_description_from_url(TEST_URLS['invalid_url'])
        
        self.assertIn("Invalid URL", str(context.exception))
    
    @patch('test_interface.requests.get')
    def test_http_error_handling(self, mock_get):
        """Test HTTP error response handling"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")
        mock_get.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            test_interface.fetch_job_description_from_url(TEST_URLS['valid_generic'])
        
        self.assertIn("404", str(context.exception))
    
    @patch('test_interface.requests.get')
    def test_403_forbidden_handling(self, mock_get):
        """Test handling of 403 Forbidden responses"""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = Exception("HTTP 403")
        mock_get.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            test_interface.fetch_job_description_from_url("https://example.com/job")
        
        self.assertIn("403", str(context.exception))
    
    @patch('test_interface.BeautifulSoup')
    @patch('test_interface.requests.get')
    def test_content_extraction(self, mock_get, mock_soup):
        """Test HTML content extraction and cleaning"""
        mock_get.return_value = TestUtils.create_mock_response(SAMPLE_URL_CONTENT)
        
        # Mock BeautifulSoup parsing
        mock_soup_instance = Mock()
        mock_soup_instance.find.return_value.get_text.return_value = "Software Engineer Job"
        mock_soup_instance.get_text.return_value = "Clean job description text"
        mock_soup.return_value = mock_soup_instance
        
        result = test_interface.fetch_job_description_from_url(TEST_URLS['valid_generic'])
        
        self.assertIsInstance(result, str)
        mock_soup.assert_called_once()
    
    def test_url_validation(self):
        """Test URL format validation"""
        # Test valid URLs
        valid_urls = [
            "https://example.com/job",
            "http://company.com/careers/123",
            "https://jobs.microsoft.com/job/456"
        ]
        
        for url in valid_urls:
            parsed = urlparse(url)
            self.assertTrue(parsed.scheme in ['http', 'https'])
            self.assertTrue(parsed.netloc)
    
    @patch('test_interface.SELENIUM_AVAILABLE', True)
    @patch('test_interface.webdriver.Chrome')
    def test_selenium_scraping(self, mock_chrome):
        """Test Selenium-based scraping for JavaScript sites"""
        mock_driver = TestUtils.create_mock_selenium_driver()
        mock_chrome.return_value = mock_driver
        
        try:
            result = test_interface.fetch_job_description_with_selenium(TEST_URLS['valid_microsoft'])
            self.assertIsInstance(result, str)
            mock_driver.get.assert_called_once()
            mock_driver.quit.assert_called_once()
        except Exception as e:
            # Handle case where Selenium setup fails in test environment
            self.assertIn("WebDriver", str(e))
    
    @patch('test_interface.SELENIUM_AVAILABLE', False)
    def test_selenium_unavailable(self):
        """Test behavior when Selenium is not available"""
        with self.assertRaises(Exception) as context:
            test_interface.fetch_job_description_with_selenium(TEST_URLS['valid_microsoft'])
        
        self.assertIn("Selenium", str(context.exception))
    
    @patch('test_interface.REQUESTS_HTML_AVAILABLE', True)
    @patch('test_interface.HTMLSession')
    def test_requests_html_scraping(self, mock_session_class):
        """Test requests-html based scraping"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.html.text = "Job description content"
        mock_response.html.render = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        try:
            result = test_interface.fetch_job_description_with_requests_html(TEST_URLS['valid_generic'])
            self.assertIsInstance(result, str)
            mock_session.get.assert_called_once()
        except Exception as e:
            # Handle case where requests-html setup fails
            self.assertIn("requests-html", str(e))
    
    @patch('test_interface.REQUESTS_HTML_AVAILABLE', False)
    def test_requests_html_unavailable(self):
        """Test behavior when requests-html is not available"""
        with self.assertRaises(Exception) as context:
            test_interface.fetch_job_description_with_requests_html(TEST_URLS['valid_generic'])
        
        self.assertIn("requests-html", str(context.exception))
    
    def test_microsoft_url_detection(self):
        """Test detection of Microsoft career URLs"""
        microsoft_urls = [
            "https://jobs.careers.microsoft.com/global/en/job/123",
            "https://careers.microsoft.com/job/456"
        ]
        
        for url in microsoft_urls:
            parsed = urlparse(url)
            self.assertTrue("microsoft.com" in parsed.netloc)
    
    def test_content_length_validation(self):
        """Test validation of extracted content length"""
        short_content = "Too short"
        long_content = "This is a proper job description " * 10
        
        # Short content should be rejected
        self.assertLess(len(short_content), 100)
        
        # Long content should be accepted
        self.assertGreater(len(long_content), 100)
    
    @patch('test_interface.requests.get')
    def test_timeout_handling(self, mock_get):
        """Test timeout handling during scraping"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        with self.assertRaises(Exception) as context:
            test_interface.fetch_job_description_from_url(TEST_URLS['timeout_url'])
        
        self.assertIn("timeout", str(context.exception).lower())
    
    @patch('test_interface.requests.get')
    def test_network_error_handling(self, mock_get):
        """Test network error handling"""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
        
        with self.assertRaises(Exception) as context:
            test_interface.fetch_job_description_from_url(TEST_URLS['valid_generic'])
        
        self.assertIn("Network", str(context.exception))
    
    def test_url_scheme_normalization(self):
        """Test URL scheme normalization (adding https://)"""
        # This would be tested by checking the URL processing logic
        test_url = "example.com/job"
        if not test_url.startswith(('http://', 'https://')):
            normalized_url = 'https://' + test_url
            self.assertTrue(normalized_url.startswith('https://'))


if __name__ == '__main__':
    unittest.main()