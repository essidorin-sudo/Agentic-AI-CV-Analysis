#!/usr/bin/env python3
"""
Fallback Parser for CV Processing

Provides basic pattern-based parsing when LLM services are unavailable.
Used as a backup mechanism to ensure the system can still function
without cloud-based AI services.
"""

import re
from typing import Dict
from datetime import datetime


class FallbackParser:
    """
    Basic pattern-based CV parser for when LLM services are unavailable
    
    Uses regex patterns and heuristics to extract basic CV information
    without requiring cloud AI services. Provides degraded functionality
    as a safety net.
    """
    
    def __init__(self):
        # Common patterns for basic extraction
        self.email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        self.phone_pattern = r'[\+]?[\s\(\-\)]?[\d\s\(\-\)]{10,}'
        self.year_pattern = r'\b20\d{2}\b'
        self.url_patterns = [
            r'https?://[^\s]+',
            r'www\.[^\s]+',
            r'linkedin\.com[^\s]*'
        ]
        
    def parse_text_fallback(self, cv_text: str) -> Dict:
        """
        Parse CV text using basic pattern matching
        
        Args:
            cv_text: Raw CV text content
            
        Returns:
            Dict with basic extracted information
        """
        lines = cv_text.split('\n')
        
        # Basic information extraction
        full_name = self._extract_name(lines)
        email = self._extract_email(cv_text)
        phone = self._extract_phone(cv_text)
        urls = self._extract_urls(cv_text)
        
        # Separate LinkedIn from other URLs
        linkedin_url = ""
        portfolio_url = ""
        
        for url in urls:
            if 'linkedin' in url.lower():
                linkedin_url = url
            elif not portfolio_url:  # Take first non-LinkedIn URL
                portfolio_url = url
        
        return {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "location": "",
            "linkedin_url": linkedin_url,
            "portfolio_url": portfolio_url,
            "professional_summary": ["Demo mode - basic pattern extraction only"],
            "key_skills": self._extract_basic_skills(cv_text),
            "work_experience": self._extract_basic_experience(lines),
            "education": [],
            "certifications": [],
            "projects": [],
            "publications": [],
            "languages": [],
            "achievements": [],
            "volunteer_work": [],
            "confidence_score": 0.2,
            "parsing_notes": [
                "FALLBACK MODE: No LLM configured - using basic pattern matching",
                "Set ANTHROPIC_API_KEY for full AI-powered parsing",
                "This is a limited demonstration only"
            ]
        }
    
    def _extract_name(self, lines: list) -> str:
        """Extract name from first few lines"""
        for line in lines[:5]:  # Check first 5 lines
            stripped = line.strip()
            if (stripped and 
                len(stripped.split()) <= 4 and  # Reasonable name length
                not '@' in stripped and  # Not email
                not any(char.isdigit() for char in stripped) and  # No numbers
                len(stripped) > 2):  # Not too short
                return stripped
        
        return lines[0].strip() if lines else "Name Not Found"
    
    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        match = re.search(self.email_pattern, text)
        return match.group() if match else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        match = re.search(self.phone_pattern, text)
        return match.group().strip() if match else ""
    
    def _extract_urls(self, text: str) -> list:
        """Extract URLs from text"""
        urls = []
        for pattern in self.url_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            urls.extend(matches)
        return urls
    
    def _extract_basic_skills(self, text: str) -> list:
        """Extract basic skills using common technology keywords"""
        
        # Common technology and skill keywords
        skill_keywords = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go',
            'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django', 'Flask',
            'HTML', 'CSS', 'SQL', 'MongoDB', 'PostgreSQL', 'MySQL',
            'AWS', 'Azure', 'Docker', 'Kubernetes', 'Git', 'Linux',
            'Machine Learning', 'AI', 'Data Science', 'Analytics'
        ]
        
        found_skills = []
        text_upper = text.upper()
        
        for skill in skill_keywords:
            if skill.upper() in text_upper:
                found_skills.append(skill)
        
        return found_skills[:10] if found_skills else ["Pattern-based extraction limited"]
    
    def _extract_basic_experience(self, lines: list) -> list:
        """Extract basic work experience patterns"""
        
        experience = []
        current_entry = None
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Look for year patterns that might indicate job entries
            if re.search(self.year_pattern, stripped):
                if current_entry:
                    experience.append(current_entry)
                
                current_entry = {
                    "company": "Company extracted from pattern",
                    "position": "Position extracted from pattern", 
                    "duration": re.search(self.year_pattern, stripped).group(),
                    "responsibilities": [stripped]
                }
            elif current_entry and (stripped.startswith('-') or stripped.startswith('•')):
                # Add responsibility to current entry
                current_entry["responsibilities"].append(stripped)
        
        # Add last entry
        if current_entry:
            experience.append(current_entry)
        
        return experience[:3] if experience else []  # Limit to 3 entries
    
    def get_fallback_info(self) -> Dict[str, str]:
        """Get information about fallback parsing capabilities"""
        
        return {
            "mode": "fallback",
            "description": "Basic pattern-based parsing without LLM",
            "capabilities": [
                "Email extraction",
                "Phone number extraction", 
                "Basic name detection",
                "URL extraction",
                "Technology keyword detection",
                "Basic work experience patterns"
            ],
            "limitations": [
                "No semantic understanding",
                "Limited accuracy",
                "Cannot parse complex structures",
                "May miss contextual information"
            ]
        }