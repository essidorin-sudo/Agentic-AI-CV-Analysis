#!/usr/bin/env python3
"""
Prompt Management for CV Parsing

Handles loading, saving, and managing CV parsing prompts with version control
and anti-hallucination protocols. Supports both built-in and custom prompts.
"""

from pathlib import Path
from typing import Optional


class PromptManager:
    """
    Manages CV parsing prompts with persistence and version control
    
    Handles prompt loading from files, template management, and ensuring
    consistent anti-hallucination protocols across all prompt versions.
    """
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.prompt_file = self.base_path / 'default_prompt.txt'
        self.current_prompt = None
        
    def load_default_prompt(self) -> str:
        """Load saved default prompt or return built-in default"""
        
        # Try to load saved prompt first
        try:
            if self.prompt_file.exists():
                with open(self.prompt_file, 'r', encoding='utf-8') as f:
                    saved_prompt = f.read().strip()
                    if saved_prompt:
                        print(f"📄 Loaded saved default prompt from {self.prompt_file}")
                        self.current_prompt = saved_prompt
                        return saved_prompt
        except Exception as e:
            print(f"⚠️  Could not load saved prompt: {e}")
        
        # Fall back to built-in default
        print("📝 Using built-in default prompt")
        self.current_prompt = self._get_builtin_prompt()
        return self.current_prompt
    
    def save_as_default(self, prompt: str) -> bool:
        """Save a prompt as the new default"""
        
        try:
            # Ensure directory exists
            self.prompt_file.parent.mkdir(exist_ok=True)
            
            # Save the prompt
            with open(self.prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            # Update current prompt
            self.current_prompt = prompt
            
            print(f"✅ Saved new default prompt to {self.prompt_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save default prompt: {e}")
            return False
    
    def get_current_prompt(self) -> str:
        """Get the currently loaded prompt"""
        
        if self.current_prompt is None:
            return self.load_default_prompt()
        return self.current_prompt
    
    def update_prompt(self, new_prompt: str):
        """Update the current prompt (runtime only, not saved)"""
        
        self.current_prompt = new_prompt
        print(f"🔄 Prompt updated. New length: {len(new_prompt)} characters")
    
    def _get_builtin_prompt(self) -> str:
        """Get the built-in default CV parsing prompt with anti-hallucination protocols"""
        
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