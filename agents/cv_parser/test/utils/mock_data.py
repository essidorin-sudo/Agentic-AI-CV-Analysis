#!/usr/bin/env python3
"""
Mock data factories for CV Parser Agent testing

Provides factory functions for creating consistent test data
following GL-Testing-Guidelines standards.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


def create_mock_cv_data(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Factory function for creating mock CV data
    
    Args:
        overrides: Dict of fields to override default values
        
    Returns:
        Dict with realistic CV data structure
    """
    default_cv = {
        "full_name": "John Smith",
        "email": "john.smith@email.com",
        "phone": "(555) 123-4567",
        "location": "San Francisco, CA",
        "linkedin_url": "https://linkedin.com/in/johnsmith",
        "portfolio_url": "https://johnsmith.dev",
        "professional_summary": [
            "Senior Software Engineer with 5+ years of experience",
            "Expertise in full-stack web development",
            "Strong background in Python and JavaScript"
        ],
        "key_skills": [
            "Python", "JavaScript", "TypeScript", "React", "Node.js",
            "PostgreSQL", "MongoDB", "Docker", "AWS", "Git"
        ],
        "work_experience": [
            {
                "company": "TechCorp Inc",
                "position": "Senior Software Engineer",
                "duration": "2020-2024",
                "responsibilities": [
                    "Led development of web applications using React and Node.js",
                    "Managed team of 3 junior developers",
                    "Implemented CI/CD pipelines using Docker and AWS"
                ]
            },
            {
                "company": "StartupXYZ",
                "position": "Full Stack Developer", 
                "duration": "2018-2020",
                "responsibilities": [
                    "Built REST APIs using Python and Flask",
                    "Developed responsive web interfaces",
                    "Optimized database queries for improved performance"
                ]
            }
        ],
        "education": [
            {
                "institution": "University of California, Berkeley",
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "graduation": "2018",
                "gpa": "3.8"
            }
        ],
        "certifications": [
            "AWS Certified Developer Associate",
            "Docker Certified Associate"
        ],
        "projects": [
            {
                "name": "E-commerce Platform",
                "description": "Built full-stack e-commerce platform with React and Node.js",
                "technologies": "React, Node.js, PostgreSQL, Stripe API",
                "url": "https://github.com/johnsmith/ecommerce"
            }
        ],
        "publications": [],
        "languages": ["English (Native)", "Spanish (Intermediate)"],
        "achievements": [
            "Employee of the Year 2022 at TechCorp",
            "Led team that reduced deployment time by 60%"
        ],
        "volunteer_work": [
            "Code mentor for local coding bootcamp"
        ],
        "confidence_score": 0.95,
        "parsing_notes": []
    }
    
    if overrides:
        default_cv.update(overrides)
        
    return default_cv


def create_mock_job_description(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Factory function for creating mock job description data
    
    Args:
        overrides: Dict of fields to override default values
        
    Returns:
        Dict with realistic JD data structure
    """
    default_jd = {
        "title": "Senior Frontend Developer",
        "company": "Amazing Tech Company",
        "location": "San Francisco, CA",
        "type": "Full-time",
        "experience_level": "Senior",
        "required_skills": [
            "React", "JavaScript", "TypeScript", "HTML", "CSS",
            "Node.js", "REST APIs", "Git", "Agile"
        ],
        "preferred_skills": [
            "GraphQL", "Redux", "Docker", "AWS", "Jest"
        ],
        "description": "Join our dynamic team as a Senior Frontend Developer...",
        "responsibilities": [
            "Develop and maintain React applications",
            "Collaborate with design and backend teams",
            "Write clean, testable code",
            "Participate in code reviews"
        ],
        "requirements": [
            "5+ years of frontend development experience",
            "Strong proficiency in React and JavaScript",
            "Experience with modern development tools",
            "Bachelor's degree in Computer Science or equivalent"
        ],
        "benefits": [
            "Competitive salary",
            "Health insurance",
            "Flexible working hours",
            "Remote work options"
        ]
    }
    
    if overrides:
        default_jd.update(overrides)
        
    return default_jd


def create_mock_analysis_result(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Factory function for creating mock gap analysis results
    
    Args:
        overrides: Dict of fields to override default values
        
    Returns:
        Dict with realistic analysis result structure
    """
    default_analysis = {
        "match_score": 85.5,
        "overall_rating": "Strong Match",
        "skill_gaps": [
            "GraphQL", "Redux"
        ],
        "skill_matches": [
            "React", "JavaScript", "TypeScript", "Node.js"
        ],
        "recommendations": [
            "Consider learning GraphQL for API development",
            "Redux knowledge would be beneficial for state management"
        ],
        "strengths": [
            "Strong React and JavaScript experience",
            "Full-stack development background",
            "Leadership experience"
        ],
        "experience_match": {
            "required_years": 5,
            "candidate_years": 6,
            "rating": "Exceeds Requirements"
        },
        "education_match": {
            "required": "Bachelor's degree in Computer Science",
            "candidate": "BS Computer Science, UC Berkeley",
            "rating": "Perfect Match"
        },
        "confidence_score": 0.92,
        "analysis_timestamp": datetime.now().isoformat()
    }
    
    if overrides:
        default_analysis.update(overrides)
        
    return default_analysis


def create_mock_parsed_cv_object(overrides: Optional[Dict[str, Any]] = None):
    """
    Factory function for creating mock ParsedCV objects
    
    Args:
        overrides: Dict of fields to override default values
        
    Returns:
        Mock ParsedCV object with realistic data
    """
    from unittest.mock import Mock
    
    cv_data = create_mock_cv_data(overrides)
    
    mock_cv = Mock()
    for key, value in cv_data.items():
        setattr(mock_cv, key, value)
    
    return mock_cv


def create_mock_file_content(file_type: str = "pdf") -> bytes:
    """
    Create mock file content for testing file uploads
    
    Args:
        file_type: Type of file (pdf, docx, txt)
        
    Returns:
        Mock file content as bytes
    """
    if file_type == "pdf":
        return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nMock PDF Content"
    elif file_type == "docx":
        return b"PK\x03\x04Mock DOCX Content"
    elif file_type == "txt":
        return "Mock CV Text Content\nJohn Smith\nSoftware Engineer".encode('utf-8')
    else:
        return b"Mock file content"


# Sample test data collections for batch testing
SAMPLE_CVS = [
    create_mock_cv_data({"full_name": "Alice Johnson", "key_skills": ["Python", "Machine Learning"]}),
    create_mock_cv_data({"full_name": "Bob Wilson", "key_skills": ["JavaScript", "React", "Node.js"]}),
    create_mock_cv_data({"full_name": "Carol Davis", "key_skills": ["Java", "Spring", "Microservices"]})
]

SAMPLE_JDS = [
    create_mock_job_description({"title": "Python Developer", "required_skills": ["Python", "Django"]}),
    create_mock_job_description({"title": "React Developer", "required_skills": ["React", "JavaScript"]}),
    create_mock_job_description({"title": "Java Developer", "required_skills": ["Java", "Spring Boot"]})
]