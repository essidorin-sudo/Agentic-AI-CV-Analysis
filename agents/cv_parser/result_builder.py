#!/usr/bin/env python3
"""
Result Builder for CV Parsing

Handles creation of standardized result objects and error responses
for CV parsing operations. Centralizes result formatting logic.
"""

from typing import Dict, Optional
from dataclasses import asdict
from datetime import datetime

from data_models import ParsedCV
from security.input_validator import InputValidator


class ResultBuilder:
    """
    Builds standardized result objects for CV parsing operations
    
    Centralizes the logic for creating success and error responses
    in consistent formats for API consumers.
    """
    
    def __init__(self):
        self.version = "2.0.0"
    
    def create_success_result(self, parsed_cv: ParsedCV) -> Dict:
        """Create successful parsing result"""
        return {
            "success": True,
            "result": asdict(parsed_cv),
            "agent_info": {
                "agent_id": f"cv_parser_{self._get_date_string()}",
                "version": self.version
            }
        }
    
    def create_validation_error_result(self, validation_result: Dict, validator: InputValidator) -> Dict:
        """Create error result for validation failures"""
        error_message = validator.get_security_summary(validation_result)
        return {
            "success": False,
            "error": error_message,
            "validation_details": validation_result,
            "agent_info": {
                "agent_id": f"cv_parser_{self._get_date_string()}",
                "version": self.version,
                "error_type": "validation_failed"
            }
        }
    
    def create_text_validation_error(self, validation_result: Dict) -> Dict:
        """Create error result for text validation failures"""
        issues = validation_result.get("issues", [])
        error_message = "; ".join(issues) if issues else "Text validation failed"
        
        return {
            "success": False,
            "error": error_message,
            "agent_info": {
                "agent_id": f"cv_parser_{self._get_date_string()}",
                "version": self.version,
                "error_type": "text_validation_failed"
            }
        }
    
    def create_error_result(self, error_message: str, filename: str = None) -> Dict:
        """Create standardized error result"""
        return {
            "success": False,
            "error": error_message,
            "agent_info": {
                "agent_id": f"cv_parser_{self._get_date_string()}",
                "version": self.version,
                "error_timestamp": self._get_timestamp(),
                "filename": filename
            }
        }
    
    def create_parsed_cv(self, parsed_data: Dict, raw_text: str) -> ParsedCV:
        """Create ParsedCV object from parsed data"""
        
        return ParsedCV(
            full_name=parsed_data.get('full_name', ''),
            email=parsed_data.get('email', ''),
            phone=parsed_data.get('phone', ''),
            location=parsed_data.get('location', ''),
            linkedin_url=parsed_data.get('linkedin_url', ''),
            portfolio_url=parsed_data.get('portfolio_url', ''),
            professional_summary=parsed_data.get('professional_summary', []),
            key_skills=parsed_data.get('key_skills', []),
            work_experience=parsed_data.get('work_experience', []),
            education=parsed_data.get('education', []),
            certifications=parsed_data.get('certifications', []),
            projects=parsed_data.get('projects', []),
            publications=parsed_data.get('publications', []),
            languages=parsed_data.get('languages', []),
            achievements=parsed_data.get('achievements', []),
            volunteer_work=parsed_data.get('volunteer_work', []),
            confidence_score=parsed_data.get('confidence_score', 0.5),
            parsing_notes=parsed_data.get('parsing_notes', []),
            raw_text=raw_text
        )
    
    def _get_date_string(self) -> str:
        """Get current date string for agent ID"""
        return datetime.now().strftime('%Y%m%d')
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()