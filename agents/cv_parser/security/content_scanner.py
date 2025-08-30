#!/usr/bin/env python3
"""
Content Security Scanner

Scans file content and text for malicious patterns, dangerous code,
and security threats. Provides pattern-based threat detection.
"""

import re
from typing import List


class ContentScanner:
    """
    Scans content for malicious patterns and security threats
    
    Provides pattern-based detection of dangerous code, script injection,
    and malicious content in files and text inputs.
    """
    
    def __init__(self):
        # Dangerous content patterns to detect
        self.dangerous_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'<?php',
            b'<%',
            b'exec(',
            b'eval(',
            b'system(',
            b'shell_exec',
            b'ActiveX',
            b'<object',
            b'<embed',
            b'onload=',
            b'onerror=',
            b'onclick='
        ]
        
        # File signatures for format verification
        self.file_signatures = {
            '.pdf': [b'%PDF'],
            '.docx': [b'PK\x03\x04'],  # ZIP-based format
            '.doc': [b'\xd0\xcf\x11\xe0'],  # OLE format
            '.txt': []  # No specific signature required
        }
        
        # Suspicious filename patterns
        self.suspicious_filename_patterns = [
            r'\.\./',  # Path traversal
            r'[<>:"|?*]',  # Invalid characters
            r'^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\.|$)',  # Windows reserved names
            r'\.exe$',  # Executable files
            r'\.scr$',  # Screen savers (often malicious)
            r'\.bat$',  # Batch files
            r'\.cmd$',  # Command files
        ]
    
    def scan_malicious_patterns(self, content: bytes) -> List[bytes]:
        """
        Scan content for malicious patterns
        
        Args:
            content: Binary content to scan
            
        Returns:
            List of found malicious patterns
        """
        found_patterns = []
        content_lower = content.lower()
        
        for pattern in self.dangerous_patterns:
            if pattern in content_lower:
                found_patterns.append(pattern)
        
        return found_patterns
    
    def verify_file_signature(self, content: bytes, file_ext: str) -> bool:
        """
        Verify file header signature matches extension
        
        Args:
            content: File content bytes
            file_ext: File extension (e.g., '.pdf')
            
        Returns:
            True if signature matches, False otherwise
        """
        if len(content) < 4:
            return file_ext == '.txt'  # Allow short text files
        
        if file_ext in self.file_signatures:
            signatures = self.file_signatures[file_ext]
            if not signatures:  # No signature check needed (like .txt)
                return True
            return any(content.startswith(sig) for sig in signatures)
        
        return False
    
    def check_suspicious_filename(self, filename: str) -> bool:
        """
        Check filename for suspicious patterns
        
        Args:
            filename: Filename to check
            
        Returns:
            True if suspicious patterns found, False otherwise
        """
        filename_lower = filename.lower()
        return any(
            re.search(pattern, filename_lower, re.IGNORECASE) 
            for pattern in self.suspicious_filename_patterns
        )
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe storage/processing
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        import os
        
        # Get base name to prevent path traversal
        safe_name = os.path.basename(filename)
        
        # Replace dangerous characters with underscores
        safe_name = re.sub(r'[<>:"|?*]', '_', safe_name)
        
        # Limit length
        if len(safe_name) > 100:
            name, ext = os.path.splitext(safe_name)
            safe_name = name[:95] + ext
        
        return safe_name
    
    def sanitize_text_content(self, text: str, max_length: int = 50000) -> str:
        """
        Sanitize text content for safe processing
        
        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text content
        """
        if not text:
            return ""
        
        # Remove potentially dangerous control characters
        dangerous_chars = ['\x00', '\x08', '\x0b', '\x0c']
        
        sanitized = text
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Ensure reasonable length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "... [truncated]"
        
        return sanitized.strip()
    
    def get_threat_level(self, malicious_patterns: List[bytes], suspicious_filename: bool) -> str:
        """
        Assess overall threat level based on scan results
        
        Args:
            malicious_patterns: List of found malicious patterns
            suspicious_filename: Whether filename is suspicious
            
        Returns:
            Threat level: 'low', 'medium', 'high'
        """
        if len(malicious_patterns) > 3 or suspicious_filename:
            return 'high'
        elif len(malicious_patterns) > 1:
            return 'medium'
        elif len(malicious_patterns) > 0:
            return 'low'
        else:
            return 'none'