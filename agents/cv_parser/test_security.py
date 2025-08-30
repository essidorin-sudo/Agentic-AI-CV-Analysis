#!/usr/bin/env python3
"""
Unit tests for Security modules following GL-Testing-Guidelines

Tests input validation and content scanning with comprehensive security scenarios.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, Mock

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from test.utils import setup_test, create_mock_file_content
from security.input_validator import InputValidator
from security.content_scanner import ContentScanner


class TestInputValidator(unittest.TestCase):
    """Test cases for InputValidator security validation"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.test_setup = setup_test()
        self.validator = InputValidator()
        
    def tearDown(self):
        """Clean up after each test"""
        self.test_setup.cleanup()
    
    def test_validator_initialization(self):
        """Test InputValidator initializes with proper settings"""
        # ACT
        validator = InputValidator()
        
        # ASSERT
        self.assertIsNotNone(validator.scanner)
        self.assertEqual(validator.max_file_size, 50 * 1024 * 1024)  # 50MB
        self.assertIn('.pdf', validator.allowed_extensions)
        self.assertIn('.docx', validator.allowed_extensions)
        self.assertIn('.txt', validator.allowed_extensions)
    
    def test_validate_file_upload_success(self):
        """Test successful file validation"""
        # ARRANGE
        file_content = create_mock_file_content("pdf")
        filename = "valid_cv.pdf"
        
        # ACT
        result = self.validator.validate_file_upload(file_content, filename)
        
        # ASSERT
        self.assertTrue(result["is_valid"])
        self.assertTrue(result["is_safe"])
        self.assertEqual(len(result["issues"]), 0)
    
    def test_validate_file_upload_invalid_extension(self):
        """Test file validation with invalid extension"""
        # ARRANGE
        file_content = b"test content"
        filename = "malicious.exe"
        
        # ACT
        result = self.validator.validate_file_upload(file_content, filename)
        
        # ASSERT
        self.assertFalse(result["is_valid"])
        self.assertIn("File type not allowed", str(result["issues"]))
    
    def test_validate_file_upload_too_large(self):
        """Test file validation with oversized file"""
        # ARRANGE
        large_content = b"x" * (60 * 1024 * 1024)  # 60MB
        filename = "large_cv.pdf"
        
        # ACT
        result = self.validator.validate_file_upload(large_content, filename)
        
        # ASSERT
        self.assertFalse(result["is_valid"])
        self.assertIn("File too large", str(result["issues"]))
    
    def test_validate_file_upload_empty_file(self):
        """Test file validation with empty file"""
        # ARRANGE
        empty_content = b""
        filename = "empty.pdf"
        
        # ACT
        result = self.validator.validate_file_upload(empty_content, filename)
        
        # ASSERT
        self.assertFalse(result["is_valid"])
        self.assertIn("File is empty", str(result["issues"]))
    
    def test_validate_text_input_success(self):
        """Test successful text input validation"""
        # ARRANGE
        valid_text = "John Smith\nSoftware Engineer\njohn@email.com"
        
        # ACT
        result = self.validator.validate_text_input(valid_text)
        
        # ASSERT
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["sanitized_text"], valid_text)
    
    def test_validate_text_input_with_html(self):
        """Test text validation removes HTML content"""
        # ARRANGE
        html_text = "John Smith<script>alert('xss')</script>\nSoftware Engineer"
        
        # ACT
        result = self.validator.validate_text_input(html_text)
        
        # ASSERT
        self.assertTrue(result["is_valid"])
        self.assertNotIn("<script>", result["sanitized_text"])
        self.assertIn("John Smith", result["sanitized_text"])
    
    def test_validate_text_input_too_long(self):
        """Test text validation with oversized text"""
        # ARRANGE
        long_text = "x" * 500001  # Over 500KB limit
        
        # ACT
        result = self.validator.validate_text_input(long_text)
        
        # ASSERT
        self.assertFalse(result["is_valid"])
        self.assertIn("Text too long", str(result["issues"]))
    
    def test_is_file_processing_safe_with_warnings(self):
        """Test file processing safety assessment with warnings"""
        # ARRANGE
        validation_result = {
            "is_valid": True,
            "is_safe": True,
            "security_warnings": ["Pattern detected", "Suspicious content"]
        }
        
        # ACT
        is_safe = self.validator.is_file_processing_safe(validation_result)
        
        # ASSERT
        self.assertTrue(is_safe)  # Should allow with minor warnings
    
    def test_is_file_processing_safe_too_many_warnings(self):
        """Test file processing safety with too many warnings"""
        # ARRANGE
        validation_result = {
            "is_valid": True,
            "is_safe": True,
            "security_warnings": ["Warning " + str(i) for i in range(12)]  # 12 warnings
        }
        
        # ACT
        is_safe = self.validator.is_file_processing_safe(validation_result)
        
        # ASSERT
        self.assertFalse(is_safe)  # Should block with too many warnings
    
    def test_get_security_summary(self):
        """Test security summary generation"""
        # ARRANGE
        validation_result = {
            "issues": ["File too large", "Invalid extension"],
            "security_warnings": ["Suspicious pattern detected"]
        }
        
        # ACT
        summary = self.validator.get_security_summary(validation_result)
        
        # ASSERT
        self.assertIsInstance(summary, str)
        self.assertIn("issues", summary)
        self.assertIn("Security concerns", summary)


class TestContentScanner(unittest.TestCase):
    """Test cases for ContentScanner security scanning"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.test_setup = setup_test()
        self.scanner = ContentScanner()
        
    def tearDown(self):
        """Clean up after each test"""
        self.test_setup.cleanup()
    
    def test_scanner_initialization(self):
        """Test ContentScanner initializes with security patterns"""
        # ACT
        scanner = ContentScanner()
        
        # ASSERT
        self.assertGreater(len(scanner.dangerous_patterns), 0)
        self.assertGreater(len(scanner.file_signatures), 0)
        self.assertIn(b'<script', scanner.dangerous_patterns)
    
    def test_scan_for_malicious_patterns_clean_content(self):
        """Test scanning clean content returns no threats"""
        # ARRANGE
        clean_content = b"John Smith\nSoftware Engineer\nPython, JavaScript"
        
        # ACT
        threats = self.scanner.scan_for_malicious_patterns(clean_content)
        
        # ASSERT
        self.assertEqual(len(threats), 0)
    
    def test_scan_for_malicious_patterns_with_threats(self):
        """Test scanning content with malicious patterns"""
        # ARRANGE
        malicious_content = b"John Smith<script>alert('hack')</script>Software Engineer"
        
        # ACT
        threats = self.scanner.scan_for_malicious_patterns(malicious_content)
        
        # ASSERT
        self.assertGreater(len(threats), 0)
        self.assertIn(b'<script', threats)
    
    def test_verify_file_signature_valid_pdf(self):
        """Test PDF file signature verification"""
        # ARRANGE
        pdf_content = create_mock_file_content("pdf")
        
        # ACT
        is_valid = self.scanner.verify_file_signature(pdf_content, ".pdf")
        
        # ASSERT
        self.assertTrue(is_valid)
    
    def test_verify_file_signature_invalid_pdf(self):
        """Test invalid PDF file signature"""
        # ARRANGE
        fake_pdf = b"This is not a PDF file"
        
        # ACT
        is_valid = self.scanner.verify_file_signature(fake_pdf, ".pdf")
        
        # ASSERT
        self.assertFalse(is_valid)
    
    def test_check_suspicious_filename_normal(self):
        """Test normal filename is not suspicious"""
        # ARRANGE
        normal_filename = "john_smith_cv.pdf"
        
        # ACT
        is_suspicious = self.scanner.check_suspicious_filename(normal_filename)
        
        # ASSERT
        self.assertFalse(is_suspicious)
    
    def test_check_suspicious_filename_suspicious(self):
        """Test suspicious filename detection"""
        # ARRANGE
        suspicious_filename = "malware.exe.pdf"
        
        # ACT
        is_suspicious = self.scanner.check_suspicious_filename(suspicious_filename)
        
        # ASSERT
        self.assertTrue(is_suspicious)
    
    def test_get_threat_level_none(self):
        """Test threat level assessment with no threats"""
        # ARRANGE
        no_patterns = []
        not_suspicious = False
        
        # ACT
        threat_level = self.scanner.get_threat_level(no_patterns, not_suspicious)
        
        # ASSERT
        self.assertEqual(threat_level, "none")
    
    def test_get_threat_level_low(self):
        """Test threat level assessment with low threats"""
        # ARRANGE
        few_patterns = [b"pattern1"]
        not_suspicious = False
        
        # ACT
        threat_level = self.scanner.get_threat_level(few_patterns, not_suspicious)
        
        # ASSERT
        self.assertEqual(threat_level, "low")
    
    def test_get_threat_level_high(self):
        """Test threat level assessment with high threats"""
        # ARRANGE
        many_patterns = [b"pattern" + str(i).encode() for i in range(5)]
        suspicious = True
        
        # ACT
        threat_level = self.scanner.get_threat_level(many_patterns, suspicious)
        
        # ASSERT
        self.assertEqual(threat_level, "high")


if __name__ == '__main__':
    unittest.main()