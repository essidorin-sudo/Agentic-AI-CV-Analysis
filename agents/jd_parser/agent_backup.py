#!/usr/bin/env python3
"""
JD Parser Agent - LLM-Based Job Description Parser

Specialized AI agent for parsing and structuring job descriptions using LLM.
Uses prompt engineering for accurate extraction and structuring of job content.
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import openai
from anthropic import Anthropic
from pathlib import Path

# Load environment variables from .env file
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
    
    # Core job information
    job_title: str
    company_name: str
    location: str
    job_summary: List[str]
    
    # Requirements (critical for CV matching)
    required_skills: List[str]
    preferred_skills: List[str]
    required_experience: List[str]
    required_education: List[str]
    required_qualifications: List[str]
    preferred_qualifications: List[str]
    
    # Job details
    key_responsibilities: List[str]
    work_environment: List[str]
    
    # Company information
    company_info: List[str]
    team_info: List[str]
    benefits: List[str]
    
    # Metadata
    confidence_score: float
    parsing_notes: List[str]
    raw_text: str = ""


class JDParserAgent:
    """
    LLM-based Job Description Parser Agent
    
    Uses advanced language models to parse and structure job descriptions
    through sophisticated prompt engineering.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.version = "2.0.0"
        self.agent_id = f"jd_parser_{datetime.now().strftime('%Y%m%d')}"
        
        # LLM configuration
        self.llm_provider = self.config.get('llm_provider', 'anthropic')  # Default to Anthropic
        self.model_name = self.config.get('model_name', 'claude-3-haiku-20240307')
        self.temperature = self.config.get('temperature', 0.1)
        
        # Initialize LLM clients
        self._init_llm_clients()
        
        # Prompt persistence
        self.prompt_file = Path(__file__).parent / 'default_prompt.txt'
        
        # Core parsing prompt template - load saved default or use built-in
        self.parsing_prompt = self._load_default_prompt()
    
    def _load_default_prompt(self) -> str:
        """Load saved default prompt or return built-in default"""
        try:
            if self.prompt_file.exists():
                with open(self.prompt_file, 'r', encoding='utf-8') as f:
                    saved_prompt = f.read().strip()
                    if saved_prompt:
                        print(f"📄 Loaded saved default prompt from {self.prompt_file}")
                        return saved_prompt
        except Exception as e:
            print(f"⚠️  Could not load saved prompt: {e}")
        
        # Return built-in default prompt
        print("📝 Using built-in default prompt")
        return self._get_parsing_prompt()
    
    def _init_llm_clients(self):
        """Initialize LLM clients based on configuration"""
        
        # OpenAI client
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                print("✅ OpenAI client initialized")
            except Exception as e:
                print(f"⚠️  OpenAI client failed: {e}")
                self.openai_client = None
        else:
            self.openai_client = None
            
        # Anthropic client - direct API approach
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_api_key:
            self.anthropic_api_key = anthropic_api_key
            self.anthropic_client = "direct_api"  # Use direct API calls
            print("✅ Anthropic API key configured for direct calls")
        else:
            self.anthropic_api_key = None
            self.anthropic_client = None
    
    def _get_parsing_prompt(self) -> str:
        """Get the core parsing prompt template"""
        
        return """You are a specialized AI agent for parsing job descriptions. You must analyze the job description text and return ONLY a valid JSON object with the extracted information.

CONTENT FILTERING - IGNORE COMPLETELY:
- Website navigation elements (menus, buttons, links like "Skip to main content", "Find jobs", "Apply", "Save")
- UI icons and symbols (represented as special characters or Unicode)
- Website headers, footers, and sidebar content
- Job search filters and dropdowns
- Social sharing buttons and website branding
- Any content that is clearly website functionality rather than job description

CRITICAL ANTI-HALLUCINATION PROTOCOL:
- Your response must be ONLY valid JSON. No explanations, no markdown, no extra text.
- EXTRACT ONLY: You can ONLY use text that appears EXACTLY in the source job description content (ignore website UI)
- QUOTE-BASED EXTRACTION: Every value must be a direct quote or exact phrase from the actual job posting content
- ZERO INFERENCE: Never create, infer, guess, or generate any information
- ZERO CREATIVITY: Do not rephrase, summarize, or interpret - copy exactly as written from job content only
- IF NOT FOUND: Use empty string "" or empty array [] if information doesn't exist in source

QUOTE VERIFICATION REQUIREMENT:
For each field, you must be able to point to the exact location in the source text where that information appears.
If you cannot find the exact text in the source, you MUST use empty values.

Extract information into this JSON structure using ONLY direct quotes from source:

{{
    "job_title": "EXACT title copied from source - NO CREATION",
    "company_name": "EXACT company name copied from source",
    "location": "EXACT location copied from source",
    "job_summary": ["EXACT phrases from source describing the role"],
    "required_skills": ["EXACT text marked as required/must-have"],
    "preferred_skills": ["EXACT text marked as preferred/nice-to-have"],
    "required_experience": ["EXACT experience requirements as written"],
    "required_education": ["EXACT education requirements as written"],
    "required_qualifications": ["EXACT required qualifications as written"],
    "preferred_qualifications": ["EXACT preferred qualifications as written"],
    "key_responsibilities": ["EXACT responsibility statements from source"],
    "work_environment": ["EXACT work environment details from source"],
    "company_info": ["EXACT company information from source"],
    "team_info": ["EXACT team/department info from source"],
    "benefits": ["EXACT benefits and compensation from source"],
    "confidence_score": 0.95,
    "parsing_notes": ["Note only if text is unclear or ambiguous"]
}}

MANDATORY EXTRACTION RULES:
1. DIRECT COPYING ONLY: Every extracted value must be copied exactly from the source text
2. NO PARAPHRASING: Do not change any words, even if they seem redundant
3. NO INTERPRETATION: Do not explain what something means, just copy it
4. NO ASSUMPTIONS: If something seems implied but not stated, ignore it
5. NO COMPLETION: If a sentence is cut off, copy only what's there
6. PRESERVE FORMATTING: Keep original punctuation, capitalization, and spacing
7. SOURCE VERIFICATION: Each value must have an exact match in the source text

HALLUCINATION PREVENTION:
- If you find yourself thinking "this probably means..." - STOP and use empty value
- If you want to "clean up" or "improve" text - STOP and copy exactly
- If information "seems obvious" but isn't stated - STOP and use empty value
- If you need to "interpret" requirements - STOP and copy exact wording only

Job Description:
{job_text}

Return ONLY the JSON object with exact source quotes:"""

    def parse_job_description(self, jd_text: str, metadata: Optional[Dict] = None) -> ParsedJobDescription:
        """
        Main parsing method using LLM
        
        Args:
            jd_text (str): Raw job description text
            metadata (dict, optional): Additional metadata about the JD
            
        Returns:
            ParsedJobDescription: Structured job description data
        """
        
        print(f"🤖 JD Parser Agent v{self.version} starting LLM analysis...")
        print(f"📄 Text length: {len(jd_text)} characters")
        print(f"🧠 Using {self.llm_provider} model: {self.model_name}")
        
        try:
            # Add invisible address markup to JD text for highlighting system
            jd_text_with_addresses = self._add_address_markup(jd_text)
            
            # Format the prompt with the ORIGINAL JD text (not the marked-up version)
            full_prompt = self.parsing_prompt.format(job_text=jd_text)
            
            # Call the LLM based on provider
            if self.llm_provider == 'anthropic' and self.anthropic_api_key:
                parsed_data = self._call_anthropic(full_prompt)
            elif self.llm_provider == 'openai' and self.openai_client:
                parsed_data = self._call_openai(full_prompt)
            else:
                # Fallback to mock parsing if no LLM available
                print("⚠️  No LLM client available, using fallback parsing")
                parsed_data = self._fallback_parsing(jd_text)
            
            # Convert to ParsedJobDescription object
            result = ParsedJobDescription(
                job_title=parsed_data.get('job_title', 'Not specified'),
                company_name=parsed_data.get('company_name', 'Not specified'),
                location=parsed_data.get('location', 'Not specified'),
                job_summary=parsed_data.get('job_summary', []),
                required_skills=parsed_data.get('required_skills', []),
                preferred_skills=parsed_data.get('preferred_skills', []),
                required_experience=parsed_data.get('required_experience', []),
                required_education=parsed_data.get('required_education', []),
                required_qualifications=parsed_data.get('required_qualifications', []),
                preferred_qualifications=parsed_data.get('preferred_qualifications', []),
                key_responsibilities=parsed_data.get('key_responsibilities', []),
                work_environment=parsed_data.get('work_environment', []),
                company_info=parsed_data.get('company_info', []),
                team_info=parsed_data.get('team_info', []),
                benefits=parsed_data.get('benefits', []),
                confidence_score=parsed_data.get('confidence_score', 0.5),
                parsing_notes=parsed_data.get('parsing_notes', []),
                raw_text=jd_text_with_addresses
            )
            
            print(f"✅ Parsing completed with confidence: {result.confidence_score:.2f}")
            return result
            
        except Exception as e:
            print(f"❌ Error during parsing: {str(e)}")
            # Return a fallback result with error information
            return ParsedJobDescription(
                job_title="Parsing Error",
                company_name="Unknown",
                location="Unknown",
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
                parsing_notes=[f"Parsing failed: {str(e)}"],
                raw_text=jd_text
            )
    
    def _call_openai(self, prompt: str) -> Dict:
        """Call OpenAI API for parsing"""
        
        response = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a specialized job description parser. You MUST return only valid JSON with properly escaped strings. Do not include any markdown formatting or explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Clean up response and parse JSON
        response_text = self._clean_json_response(response_text)
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"📄 Raw response: {response_text[:500]}...")
            # Try to fix common JSON issues
            return self._attempt_json_repair(response_text)
    
    def _call_anthropic(self, prompt: str) -> Dict:
        """Call Anthropic API for parsing using direct HTTP requests"""
        
        import requests
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 4000,
            "temperature": self.temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result["content"][0]["text"].strip()
            else:
                print(f"❌ Anthropic API error: {response.status_code} - {response.text}")
                raise Exception(f"API call failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Anthropic API call failed: {e}")
            raise e
        
        # Clean up response and parse JSON
        response_text = self._clean_json_response(response_text)
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"📄 Raw response: {response_text[:500]}...")
            # Try to fix common JSON issues
            return self._attempt_json_repair(response_text)
    
    def _clean_json_response(self, response_text: str) -> str:
        """Clean up JSON response from LLM"""
        
        # Remove markdown formatting
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        elif response_text.startswith('```'):
            response_text = response_text[3:]
        
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        # Remove any leading/trailing whitespace
        response_text = response_text.strip()
        
        # Ensure it starts and ends with braces
        if not response_text.startswith('{'):
            # Try to find the first brace
            start_idx = response_text.find('{')
            if start_idx != -1:
                response_text = response_text[start_idx:]
        
        if not response_text.endswith('}'):
            # Try to find the last brace
            end_idx = response_text.rfind('}')
            if end_idx != -1:
                response_text = response_text[:end_idx + 1]
        
        return response_text
    
    def _attempt_json_repair(self, response_text: str) -> Dict:
        """Attempt to repair malformed JSON"""
        
        try:
            # Try to fix common issues
            import re
            
            # Fix unescaped quotes in strings (basic attempt)
            # This is a simple fix - for production use a proper JSON repair library
            
            # If JSON parsing completely fails, return a fallback
            print("🔧 Attempting JSON repair...")
            
            # Try to extract job title from the raw text
            job_title_match = re.search(r'"job_title":\s*"([^"]*)"', response_text)
            job_title = job_title_match.group(1) if job_title_match else "Could not parse"
            
            return {
                "job_title": job_title,
                "company_name": "Parsing Error - Check JSON Format",
                "location": "Unknown",
                "job_summary": ["JSON parsing failed - LLM returned malformed JSON"],
                "required_skills": [],
                "preferred_skills": [],
                "required_experience": [],
                "required_education": [],
                "required_qualifications": [],
                "preferred_qualifications": [],
                "key_responsibilities": [],
                "work_environment": [],
                "company_info": [],
                "team_info": [],
                "benefits": [],
                "confidence_score": 0.0,
                "parsing_notes": ["JSON parsing failed - please check prompt engineering"]
            }
            
        except Exception as e:
            print(f"❌ JSON repair failed: {e}")
            return {
                "job_title": "Complete Parsing Failure",
                "company_name": "Unknown",
                "location": "Unknown",
                "job_summary": [],
                "required_skills": [],
                "preferred_skills": [],
                "required_experience": [],
                "required_education": [],
                "required_qualifications": [],
                "preferred_qualifications": [],
                "key_responsibilities": [],
                "work_environment": [],
                "company_info": [],
                "team_info": [],
                "benefits": [],
                "confidence_score": 0.0,
                "parsing_notes": [f"Complete parsing failure: {str(e)}"]
            }
    
    def _fallback_parsing(self, jd_text: str) -> Dict:
        """Fallback parsing when no LLM is available"""
        
        # For demo purposes, extract some basic info using simple patterns
        import re
        
        lines = jd_text.split('\n')
        first_few_lines = ' '.join(lines[:3])
        
        # Try to extract job title (usually first line)
        job_title = lines[0].strip() if lines else "Job Title Not Found"
        
        # Look for company patterns
        company_patterns = [r'at ([A-Z][a-zA-Z\s&]+)', r'([A-Z][a-zA-Z\s&]+) is looking', r'Join ([A-Z][a-zA-Z\s&]+)']
        company_name = "Company Not Found"
        for pattern in company_patterns:
            match = re.search(pattern, first_few_lines)
            if match:
                company_name = match.group(1).strip()
                break
        
        # Look for location patterns
        location_patterns = [r'([A-Z][a-zA-Z\s]+, [A-Z]{2})', r'(Remote)', r'([A-Z][a-zA-Z\s]+, [A-Z][a-zA-Z\s]+)']
        location = "Location Not Found"
        for pattern in location_patterns:
            match = re.search(pattern, jd_text)
            if match:
                location = match.group(1).strip()
                break
        
        # Extract some basic skills (demo)
        skill_patterns = [
            r'(Python|JavaScript|Java|React|Node\.js|AWS|Azure|Docker|Kubernetes)',
            r'(\d+\+?\s*years?\s*of?\s*experience)',
            r'(Bachelor\'s|Master\'s|PhD)'
        ]
        
        found_skills = []
        for pattern in skill_patterns:
            matches = re.findall(pattern, jd_text, re.IGNORECASE)
            found_skills.extend(matches)
        
        return {
            "job_title": job_title,
            "company_name": company_name,
            "location": location,
            "job_summary": ["Demo mode - basic pattern extraction only"],
            "required_skills": found_skills[:5] if found_skills else ["Pattern-based extraction limited"],
            "preferred_skills": [],
            "required_experience": [],
            "required_education": [],
            "required_qualifications": [],
            "preferred_qualifications": [],
            "key_responsibilities": ["Configure API keys for full LLM-powered analysis"],
            "work_environment": [],
            "company_info": [],
            "team_info": [],
            "benefits": [],
            "confidence_score": 0.2,
            "parsing_notes": [
                "DEMO MODE: No LLM configured - using basic pattern matching",
                "Set OPENAI_API_KEY or ANTHROPIC_API_KEY for full AI-powered parsing",
                "This is a limited fallback demonstration only"
            ]
        }
    
    def to_dict(self, result: ParsedJobDescription) -> Dict[str, Any]:
        """Convert ParsedJobDescription to dictionary"""
        return asdict(result)
    
    def to_json(self, result: ParsedJobDescription, indent: int = 2) -> str:
        """Convert ParsedJobDescription to JSON string"""
        return json.dumps(asdict(result), indent=indent, ensure_ascii=False)
    
    def update_prompt(self, new_prompt: str):
        """Update the parsing prompt for testing different approaches"""
        self.parsing_prompt = new_prompt
        print(f"🔄 Prompt updated. New length: {len(new_prompt)} characters")
    
    def get_prompt(self) -> str:
        """Get the current parsing prompt"""
        return self.parsing_prompt
    
    def _add_address_markup(self, jd_text: str) -> str:
        """Add invisible address markup to JD text for highlighting system"""
        
        import re
        
        # Split text into lines for processing
        lines = jd_text.split('\n')
        marked_lines = []
        
        # Add address markers to key sections
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            
            # Skip empty lines
            if not stripped_line:
                marked_lines.append(line)
                continue
            
            # Detect section headers (requirements, qualifications, responsibilities, etc.)
            if (len(stripped_line) > 2 and 
                (stripped_line.isupper() or 
                 any(keyword in stripped_line.upper() for keyword in 
                     ['REQUIREMENTS', 'QUALIFICATIONS', 'RESPONSIBILITIES', 'EXPERIENCE', 
                      'SKILLS', 'EDUCATION', 'ABOUT', 'COMPANY', 'BENEFITS', 'PERKS',
                      'JOB DESCRIPTION', 'DUTIES', 'POSITION', 'ROLE']))):
                marked_lines.append(f'<!--jd_section_{i}-->{line}<!--/jd_section_{i}-->')
            
            # Detect requirement items (bullet points, numbered lists, or skill mentions)
            elif (stripped_line.startswith(('•', '-', '*', '●', '◦')) or 
                  stripped_line.startswith(tuple('0123456789')) or
                  re.search(r'(required|preferred|must have|should have|experience with)', stripped_line, re.IGNORECASE)):
                marked_lines.append(f'<!--jd_requirement_{i}-->{line}<!--/jd_requirement_{i}-->')
            
            # Detect skill or technology mentions
            elif re.search(r'\b(Python|Java|JavaScript|React|AWS|Docker|SQL|Git|Linux|Windows|Mac|iOS|Android|C\+\+|C#|PHP|Ruby|Go|Rust|Kotlin|Swift|HTML|CSS|Node\.js|Angular|Vue|Spring|Django|Flask|MongoDB|PostgreSQL|MySQL|Redis|Kubernetes|Terraform|Jenkins|CI/CD|Agile|Scrum|REST|API|JSON|XML|NoSQL|DevOps|Cloud|Machine Learning|AI|Data Science|Analytics|Tableau|Excel|PowerBI|Salesforce|SAP|Oracle|Microsoft|Google|Amazon|Azure|GCP)\b', stripped_line, re.IGNORECASE):
                marked_lines.append(f'<!--jd_skill_{i}-->{line}<!--/jd_skill_{i}-->')
            
            # Detect experience or education requirements (years, degrees, certifications)
            elif (re.search(r'\b(\d+\+?\s*(years?|yrs?)|Bachelor|Master|PhD|degree|certification|certified)\b', stripped_line, re.IGNORECASE) or
                  re.search(r'\b(B\.S\.|M\.S\.|B\.A\.|M\.A\.|MBA|Ph\.D\.)\b', stripped_line)):
                marked_lines.append(f'<!--jd_qualification_{i}-->{line}<!--/jd_qualification_{i}-->')
            
            # Regular content lines
            else:
                marked_lines.append(f'<!--jd_line_{i}-->{line}<!--/jd_line_{i}-->')
        
        marked_text = '\n'.join(marked_lines)
        print(f"🔖 Added address markup to JD text: {len(lines)} lines processed")
        return marked_text
    
    def save_as_default_prompt(self, prompt: str) -> bool:
        """Save a prompt as the new default"""
        try:
            # Ensure directory exists
            self.prompt_file.parent.mkdir(exist_ok=True)
            
            # Save the prompt
            with open(self.prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            # Update current prompt
            self.parsing_prompt = prompt
            
            print(f"✅ Saved new default prompt to {self.prompt_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save default prompt: {e}")
            return False


# Test the agent when run directly
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
    
    Preferred:
    - AWS experience
    - Startup experience
    
    Responsibilities:
    - Build scalable web applications
    - Lead code reviews
    - Mentor junior developers
    
    We offer competitive salary ($120k-160k) and remote work options.
    """
    
    agent = JDParserAgent()
    result = agent.parse_job_description(sample_jd)
    
    print("\n📊 Parsing Results:")
    print(agent.to_json(result))