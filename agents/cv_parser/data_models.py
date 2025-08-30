#!/usr/bin/env python3
"""
CV Parser data models and structures.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


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


@dataclass
class CVParsingConfig:
    """Configuration for CV parsing operations."""
    
    llm_provider: str = 'anthropic'
    model_name: str = 'claude-3-5-sonnet-20241022'
    temperature: float = 0.1
    max_tokens: int = 4000
    timeout: int = 30
    enable_fallback: bool = True
    confidence_threshold: float = 0.7