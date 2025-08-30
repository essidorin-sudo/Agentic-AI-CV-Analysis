#!/usr/bin/env python3
"""
JD Parser prompt templates and management.
"""

from pathlib import Path
from typing import Optional


class JDParsingPrompts:
    """Manages parsing prompts for job description analysis."""
    
    @staticmethod
    def get_parsing_prompt() -> str:
        """Get the core parsing prompt template."""
        
        return """You are a specialized AI agent for parsing job descriptions. You must return ONLY a valid JSON object - no explanations, no markdown formatting, no extra text before or after the JSON.

CRITICAL OUTPUT REQUIREMENTS:
- Return ONLY a valid JSON object
- No markdown code blocks, no explanations, no extra text
- Response must start with opening brace and end with closing brace
- All strings must be properly escaped for JSON

CRITICAL ANTI-HALLUCINATION PROTOCOL:
- EXTRACT ONLY: You can ONLY use text that appears EXACTLY in the source job description
- QUOTE-BASED EXTRACTION: Every value must be a direct quote or exact phrase from the source text
- ZERO INFERENCE: Never create, infer, guess, or generate any information
- ZERO CREATIVITY: Do not rephrase, summarize, or interpret - copy exactly as written
- IF NOT FOUND: Use empty string "" or empty array [] if information doesn't exist in source

QUOTE VERIFICATION REQUIREMENT:
For each field, you must be able to point to the exact location in the source text where that information appears.
If you cannot find the exact text in the source, you MUST use empty values.

Extract information into this JSON structure using ONLY direct quotes from source:

{
    "job_title": "EXACT job title from JD",
    "company_name": "EXACT company name from JD",
    "location": "EXACT location from JD",
    "job_summary": ["EXACT summary statements from JD"],
    "required_skills": ["EXACT required skills listed in JD"],
    "preferred_skills": ["EXACT preferred skills listed in JD"],
    "required_experience": ["EXACT experience requirements from JD"],
    "required_education": ["EXACT education requirements from JD"],
    "required_qualifications": ["EXACT required qualifications from JD"],
    "preferred_qualifications": ["EXACT preferred qualifications from JD"],
    "key_responsibilities": ["EXACT responsibility statements from JD"],
    "work_environment": ["EXACT work environment details from JD"],
    "team_structure": ["EXACT team structure information from JD"],
    "salary_range": "EXACT salary range from JD",
    "compensation_details": ["EXACT compensation details from JD"],
    "benefits_package": ["EXACT benefits listed in JD"],
    "job_type": "EXACT job type from JD",
    "employment_duration": "EXACT duration from JD",
    "work_schedule": "EXACT schedule from JD",
    "remote_work_policy": "EXACT remote work policy from JD",
    "travel_requirements": "EXACT travel requirements from JD",
    "company_description": ["EXACT company description from JD"],
    "company_culture": ["EXACT culture information from JD"],
    "company_size": "EXACT company size from JD",
    "industry": "EXACT industry from JD",
    "application_process": ["EXACT application process from JD"],
    "application_deadline": "EXACT deadline from JD",
    "contact_information": "EXACT contact info from JD",
    "confidence_score": 0.95,
    "parsing_notes": ["Any specific notes about parsing challenges"]
}

JOB DESCRIPTION CONTENT TO PARSE:"""
    
    @staticmethod
    def load_custom_prompt(prompt_file: Path) -> Optional[str]:
        """Load custom prompt from file."""
        try:
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    saved_prompt = f.read().strip()
                    if saved_prompt:
                        print(f"📄 Loaded saved default prompt from {prompt_file}")
                        return saved_prompt
        except Exception as e:
            print(f"⚠️  Could not load saved prompt: {e}")
        return None
    
    @staticmethod
    def save_custom_prompt(prompt: str, prompt_file: Path) -> bool:
        """Save custom prompt to file."""
        try:
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            print(f"💾 Prompt saved to {prompt_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to save prompt: {e}")
            return False