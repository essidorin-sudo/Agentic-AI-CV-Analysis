#!/usr/bin/env python3
"""
Direct API clients for JD Parser Agent.
Handles direct API calls to various LLM providers for job description parsing.
"""

import os
import json
import requests
from typing import Dict, Any, Optional


class JDAnthropicAPIClient:
    """Direct Anthropic API client for JD parsing."""
    
    def __init__(self, api_key: str, model_name: str, config: Dict[str, Any]):
        self.api_key = api_key
        self.model_name = model_name
        self.config = config
        
    def call_api(self, jd_text: str, parsing_prompt: str) -> str:
        """Make direct Anthropic API call."""
        
        api_url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model_name,
            "max_tokens": self.config.get('max_tokens', 4000),
            "temperature": self.config.get('temperature', 0.1),
            "messages": [
                {
                    "role": "user",
                    "content": f"{parsing_prompt}\n\n{jd_text}"
                }
            ]
        }
        
        response = requests.post(
            api_url, 
            headers=headers, 
            json=payload, 
            timeout=self.config.get('timeout', 30)
        )
        response.raise_for_status()
        
        result = response.json()
        return result['content'][0]['text']


class JDOpenAIAPIClient:
    """OpenAI API client for JD parsing."""
    
    def __init__(self, client, model_name: str, config: Dict[str, Any]):
        self.client = client
        self.model_name = model_name if "gpt" in model_name else "gpt-4"
        self.config = config
        
    def call_api(self, jd_text: str, parsing_prompt: str) -> str:
        """Make OpenAI API call."""
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": f"{parsing_prompt}\n\n{jd_text}"}
            ],
            temperature=self.config.get('temperature', 0.1),
            max_tokens=self.config.get('max_tokens', 4000)
        )
        
        return response.choices[0].message.content


class JDJSONResponseParser:
    """Handles JSON response parsing for job description data."""
    
    @staticmethod
    def parse_json_response(content: str) -> Dict[str, Any]:
        """Parse JSON response with comprehensive error handling."""
        
        try:
            # Clean response
            content = content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            content = content.strip()
            
            # Parse JSON
            parsed_data = json.loads(content)
            
            # Validate and ensure required fields
            return JDJSONResponseParser._ensure_required_fields(parsed_data)
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Raw content: {content[:200]}...")
            
            return JDJSONResponseParser._create_error_structure(str(e), content)
    
    @staticmethod
    def _ensure_required_fields(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all required fields are present."""
        
        required_fields = {
            'job_title': '',
            'company_name': '',
            'location': '',
            'job_summary': [],
            'required_skills': [],
            'preferred_skills': [],
            'required_experience': [],
            'required_education': [],
            'required_qualifications': [],
            'preferred_qualifications': [],
            'key_responsibilities': [],
            'work_environment': [],
            'team_structure': [],
            'salary_range': '',
            'compensation_details': [],
            'benefits_package': [],
            'job_type': '',
            'employment_duration': '',
            'work_schedule': '',
            'remote_work_policy': '',
            'travel_requirements': '',
            'company_description': [],
            'company_culture': [],
            'company_size': '',
            'industry': '',
            'application_process': [],
            'application_deadline': '',
            'contact_information': '',
            'confidence_score': 0.0,
            'parsing_notes': []
        }
        
        for field, default_value in required_fields.items():
            if field not in parsed_data:
                parsed_data[field] = default_value
                
        return parsed_data
    
    @staticmethod
    def _create_error_structure(error_msg: str, raw_content: str) -> Dict[str, Any]:
        """Create error response structure."""
        
        return {
            'job_title': 'Parse error - manual review required',
            'company_name': '',
            'location': '',
            'job_summary': ['JSON parsing failed'],
            'required_skills': [],
            'preferred_skills': [],
            'required_experience': [],
            'required_education': [],
            'required_qualifications': [],
            'preferred_qualifications': [],
            'key_responsibilities': [],
            'work_environment': [],
            'team_structure': [],
            'salary_range': '',
            'compensation_details': [],
            'benefits_package': [],
            'job_type': '',
            'employment_duration': '',
            'work_schedule': '',
            'remote_work_policy': '',
            'travel_requirements': '',
            'company_description': [],
            'company_culture': [],
            'company_size': '',
            'industry': '',
            'application_process': [],
            'application_deadline': '',
            'contact_information': '',
            'confidence_score': 0.0,
            'parsing_notes': [f'JSON parse error: {error_msg}'],
            'raw_content': raw_content[:500]
        }