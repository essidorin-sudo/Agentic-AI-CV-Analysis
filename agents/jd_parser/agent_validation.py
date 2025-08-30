#!/usr/bin/env python3
"""
JD Parser Agent Validation Module

Provides validation methods for parsed job descriptions and agent information.
Extracted from main agent to comply with 200-line development guidelines.
"""

from typing import Dict, List, Any
import json
from datetime import datetime


class JDValidationMixin:
    """Validation methods for JD Parser Agent"""
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get comprehensive agent information"""
        return {
            'agent_id': self.agent_id,
            'version': self.version,
            'status': 'active',
            'llm_provider': self.llm_provider,
            'model_name': self.model_name,
            'capabilities': [
                'job_description_parsing',
                'skills_extraction',
                'requirements_analysis',
                'json_output_formatting',
                'fallback_parsing',
                'prompt_management'
            ],
            'config': {
                'temperature': self.temperature,
                'max_tokens': self.max_tokens,
                'anthropic_api_key_configured': bool(self.anthropic_api_key),
                'openai_api_key_configured': bool(getattr(self, 'openai_api_key', None)),
                'prompt_file': str(self.prompt_file)
            },
            'last_updated': datetime.now().isoformat()
        }
    
    def validate_parsed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parsed job description data"""
        validation_result = {
            'is_valid': True,
            'score': 1.0,
            'warnings': [],
            'missing_fields': [],
            'validation_timestamp': datetime.now().isoformat()
        }
        
        # Required fields check
        required_fields = ['job_title', 'company_name']
        critical_fields = ['required_skills', 'key_responsibilities']
        
        score = 1.0
        
        # Check required fields
        for field in required_fields:
            if field not in data or not data[field]:
                validation_result['missing_fields'].append(field)
                validation_result['warnings'].append(f"Missing critical field: {field}")
                score -= 0.3
        
        # Check critical content fields
        for field in critical_fields:
            if field not in data or not data[field] or len(data[field]) == 0:
                validation_result['missing_fields'].append(field)
                validation_result['warnings'].append(f"Missing important content: {field}")
                score -= 0.2
        
        # Check if no requirements found at all
        requirement_fields = [
            'required_skills', 'required_qualifications', 
            'required_experience', 'required_education'
        ]
        has_requirements = any(
            field in data and data[field] and len(data[field]) > 0 
            for field in requirement_fields
        )
        
        if not has_requirements:
            validation_result['warnings'].append("No requirements found in job description")
            score -= 0.1
        
        # Check confidence score
        if 'confidence_score' in data:
            conf_score = data['confidence_score']
            if not isinstance(conf_score, (int, float)) or conf_score < 0 or conf_score > 1:
                validation_result['warnings'].append("Invalid confidence score format")
                score -= 0.1
        
        # Validate list fields
        list_fields = [
            'job_summary', 'required_skills', 'preferred_skills',
            'required_experience', 'required_education', 'key_responsibilities',
            'benefits', 'parsing_notes'
        ]
        
        for field in list_fields:
            if field in data and not isinstance(data[field], list):
                validation_result['warnings'].append(f"Field {field} should be a list")
                score -= 0.05
        
        # Final validation
        validation_result['score'] = max(0.0, score)
        validation_result['is_valid'] = score > 0.5 and len(validation_result['missing_fields']) == 0
        
        return validation_result
    
    def _validate_data_structure(self, data: Dict[str, Any]) -> bool:
        """Internal method to validate basic data structure"""
        if not isinstance(data, dict):
            return False
        
        # Must have basic structure
        required_keys = ['job_title', 'company_name']
        return all(key in data for key in required_keys)
    
    def _calculate_completeness_score(self, data: Dict[str, Any]) -> float:
        """Calculate data completeness score"""
        total_fields = [
            'job_title', 'company_name', 'location', 'job_summary',
            'required_skills', 'preferred_skills', 'required_experience',
            'required_education', 'key_responsibilities', 'benefits'
        ]
        
        completed_fields = sum(1 for field in total_fields 
                             if field in data and data[field])
        
        return completed_fields / len(total_fields)