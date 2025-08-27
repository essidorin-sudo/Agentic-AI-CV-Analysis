#!/usr/bin/env python3
"""
CV Parser Agent - LLM-Based Resume/CV Parser

Specialized AI agent for parsing and structuring CVs/resumes using LLM.
Uses prompt engineering for accurate extraction and structuring of candidate information.
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
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
class ParsedCV:
    """Structured representation of a parsed CV/resume"""
    
    # Personal information
    full_name: str
    email: str
    phone: str
    location: str
    linkedin_url: str
    portfolio_url: str
    
    # Professional summary
    professional_summary: List[str]
    key_skills: List[str]
    
    # Work experience
    work_experience: List[Dict[str, str]]  # [{"company": "", "position": "", "duration": "", "responsibilities": []}]
    
    # Education
    education: List[Dict[str, str]]  # [{"institution": "", "degree": "", "field": "", "graduation": "", "gpa": ""}]
    
    # Additional sections
    certifications: List[str]
    projects: List[Dict[str, str]]  # [{"name": "", "description": "", "technologies": "", "url": ""}]
    publications: List[str]
    languages: List[str]
    achievements: List[str]
    volunteer_work: List[str]
    
    # Metadata
    confidence_score: float
    parsing_notes: List[str]
    raw_text: str = ""


class CVParserAgent:
    """
    LLM-based CV/Resume Parser Agent
    
    Uses advanced language models to parse and structure CVs/resumes
    through sophisticated prompt engineering with anti-hallucination protocols.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.version = "1.0.0"
        self.agent_id = f"cv_parser_{datetime.now().strftime('%Y%m%d')}"
        
        # LLM configuration
        self.llm_provider = self.config.get('llm_provider', 'anthropic')  # Default to Anthropic
        self.model_name = self.config.get('model_name', 'claude-3-5-sonnet-20241022')  # Use Sonnet for consistent JSON parsing
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
                import openai
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
        
        return """You are a specialized AI agent for parsing CVs/resumes. You must return ONLY a valid JSON object - no explanations, no markdown formatting, no extra text before or after the JSON.

DOCUMENT FORMAT HANDLING:
- If the input appears to be PDF binary data (starts with %PDF), extract readable text content first
- If the input appears to be Word document content, extract text from the formatted content  
- If the input is structured data or encoded content, decode it to find the actual CV text
- Focus on finding human-readable CV information regardless of source format

CRITICAL OUTPUT REQUIREMENTS:
- Return ONLY a valid JSON object
- No markdown code blocks, no explanations, no extra text
- Response must start with opening brace and end with closing brace
- All strings must be properly escaped for JSON

CRITICAL ANTI-HALLUCINATION PROTOCOL:
- EXTRACT ONLY: You can ONLY use text that appears EXACTLY in the source CV
- QUOTE-BASED EXTRACTION: Every value must be a direct quote or exact phrase from the source text
- ZERO INFERENCE: Never create, infer, guess, or generate any information
- ZERO CREATIVITY: Do not rephrase, summarize, or interpret - copy exactly as written
- IF NOT FOUND: Use empty string "" or empty array [] if information doesn't exist in source

QUOTE VERIFICATION REQUIREMENT:
For each field, you must be able to point to the exact location in the source text where that information appears.
If you cannot find the exact text in the source, you MUST use empty values.

Extract information into this JSON structure using ONLY direct quotes from source:

{{
    "full_name": "EXACT name as written in CV",
    "email": "EXACT email address from CV",
    "phone": "EXACT phone number from CV",
    "location": "EXACT location/address from CV",
    "linkedin_url": "EXACT LinkedIn URL from CV",
    "portfolio_url": "EXACT portfolio/website URL from CV",
    "professional_summary": ["EXACT summary statements from CV"],
    "key_skills": ["EXACT skills listed in CV"],
    "work_experience": [
        {{
            "company": "EXACT company name from CV",
            "position": "EXACT job title from CV", 
            "duration": "EXACT employment dates from CV",
            "responsibilities": ["EXACT responsibility statements from CV"]
        }}
    ],
    "education": [
        {{
            "institution": "EXACT school/university name from CV",
            "degree": "EXACT degree name from CV",
            "field": "EXACT field of study from CV",
            "graduation": "EXACT graduation date from CV",
            "gpa": "EXACT GPA if mentioned in CV"
        }}
    ],
    "certifications": ["EXACT certifications listed in CV"],
    "projects": [
        {{
            "name": "EXACT project name from CV",
            "description": "EXACT project description from CV",
            "technologies": "EXACT technologies mentioned for project",
            "url": "EXACT project URL if provided"
        }}
    ],
    "publications": ["EXACT publications listed in CV"],
    "languages": ["EXACT languages mentioned in CV"],
    "achievements": ["EXACT achievements/awards from CV"],
    "volunteer_work": ["EXACT volunteer experience from CV"],
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

CV/Resume Content:
{cv_text}

Return ONLY the JSON object with exact source quotes:"""

    def parse_cv_file(self, file_content: bytes, filename: str) -> ParsedCV:
        """
        Parse a CV file (PDF, DOC, DOCX) by sending it directly to Claude
        
        Args:
            file_content (bytes): Raw file content
            filename (str): Original filename
            
        Returns:
            ParsedCV: Structured CV data
        """
        
        print(f"🤖 CV Parser Agent v{self.version} processing file: {filename}")
        print(f"📄 File size: {len(file_content)} bytes")
        print(f"🧠 Using {self.llm_provider} model: {self.model_name}")
        
        try:
            # Send file directly to Claude with document processing
            if self.llm_provider == 'anthropic' and self.anthropic_api_key:
                parsed_data = self._call_anthropic_with_file(file_content, filename)
            else:
                # Fallback for non-Anthropic providers
                print("⚠️  File processing only supported with Anthropic Claude")
                return self._create_error_result(f"File processing requires Anthropic Claude API")
            
            # Convert to ParsedCV object
            result = ParsedCV(
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
                raw_text=f"[FILE: {filename}]"
            )
            
            print(f"✅ File parsing completed with confidence: {result.confidence_score:.2f}")
            return result
            
        except Exception as e:
            print(f"❌ Error during file parsing: {str(e)}")
            return self._create_error_result(f"File parsing failed: {str(e)}")

    def parse_cv(self, cv_text: str, metadata: Optional[Dict] = None) -> ParsedCV:
        """
        Main parsing method using LLM
        
        Args:
            cv_text (str): Raw CV/resume text
            metadata (dict, optional): Additional metadata about the CV
            
        Returns:
            ParsedCV: Structured CV data
        """
        
        print(f"🤖 CV Parser Agent v{self.version} starting LLM analysis...")
        print(f"📄 Text length: {len(cv_text)} characters")
        print(f"🧠 Using {self.llm_provider} model: {self.model_name}")
        
        try:
            # Add invisible address markup to CV text for highlighting system
            cv_text_with_addresses = self._add_address_markup(cv_text)
            
            # Format the prompt with the ORIGINAL CV text (not the marked-up version)
            full_prompt = self.parsing_prompt.format(cv_text=cv_text)
            
            # Call the LLM based on provider
            if self.llm_provider == 'anthropic' and self.anthropic_api_key:
                parsed_data = self._call_anthropic(full_prompt)
            elif self.llm_provider == 'openai' and self.openai_client:
                parsed_data = self._call_openai(full_prompt)
            else:
                # Fallback to mock parsing if no LLM available
                print("⚠️  No LLM client available, using fallback parsing")
                parsed_data = self._fallback_parsing(cv_text)
            
            # Convert to ParsedCV object
            result = ParsedCV(
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
                raw_text=cv_text_with_addresses
            )
            
            print(f"✅ CV parsing completed with confidence: {result.confidence_score:.2f}")
            return result
            
        except Exception as e:
            print(f"❌ Error during CV parsing: {str(e)}")
            print(f"❌ Exception type: {type(e)}")
            print(f"❌ Full exception details: {repr(e)}")
            # Return a fallback result with error information
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
                parsing_notes=[f"CV parsing failed: {str(e)}"],
                raw_text=cv_text
            )
    
    def _call_openai(self, prompt: str) -> Dict:
        """Call OpenAI API for parsing"""
        
        response = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a specialized CV parser. You MUST return only valid JSON with properly escaped strings. Do not include any markdown formatting or explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Clean up response and parse JSON
        response_text = self._clean_json_response(response_text)
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"📄 Full raw response: {response_text}")
            print(f"📄 Response length: {len(response_text)}")
            # Try to fix common JSON issues
            return self._attempt_json_repair(response_text)
    
    def _call_anthropic_with_file(self, file_content: bytes, filename: str) -> Dict:
        """Call Anthropic API with file content using Claude Sonnet for document processing"""
        
        import requests
        import time
        import base64
        
        # Encode file as base64
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Determine media type
        if filename.lower().endswith('.pdf'):
            media_type = "application/pdf"
        elif filename.lower().endswith('.docx'):
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif filename.lower().endswith('.doc'):
            media_type = "application/msword"
        else:
            media_type = "application/octet-stream"
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-5-sonnet-20241022",  # Use Sonnet for document processing
            "max_tokens": 8000,  # Increase token limit for full document processing
            "temperature": self.temperature,
            "messages": [
                {
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

{self.parsing_prompt.replace('{cv_text}', 'the COMPLETE text content extracted from ALL pages of the document')}"""
                        }
                    ]
                }
            ]
        }
        
        # Retry logic for rate limiting
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result["content"][0]["text"].strip()
                    print(f"🔍 Claude Sonnet file response: {response_text[:300]}...")
                    break
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("retry-after", base_delay * (2 ** attempt)))
                    print(f"⏱️  Rate limited. Waiting {retry_after} seconds before retry {attempt + 1}/{max_retries}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(retry_after)
                        continue
                    else:
                        raise Exception(f"Rate limited - please wait before trying again")
                else:
                    print(f"❌ Anthropic API error: {response.status_code} - {response.text}")
                    raise Exception(f"API error ({response.status_code})")
                    
            except requests.exceptions.Timeout:
                print(f"⏱️  Request timeout on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2 ** attempt))
                    continue
                else:
                    raise Exception("Request timed out")
            except requests.exceptions.RequestException as e:
                print(f"❌ Network error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2 ** attempt))
                    continue
                else:
                    raise Exception(f"Network error: {str(e)}")
        
        # Clean up response and parse JSON
        response_text = self._clean_json_response(response_text)
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"📄 Full raw response: {response_text}")
            print(f"📄 Response length: {len(response_text)}")
            return self._attempt_json_repair(response_text)

    def _create_error_result(self, error_message: str) -> ParsedCV:
        """Create a ParsedCV object for error cases"""
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

    def _call_anthropic(self, prompt: str) -> Dict:
        """Call Anthropic API for parsing using direct HTTP requests with retry logic"""
        
        import requests
        import time
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-5-sonnet-20241022",  # Use Sonnet for consistent JSON parsing
            "max_tokens": 4000,  # Increase token limit for better parsing
            "temperature": self.temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        # Retry logic for rate limiting
        max_retries = 3
        base_delay = 2  # Start with 2 second delay
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=45
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result["content"][0]["text"].strip()
                    break
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    retry_after = int(response.headers.get("retry-after", base_delay * (2 ** attempt)))
                    print(f"⏱️  Rate limited. Waiting {retry_after} seconds before retry {attempt + 1}/{max_retries}")
                    
                    if attempt < max_retries - 1:  # Don't sleep on the last attempt
                        time.sleep(retry_after)
                        continue
                    else:
                        print(f"❌ Max retries exceeded for rate limiting")
                        raise Exception(f"Rate limited - please wait a few minutes before trying again. Both JD and CV parsers share the same API quota.")
                else:
                    print(f"❌ Anthropic API error: {response.status_code} - {response.text}")
                    raise Exception(f"API error ({response.status_code}). Please try again.")
                    
            except requests.exceptions.Timeout:
                print(f"⏱️  Request timeout on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2 ** attempt))
                    continue
                else:
                    raise Exception("Request timed out. Please try again.")
            except requests.exceptions.RequestException as e:
                print(f"❌ Network error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2 ** attempt))
                    continue
                else:
                    raise Exception(f"Network error: {str(e)}")
        
        # Clean up response and parse JSON
        response_text = self._clean_json_response(response_text)
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"📄 Full raw response: {response_text}")
            print(f"📄 Response length: {len(response_text)}")
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
            
            # If JSON parsing completely fails, return a fallback
            print("🔧 Attempting JSON repair...")
            
            # Try to extract name from the raw text
            name_match = re.search(r'"full_name":\s*"([^"]*)"', response_text)
            name = name_match.group(1) if name_match else "Could not parse"
            
            return {
                "full_name": name,
                "email": "",
                "phone": "",
                "location": "",
                "linkedin_url": "",
                "portfolio_url": "",
                "professional_summary": ["JSON parsing failed - LLM returned malformed JSON"],
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
                "parsing_notes": ["JSON parsing failed - please check prompt engineering"]
            }
            
        except Exception as e:
            print(f"❌ JSON repair failed: {e}")
            return {
                "full_name": "Complete Parsing Failure",
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
                "parsing_notes": [f"Complete parsing failure: {str(e)}"]
            }
    
    def _fallback_parsing(self, cv_text: str) -> Dict:
        """Fallback parsing when no LLM is available"""
        
        # For demo purposes, extract some basic info using simple patterns
        import re
        
        lines = cv_text.split('\n')
        
        # Try to extract basic info
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', cv_text)
        phone_match = re.search(r'[\+]?[\s\(\-\)]?[\d\s\(\-\)]{10,}', cv_text)
        
        return {
            "full_name": lines[0].strip() if lines else "Name Not Found",
            "email": email_match.group() if email_match else "",
            "phone": phone_match.group().strip() if phone_match else "",
            "location": "",
            "linkedin_url": "",
            "portfolio_url": "",
            "professional_summary": ["Demo mode - basic pattern extraction only"],
            "key_skills": ["Pattern-based extraction limited"],
            "work_experience": [],
            "education": [],
            "certifications": [],
            "projects": [],
            "publications": [],
            "languages": [],
            "achievements": [],
            "volunteer_work": [],
            "confidence_score": 0.2,
            "parsing_notes": [
                "DEMO MODE: No LLM configured - using basic pattern matching",
                "Set OPENAI_API_KEY or ANTHROPIC_API_KEY for full AI-powered parsing",
                "This is a limited fallback demonstration only"
            ]
        }
    
    def to_dict(self, result: ParsedCV) -> Dict[str, Any]:
        """Convert ParsedCV to dictionary"""
        return asdict(result)
    
    def to_json(self, result: ParsedCV, indent: int = 2) -> str:
        """Convert ParsedCV to JSON string"""
        return json.dumps(asdict(result), indent=indent, ensure_ascii=False)
    
    def update_prompt(self, new_prompt: str):
        """Update the parsing prompt for testing different approaches"""
        self.parsing_prompt = new_prompt
        print(f"🔄 Prompt updated. New length: {len(new_prompt)} characters")
    
    def get_prompt(self) -> str:
        """Get the current parsing prompt"""
        return self.parsing_prompt
    
    def _add_address_markup(self, cv_text: str) -> str:
        """Add invisible address markup to CV text for highlighting system"""
        
        import re
        
        # Split text into lines for processing
        lines = cv_text.split('\n')
        marked_lines = []
        
        # Add address markers to key sections
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            
            # Skip empty lines
            if not stripped_line:
                marked_lines.append(line)
                continue
            
            # Detect section headers (all caps, standalone lines)
            if (len(stripped_line) > 2 and 
                (stripped_line.isupper() or 
                 any(keyword in stripped_line.upper() for keyword in 
                     ['EXPERIENCE', 'EDUCATION', 'SKILLS', 'SUMMARY', 'COMPETENCIES', 
                      'CERTIFICATIONS', 'PROJECTS', 'ACHIEVEMENTS', 'LANGUAGES']))):
                marked_lines.append(f'<!--cv_section_{i}-->{line}<!--/cv_section_{i}-->')
            
            # Detect company/position lines (contains years or company patterns)
            elif (re.search(r'\b20\d{2}\b', stripped_line) or  # Contains year
                  re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', stripped_line) or  # Contains month
                  re.search(r'(CEO|CTO|Manager|Director|Engineer|Analyst|Lead)', stripped_line, re.IGNORECASE)):
                marked_lines.append(f'<!--cv_position_{i}-->{line}<!--/cv_position_{i}-->')
            
            # Detect bullet points or responsibility items
            elif stripped_line.startswith(('•', '-', '*', '●')) or stripped_line.startswith(tuple('0123456789')):
                marked_lines.append(f'<!--cv_item_{i}-->{line}<!--/cv_item_{i}-->')
            
            # Regular content lines
            else:
                marked_lines.append(f'<!--cv_line_{i}-->{line}<!--/cv_line_{i}-->')
        
        marked_text = '\n'.join(marked_lines)
        print(f"🔖 Added address markup to CV text: {len(lines)} lines processed")
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
    print("🤖 CV Parser Agent v1.0.0 - LLM-Based CV Parsing")
    print("=" * 50)
    
    # Sample test
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