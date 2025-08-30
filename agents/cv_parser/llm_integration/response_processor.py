#!/usr/bin/env python3
"""
Response Processing for LLM APIs

Handles cleaning, parsing, and repairing responses from Language Model APIs.
Provides JSON processing with error recovery and content sanitization.
"""

import json
import re
from typing import Dict


class ResponseProcessor:
    """
    Processes and repairs LLM API responses for CV parsing
    
    Handles JSON cleaning, parsing, error recovery, and response
    sanitization to ensure reliable data extraction from LLM outputs.
    """
    
    def __init__(self):
        # Fallback CV structure for failed parsing
        self.fallback_structure = {
            "full_name": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin_url": "",
            "portfolio_url": "",
            "professional_summary": [],
            "key_skills": [],
            "work_experience": [],
            "education": [],
            "certifications": [],
            "projects": [],
            "publications": [],
            "languages": [],
            "achievements": [],
            "volunteer_work": [],
            "confidence_score": 0.0,
            "parsing_notes": []
        }
    
    def parse_json_response(self, response_text: str) -> Dict:
        """
        Parse and clean JSON response from LLM
        
        Args:
            response_text: Raw response text from LLM API
            
        Returns:
            Dict: Parsed CV data or fallback structure
        """
        # Clean up response formatting
        cleaned_text = self._clean_json_response(response_text)
        
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"📄 Response length: {len(cleaned_text)}")
            return self._attempt_json_repair(cleaned_text)
    
    def _clean_json_response(self, response_text: str) -> str:
        """Remove markdown formatting and clean JSON"""
        
        # Remove markdown code blocks
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        elif response_text.startswith('```'):
            response_text = response_text[3:]
        
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        # Remove leading/trailing whitespace
        response_text = response_text.strip()
        
        # Ensure proper JSON boundaries
        if not response_text.startswith('{'):
            start_idx = response_text.find('{')
            if start_idx != -1:
                response_text = response_text[start_idx:]
        
        if not response_text.endswith('}'):
            end_idx = response_text.rfind('}')
            if end_idx != -1:
                response_text = response_text[:end_idx + 1]
        
        return response_text
    
    def _attempt_json_repair(self, response_text: str) -> Dict:
        """Attempt to repair malformed JSON response"""
        
        try:
            print("🔧 Attempting JSON repair...")
            
            # Try to extract name from the raw text
            name_match = re.search(r'"full_name":\s*"([^"]*)"', response_text)
            name = name_match.group(1) if name_match else "Could not parse"
            
            # Create fallback with extracted name
            result = self.fallback_structure.copy()
            result["full_name"] = name
            result["parsing_notes"] = ["JSON parsing failed - LLM returned malformed JSON"]
            
            return result
            
        except Exception as e:
            print(f"❌ JSON repair failed: {e}")
            
            # Return complete fallback
            result = self.fallback_structure.copy()
            result["full_name"] = "Complete Parsing Failure"
            result["parsing_notes"] = [f"Complete parsing failure: {str(e)}"]
            
            return result
    
    def validate_response_structure(self, data: Dict) -> Dict:
        """
        Validate and normalize response structure
        
        Args:
            data: Parsed response data
            
        Returns:
            Dict: Validated and normalized data
        """
        # Ensure all required fields exist
        for key, default_value in self.fallback_structure.items():
            if key not in data:
                data[key] = default_value
        
        # Validate data types
        data = self._normalize_data_types(data)
        
        return data
    
    def _normalize_data_types(self, data: Dict) -> Dict:
        """Normalize data types to expected formats"""
        
        # Ensure string fields are strings
        string_fields = ["full_name", "email", "phone", "location", "linkedin_url", "portfolio_url"]
        for field in string_fields:
            if not isinstance(data.get(field, ""), str):
                data[field] = str(data.get(field, ""))
        
        # Ensure array fields are lists
        array_fields = ["professional_summary", "key_skills", "work_experience", "education", 
                       "certifications", "projects", "publications", "languages", 
                       "achievements", "volunteer_work", "parsing_notes"]
        for field in array_fields:
            if not isinstance(data.get(field, []), list):
                data[field] = []
        
        # Ensure confidence_score is float
        try:
            data["confidence_score"] = float(data.get("confidence_score", 0.0))
        except (ValueError, TypeError):
            data["confidence_score"] = 0.0
        
        return data