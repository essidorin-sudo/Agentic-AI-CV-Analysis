#!/usr/bin/env python3
"""
Input Validation and Security for CV Parser

Comprehensive security validation for file uploads, text content, and user inputs.
Implements multi-layered protection against malicious content and attacks.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from .content_scanner import ContentScanner


class InputValidator:
    """
    Comprehensive input validation and security checking for CV parser
    
    Validates file uploads, text content, and parameters to ensure safe
    processing and protection against malicious content and attacks.
    """
    
    def __init__(self):
        # Security configuration
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.max_text_length = 50000           # 50KB
        self.allowed_extensions = {'.pdf', '.docx', '.doc', '.txt'}
        
        # Initialize content scanner
        self.scanner = ContentScanner()
    
    def validate_file_upload(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Comprehensive file upload validation with security checks
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            
        Returns:
            Dict with validation results and security assessment
        """
        validation_result = {
            "is_valid": True,
            "is_safe": True,
            "issues": [],
            "security_warnings": [],
            "file_info": {
                "size": len(file_content),
                "extension": Path(filename).suffix.lower(),
                "name": self.scanner.sanitize_filename(filename)
            }
        }
        
        # Basic file validation
        self._validate_basic_properties(file_content, filename, validation_result)
        
        # Security validation
        self._validate_security(file_content, filename, validation_result)
        
        # Final security assessment
        validation_result["is_safe"] = len(validation_result["security_warnings"]) == 0
        
        return validation_result
    
    def validate_text_input(self, text: str, max_length: Optional[int] = None) -> Dict[str, Any]:
        """
        Validate and sanitize text input
        
        Args:
            text: Input text to validate
            max_length: Optional custom length limit
            
        Returns:
            Dict with validation results and sanitized text
        """
        if max_length is None:
            max_length = self.max_text_length
        
        validation_result = {
            "is_valid": True,
            "sanitized_text": "",
            "issues": [],
            "original_length": len(text) if text else 0
        }
        
        if not text:
            validation_result["sanitized_text"] = ""
            return validation_result
        
        # Length validation
        if len(text) > max_length:
            validation_result["issues"].append(f"Text exceeds maximum length of {max_length} characters")
            text = text[:max_length] + "... [truncated for security]"
        
        # Sanitize text content
        validation_result["sanitized_text"] = self.scanner.sanitize_text_content(text, max_length)
        
        return validation_result
    
    def _validate_basic_properties(self, file_content: bytes, filename: str, result: Dict):
        """Validate basic file properties"""
        
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.allowed_extensions:
            result["is_valid"] = False
            result["issues"].append(f"Unsupported file type: {file_ext}")
        
        # Check file size
        if len(file_content) > self.max_file_size:
            result["is_valid"] = False
            result["issues"].append(f"File size ({len(file_content)} bytes) exceeds limit ({self.max_file_size} bytes)")
        
        # Check for empty files
        if len(file_content) == 0:
            result["is_valid"] = False
            result["issues"].append("File is empty")
    
    def _validate_security(self, file_content: bytes, filename: str, result: Dict):
        """Perform security validation on file content"""
        
        file_ext = Path(filename).suffix.lower()
        
        # Verify file signature matches extension
        if not self.scanner.verify_file_signature(file_content, file_ext):
            result["security_warnings"].append("File signature doesn't match extension - possible file type spoofing")
        
        # Scan for malicious patterns
        malicious_patterns = self.scanner.scan_malicious_patterns(file_content)
        if malicious_patterns:
            result["security_warnings"].extend([
                f"Potentially malicious content detected: {pattern.decode('utf-8', errors='ignore')}"
                for pattern in malicious_patterns
            ])
        
        # Check filename for suspicious patterns
        if self.scanner.check_suspicious_filename(filename):
            result["security_warnings"].append("Suspicious filename detected")
        
        # Assess overall threat level
        suspicious_filename = self.scanner.check_suspicious_filename(filename)
        threat_level = self.scanner.get_threat_level(malicious_patterns, suspicious_filename)
        
        if threat_level != 'none':
            result["security_warnings"].append(f"Threat level: {threat_level}")
    
    def get_security_summary(self, validation_result: Dict) -> str:
        """Generate a human-readable security summary"""
        
        if validation_result.get("is_safe", True) and validation_result.get("is_valid", True):
            return "✅ File passed all security checks"
        
        summary_parts = []
        
        if not validation_result.get("is_valid", True):
            summary_parts.append(f"❌ Validation failed: {len(validation_result.get('issues', []))} issues")
        
        if not validation_result.get("is_safe", True):
            summary_parts.append(f"⚠️ Security concerns: {len(validation_result.get('security_warnings', []))} warnings")
        
        return " | ".join(summary_parts) if summary_parts else "✅ No issues detected"
    
    def is_file_processing_safe(self, validation_result: Dict) -> bool:
        """
        Determine if file is safe to process based on validation results
        
        Args:
            validation_result: Result from validate_file_upload
            
        Returns:
            True if safe to process, False otherwise
        """
        # Allow processing with warnings for legitimate CV documents
        # Only block if there are critical security threats
        warning_count = len(validation_result.get("security_warnings", []))
        has_critical_threats = any("critical" in str(w).lower() or "malicious" in str(w).lower() 
                                 for w in validation_result.get("security_warnings", []))
        
        return (validation_result.get("is_valid", False) and 
                validation_result.get("is_safe", True) and
                warning_count < 10 and  # Very permissive for CV documents
                not has_critical_threats)  # Only block actual critical threats