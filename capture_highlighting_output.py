#!/usr/bin/env python3
"""
Capture current highlighting output to analyze what's actually happening vs expectations
"""
import requests
import json
from datetime import datetime

def capture_current_highlighting():
    """Capture the actual highlighting output from Gap Analyst"""
    
    # Test data
    sample_cv = {
        "full_name": "John Doe",
        "key_skills": ["Python", "JavaScript", "React", "SQL", "Git"],
        "work_experience": [
            {
                "position": "Software Engineer",
                "company": "Tech Solutions Inc",
                "duration": "2021-2024",
                "responsibilities": [
                    "Developed web applications using React and Node.js",
                    "Collaborated with cross-functional teams", 
                    "Implemented REST APIs and database integrations"
                ]
            },
            {
                "position": "Junior Developer", 
                "company": "StartupCorp",
                "duration": "2020-2021",
                "responsibilities": [
                    "Built responsive web interfaces with HTML, CSS, JavaScript",
                    "Worked with SQL databases and basic backend services"
                ]
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "institution": "State University", 
                "graduation": "2020"
            }
        ]
    }
    
    sample_jd = {
        "job_title": "Senior Software Engineer",
        "company_name": "Innovation Labs",
        "required_skills": ["Python", "React", "AWS", "Docker", "Kubernetes", "Microservices"],
        "preferred_skills": ["GraphQL", "TypeScript", "CI/CD", "Terraform"],
        "required_experience": [
            "5+ years of software development experience",
            "Experience with cloud platforms and containerization",
            "Leadership experience mentoring junior developers",
            "Experience with agile development methodologies"
        ],
        "required_education": ["Bachelor's degree in Computer Science or related field"],
        "key_responsibilities": [
            "Lead development of scalable web applications",
            "Architect and implement microservices solutions", 
            "Mentor junior developers and conduct code reviews",
            "Collaborate with DevOps team on CI/CD pipelines"
        ]
    }
    
    url = "http://localhost:5006/analyze_gap"
    payload = {"cv_data": sample_cv, "jd_data": sample_jd}
    
    try:
        print("🔍 Capturing current highlighting output...")
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                gap_result = result['result']
                
                # Capture the raw highlighting data
                output_data = {
                    "timestamp": datetime.now().isoformat(),
                    "cv_data": sample_cv,
                    "jd_data": sample_jd,
                    "cv_highlighted": gap_result.get('cv_highlighted', []),
                    "jd_highlighted": gap_result.get('jd_highlighted', []),
                    "match_scores": {
                        "overall_score": gap_result['match_score']['overall_score'],
                        "skills_score": gap_result['match_score']['skills_score'],
                        "experience_score": gap_result['match_score']['experience_score'],
                        "education_score": gap_result['match_score']['education_score']
                    }
                }
                
                # Save to file for analysis
                with open('/Users/eugenes/Desktop/Agentic-AI-CV-Analysis/current_highlighting_output.json', 'w') as f:
                    json.dump(output_data, f, indent=2)
                
                print(f"✅ Captured highlighting output to current_highlighting_output.json")
                
                # Print analysis
                print(f"\n📊 Analysis Summary:")
                print(f"   Overall Score: {output_data['match_scores']['overall_score']}")
                print(f"   CV Highlights: {len(output_data['cv_highlighted'])}")
                print(f"   JD Highlights: {len(output_data['jd_highlighted'])}")
                
                print(f"\n🔍 CV Highlighting Details:")
                for i, highlight in enumerate(output_data['cv_highlighted'], 1):
                    print(f"   {i}. Address: {highlight.get('address', 'N/A')}")
                    print(f"      Class: {highlight.get('class', 'N/A')}")
                    print(f"      Reason: {highlight.get('reason', 'N/A')[:100]}{'...' if len(highlight.get('reason', '')) > 100 else ''}")
                    print()
                
                print(f"🔍 JD Highlighting Details:")
                for i, highlight in enumerate(output_data['jd_highlighted'], 1):
                    print(f"   {i}. Address: {highlight.get('address', 'N/A')}")
                    print(f"      Class: {highlight.get('class', 'N/A')}")
                    print(f"      Reason: {highlight.get('reason', 'N/A')[:100]}{'...' if len(highlight.get('reason', '')) > 100 else ''}")
                    print()
                
                return True
            else:
                print(f"❌ Gap analysis failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = capture_current_highlighting()
    if not success:
        print("💥 Failed to capture highlighting output")