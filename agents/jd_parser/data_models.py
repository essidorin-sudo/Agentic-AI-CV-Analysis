#!/usr/bin/env python3
"""
JD Parser data models and structures.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


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
    team_structure: List[str]
    
    # Compensation and benefits
    salary_range: str
    compensation_details: List[str]
    benefits_package: List[str]
    
    # Employment details
    job_type: str  # full-time, part-time, contract, etc.
    employment_duration: str
    work_schedule: str
    remote_work_policy: str
    travel_requirements: str
    
    # Company information
    company_description: List[str]
    company_culture: List[str]
    company_size: str
    industry: str
    
    # Application details
    application_process: List[str]
    application_deadline: str
    contact_information: str
    
    # Metadata
    confidence_score: float
    parsing_notes: List[str]
    raw_text: str = ""


@dataclass
class JDParsingConfig:
    """Configuration for JD parsing operations."""
    
    llm_provider: str = 'anthropic'
    model_name: str = 'claude-3-5-sonnet-20241022'
    temperature: float = 0.1
    max_tokens: int = 4000
    timeout: int = 30
    enable_fallback: bool = True
    confidence_threshold: float = 0.7