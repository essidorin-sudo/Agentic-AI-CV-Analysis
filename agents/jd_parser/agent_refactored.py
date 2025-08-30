#!/usr/bin/env python3
"""
JD Parser Agent - LLM-Based Job Description Parser

Specialized AI agent for parsing and structuring job descriptions using LLM.
Uses prompt engineering for accurate extraction and structuring of job content.
Refactored to comply with 200-line development guidelines.
"""

import json
import os
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import openai
from pathlib import Path

# Import mixins for extended functionality
from agent_validation import JDValidationMixin
from agent_llm_core import JDLLMCoreMixin

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"🔧 Loaded environment from {env_path}")
except ImportError:
    print("📝 python-dotenv not installed, using system environment variables")


@dataclass
class ParsedJobDescription:
    """Structured representation of a parsed job description"""
    job_title: str
    company_name: str
    location: str
    job_summary: List[str]
    required_skills: List[str]
    preferred_skills: List[str]
    required_experience: List[str]
    required_education: List[str]
    required_qualifications: List[str]
    preferred_qualifications: List[str]
    key_responsibilities: List[str]
    work_environment: List[str]
    company_info: List[str]
    team_info: List[str]
    benefits: List[str]
    confidence_score: float
    parsing_notes: List[str]
    raw_text: str = ""


class JDParserAgent(JDValidationMixin, JDLLMCoreMixin):
    """Main JD Parser Agent with LLM integration"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the JD Parser Agent"""
        self.version = "2.0.0"
        self.agent_id = f"jd_parser_{uuid.uuid4().hex[:8]}"
        
        # Configuration
        config = config or {}
        self.llm_provider = config.get('llm_provider', 'anthropic')
        self.model_name = config.get('model_name', 'claude-3-haiku-20240307')
        self.temperature = config.get('temperature', 0.1)
        self.max_tokens = config.get('max_tokens', 4000)
        
        # API configuration
        self.anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY', 'test-key-12345')
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        
        if self.anthropic_api_key and self.anthropic_api_key != 'test-key-12345':
            print("✅ Anthropic API key configured for direct calls")
        
        # OpenAI client setup
        self.openai_client = None
        if self.openai_api_key and self.llm_provider == 'openai':
            try:
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                print("✅ OpenAI client configured")
            except Exception as e:
                print(f"⚠️ OpenAI setup failed: {e}")
        
        # Load prompt
        self.prompt_file = Path(__file__).parent / 'default_prompt.txt'
        self.parsing_prompt = self._load_default_prompt()
        
        print(f"🤖 JD Parser Agent v{self.version} initialized")
    
    def parse_job_description(self, job_text: str) -> ParsedJobDescription:
        """Parse job description text using LLM"""
        print(f"🤖 JD Parser Agent v{self.version} starting LLM analysis...")
        print(f"📄 Text length: {len(job_text)} characters")
        print(f"🧠 Using {self.llm_provider} model: {self.model_name}")
        
        if len(job_text.strip()) < 20:
            return ParsedJobDescription(
                job_title="Parsing Error",
                company_name="Input Too Short",
                location="",
                job_summary=[],
                required_skills=[],
                preferred_skills=[],
                required_experience=[],
                required_education=[],
                required_qualifications=[],
                preferred_qualifications=[],
                key_responsibilities=[],
                work_environment=[],
                company_info=[],
                team_info=[],
                benefits=[],
                confidence_score=0.0,
                parsing_notes=[f"Input text too short: {len(job_text)} characters"],
                raw_text=job_text
            )
        
        try:
            # Add address markup for better parsing
            processed_text = self._add_address_markup(job_text)
            print(f"🔖 Added address markup to JD text: {len(processed_text.split('\n'))} lines processed")
            
            # Format prompt
            formatted_prompt = self.parsing_prompt.format(job_text=processed_text)
            
            # Call appropriate LLM
            if self.llm_provider == 'anthropic':
                parsed_data = self._call_anthropic(formatted_prompt)
            elif self.llm_provider == 'openai' and self.openai_client:
                parsed_data = self._call_openai(formatted_prompt)
            else:
                parsed_data = self._fallback_parsing(job_text)
            
            # Add raw text
            parsed_data['raw_text'] = job_text
            
            return ParsedJobDescription(**parsed_data)
            
        except Exception as e:
            print(f"❌ Error during parsing: {str(e)}")
            return ParsedJobDescription(
                job_title="Parsing Error",
                company_name="LLM Processing Failed",
                location="",
                job_summary=[],
                required_skills=[],
                preferred_skills=[],
                required_experience=[],
                required_education=[],
                required_qualifications=[],
                preferred_qualifications=[],
                key_responsibilities=[],
                work_environment=[],
                company_info=[],
                team_info=[],
                benefits=[],
                confidence_score=0.0,
                parsing_notes=[f"Error: {str(e)}"],
                raw_text=job_text
            )
    
    def _add_address_markup(self, text: str) -> str:
        """Add markup for better address detection"""
        # Simple implementation - could be enhanced
        return text
    
    def _load_default_prompt(self) -> str:
        """Load default parsing prompt"""
        if self.prompt_file.exists():
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                prompt = f.read()
                print(f"📄 Loaded saved default prompt from {self.prompt_file}")
                return prompt
        
        # Fallback prompt if file doesn't exist
        return """Parse the following job description and extract structured information as JSON:

{job_text}

Return ONLY a valid JSON object with these exact fields:
- job_title, company_name, location
- job_summary, required_skills, preferred_skills
- required_experience, required_education
- required_qualifications, preferred_qualifications  
- key_responsibilities, work_environment
- company_info, team_info, benefits
- confidence_score (0.0-1.0), parsing_notes

Ensure all fields are present and lists are used appropriately."""
    
    def get_prompt(self) -> str:
        """Get current parsing prompt"""
        return self.parsing_prompt
    
    def update_prompt(self, new_prompt: str) -> None:
        """Update parsing prompt"""
        self.parsing_prompt = new_prompt
        print(f"🔄 Prompt updated. New length: {len(new_prompt)} characters")
    
    def save_as_default_prompt(self, prompt: str) -> bool:
        """Save prompt as default"""
        try:
            with open(self.prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            print(f"✅ Saved new default prompt to {self.prompt_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to save prompt: {e}")
            return False
    
    def to_dict(self, result: ParsedJobDescription) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return asdict(result)
    
    def to_json(self, result: ParsedJobDescription, indent: int = 2) -> str:
        """Convert result to JSON string"""
        return json.dumps(asdict(result), indent=indent, ensure_ascii=False)


if __name__ == "__main__":
    print("🤖 JD Parser Agent v2.0.0 - LLM-Based Parsing")
    print("=" * 50)
    
    # Sample test
    sample_jd = """
    Senior Software Engineer - Full Stack
    TechCorp Solutions
    
    We are looking for a Senior Software Engineer to join our innovative team.
    
    Required:
    - 5+ years software development experience
    - Proficiency in Python, JavaScript, React
    - Bachelor's degree in Computer Science
    
    Responsibilities:
    - Build scalable web applications
    - Lead code reviews
    - Mentor junior developers
    """
    
    agent = JDParserAgent()
    result = agent.parse_job_description(sample_jd)
    print(f"\n🎯 Parsed: {result.job_title} at {result.company_name}")