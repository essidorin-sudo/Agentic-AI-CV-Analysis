#!/usr/bin/env python3
"""
Sample Test for JD Parser Agent

Simple test script to verify agent functionality with sample data.
"""

from agent import JDParserAgent

def main():
    """Run sample test"""
    print("🤖 JD Parser Agent v2.0.0 - Sample Test")
    print("=" * 50)
    
    # Sample job description
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
    
    # Test the agent
    agent = JDParserAgent()
    result = agent.parse_job_description(sample_jd)
    
    print(f"\n🎯 Job Overview")
    print(f"Job Title: {result.job_title}")
    print(f"Company: {result.company_name}")
    print(f"Location: {result.location}")
    print(f"Confidence: {result.confidence_score*100:.0f}%")
    
    print(f"\n🛠️ Skills & Requirements")
    if result.required_skills:
        print("Required Skills:", ", ".join(result.required_skills))
    if result.preferred_skills:
        print("Preferred Skills:", ", ".join(result.preferred_skills))
    
    print(f"\n🔍 Parsing Notes")
    for note in result.parsing_notes:
        print(f"- {note}")


if __name__ == "__main__":
    main()