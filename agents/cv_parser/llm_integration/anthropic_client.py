#!/usr/bin/env python3
"""
Anthropic API Client for CV Parsing

Handles direct HTTP API communication with Anthropic Claude for CV parsing operations.
Manages authentication, retries, file processing, and response handling.
"""

import os
import time
import base64
import requests
from typing import Dict, Optional
from .response_processor import ResponseProcessor


class AnthropicClient:
    """
    Direct HTTP client for Anthropic Claude API
    
    Handles both text and file processing with robust error handling,
    retry logic, and response cleaning for CV parsing operations.
    """
    
    def __init__(self, temperature: float = 0.1):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.temperature = temperature
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.max_retries = 3
        self.base_delay = 2
        self.response_processor = ResponseProcessor()
        
        if not self.api_key:
            print("⚠️  No Anthropic API key found")
        else:
            print("✅ Anthropic API client initialized")
    
    def is_available(self) -> bool:
        """Check if Anthropic client is available"""
        return bool(self.api_key)
    
    def call_text_api(self, prompt: str) -> Dict:
        """
        Call Anthropic API with text prompt for CV parsing
        
        Args:
            prompt: Formatted prompt with CV text
            
        Returns:
            Dict: Parsed CV data from LLM response
        """
        if not self.api_key:
            raise Exception("Anthropic API key not available")
        
        headers = self._get_headers()
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4000,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        return self._make_request_with_retry(headers, data)
    
    def call_file_api(self, file_content: bytes, filename: str, prompt_template: str) -> Dict:
        """
        Call Anthropic API with file content for CV parsing
        
        Args:
            file_content: Raw file bytes
            filename: Original filename for media type detection
            prompt_template: Template with {cv_text} placeholder
            
        Returns:
            Dict: Parsed CV data from LLM response
        """
        if not self.api_key:
            raise Exception("Anthropic API key not available")
        
        # Prepare file data
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        media_type = self._get_media_type(filename)
        
        headers = self._get_headers()
        data = self._build_file_request_data(file_base64, media_type, prompt_template)
        
        return self._make_request_with_retry(headers, data)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get standard headers for API requests"""
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
    
    def _get_media_type(self, filename: str) -> str:
        """Determine media type from filename"""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        media_types = {
            'pdf': "application/pdf",
            'docx': "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            'doc': "application/msword"
        }
        
        return media_types.get(ext, "application/octet-stream")
    
    def _build_file_request_data(self, file_base64: str, media_type: str, prompt_template: str) -> Dict:
        """Build request data for file processing"""
        
        # Format prompt for file processing
        file_prompt = prompt_template.replace(
            '{cv_text}', 
            'the COMPLETE text content extracted from ALL pages of the document'
        )
        
        return {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 8000,  # Higher limit for file processing
            "temperature": self.temperature,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": file_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": f"""Extract ALL text content from this COMPLETE CV/resume document (including ALL pages) and parse it into the required JSON format.

CRITICAL: Make sure you process the ENTIRE document - do not stop at page 1. Read through all pages and extract ALL work experience, education, skills, and other sections.

{file_prompt}"""
                    }
                ]
            }]
        }
    
    def _make_request_with_retry(self, headers: Dict, data: Dict) -> Dict:
        """Make API request with retry logic"""
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(self.base_url, headers=headers, json=data, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result["content"][0]["text"].strip()
                    print(f"🔍 Claude response: {response_text[:200]}...")
                    return self.response_processor.parse_json_response(response_text)
                
                elif response.status_code == 429:
                    if not self._handle_rate_limit(attempt):
                        raise Exception("Rate limited - please wait before trying again")
                
                else:
                    print(f"❌ Anthropic API error: {response.status_code} - {response.text}")
                    raise Exception(f"API error ({response.status_code})")
                    
            except requests.exceptions.Timeout:
                if not self._handle_timeout(attempt):
                    raise Exception("Request timed out")
                    
            except requests.exceptions.RequestException as e:
                if not self._handle_network_error(attempt, e):
                    raise Exception(f"Network error: {str(e)}")
        
        raise Exception("All retry attempts failed")
    
    def _handle_rate_limit(self, attempt: int) -> bool:
        """Handle rate limiting with backoff"""
        retry_after = self.base_delay * (2 ** attempt)
        print(f"⏱️  Rate limited. Waiting {retry_after} seconds before retry {attempt + 1}/{self.max_retries}")
        
        if attempt < self.max_retries - 1:
            time.sleep(retry_after)
            return True
        return False
    
    def _handle_timeout(self, attempt: int) -> bool:
        """Handle timeout with backoff"""
        print(f"⏱️  Request timeout on attempt {attempt + 1}/{self.max_retries}")
        if attempt < self.max_retries - 1:
            time.sleep(self.base_delay * (2 ** attempt))
            return True
        return False
    
    def _handle_network_error(self, attempt: int, error: Exception) -> bool:
        """Handle network errors with backoff"""
        print(f"❌ Network error on attempt {attempt + 1}/{self.max_retries}: {error}")
        if attempt < self.max_retries - 1:
            time.sleep(self.base_delay * (2 ** attempt))
            return True
        return False