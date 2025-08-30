#!/usr/bin/env python3
"""
CV Parser Agent - Main Agent Interface

Main orchestration layer for CV parsing operations. Provides the exact same
public API as the original agent while using modular components internally.
Maintains complete backward compatibility with all existing integrations.
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

# Import modular components
from data_models import ParsedCV
from cv_parsing_service import CVParsingService
from llm_integration.prompt_manager import PromptManager

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"🔧 Loaded environment from {env_path}")
except ImportError:
    print("📝 python-dotenv not installed, using system environment variables")


class CVParserAgent:
    """
    LLM-based CV/Resume Parser Agent
    
    Main interface that maintains exact API compatibility with the original
    agent while using modular components internally. All existing integrations
    continue to work without any changes.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.version = "2.0.0"
        self.agent_id = f"cv_parser_{datetime.now().strftime('%Y%m%d')}"
        
        # Initialize service components
        self.parsing_service = CVParsingService()
        self.prompt_manager = PromptManager(Path(__file__).parent)
        
        # LLM configuration for backward compatibility
        self.llm_provider = self.config.get('llm_provider', 'anthropic')
        self.model_name = self.config.get('model_name', 'claude-3-5-sonnet-20241022')
        self.temperature = self.config.get('temperature', 0.1)
        
        print(f"🤖 CV Parser Agent v{self.version} initialized")
    
    def parse_cv_file(self, file_content: bytes, filename: str) -> ParsedCV:
        """
        Parse a CV file (PDF, DOC, DOCX) - EXACT API COMPATIBILITY
        
        Args:
            file_content (bytes): Raw file content
            filename (str): Original filename
            
        Returns:
            ParsedCV: Structured CV data
        """
        print(f"🤖 CV Parser Agent v{self.version} processing file: {filename}")
        
        # Use parsing service
        result = self.parsing_service.parse_file(file_content, filename)
        
        if result["success"]:
            # Convert back to ParsedCV object for exact compatibility
            data = result["result"]
            return ParsedCV(**data)
        else:
            # Return error as ParsedCV object (backward compatibility)
            return self._create_error_result(result.get("error", "Unknown error"))
    
    def parse_cv(self, cv_text: str, metadata: Optional[Dict] = None) -> ParsedCV:
        """
        Main parsing method using LLM - EXACT API COMPATIBILITY
        
        Args:
            cv_text (str): Raw CV/resume text
            metadata (dict, optional): Additional metadata about the CV
            
        Returns:
            ParsedCV: Structured CV data
        """
        print(f"🤖 CV Parser Agent v{self.version} starting LLM analysis...")
        
        # Use parsing service
        result = self.parsing_service.parse_text(cv_text, metadata)
        
        if result["success"]:
            # Convert back to ParsedCV object for exact compatibility
            data = result["result"]
            return ParsedCV(**data)
        else:
            # Return error as ParsedCV object (backward compatibility)
            return self._create_error_result(result.get("error", "Unknown error"))
    
    def to_dict(self, result: ParsedCV) -> Dict[str, Any]:
        """Convert ParsedCV to dictionary - EXACT API COMPATIBILITY"""
        return asdict(result)
    
    def to_json(self, result: ParsedCV, indent: int = 2) -> str:
        """Convert ParsedCV to JSON string - EXACT API COMPATIBILITY"""
        return json.dumps(asdict(result), indent=indent, ensure_ascii=False)
    
    def update_prompt(self, new_prompt: str):
        """Update the parsing prompt - EXACT API COMPATIBILITY"""
        self.prompt_manager.update_prompt(new_prompt)
        print(f"🔄 Prompt updated. New length: {len(new_prompt)} characters")
    
    def get_prompt(self) -> str:
        """Get the current parsing prompt - EXACT API COMPATIBILITY"""
        return self.prompt_manager.get_current_prompt()
    
    def save_as_default_prompt(self, prompt: str) -> bool:
        """Save a prompt as the new default - EXACT API COMPATIBILITY"""
        return self.prompt_manager.save_as_default(prompt)
    
    def _create_error_result(self, error_message: str) -> ParsedCV:
        """Create a ParsedCV object for error cases - maintains compatibility"""
        return ParsedCV(
            full_name="Parsing Error",
            email="",
            phone="",
            location="",
            linkedin_url="",
            portfolio_url="",
            professional_summary=[],
            key_skills=[],
            work_experience=[],
            education=[],
            certifications=[],
            projects=[],
            publications=[],
            languages=[],
            achievements=[],
            volunteer_work=[],
            confidence_score=0.0,
            parsing_notes=[error_message],
            raw_text=""
        )


# Backward compatibility - maintain exact same test when run directly
if __name__ == "__main__":
    print("🤖 CV Parser Agent v2.0.0 - LLM-Based CV Parsing")
    print("=" * 50)
    
    # Sample test - EXACT SAME as original
    sample_cv = """
    John Smith
    john.smith@email.com
    (555) 123-4567
    San Francisco, CA
    
    PROFESSIONAL SUMMARY
    Senior Software Engineer with 8+ years of experience in full-stack development.
    
    EXPERIENCE
    Senior Software Engineer - Google (2020-2024)
    - Led development of cloud infrastructure
    - Managed team of 5 engineers
    
    Software Engineer - Apple (2018-2020)
    - Developed iOS applications
    - Collaborated with design teams
    
    EDUCATION
    Master of Science in Computer Science - Stanford University (2018)
    Bachelor of Science in Computer Science - UC Berkeley (2016)
    
    SKILLS
    Python, JavaScript, React, Node.js, AWS, Docker
    """
    
    agent = CVParserAgent()
    result = agent.parse_cv(sample_cv)
    
    print("\n📊 CV Parsing Results:")
    print(agent.to_json(result))