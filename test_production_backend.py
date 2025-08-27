#!/usr/bin/env python3
"""
Test the PRODUCTION backend API to see if there's an issue with the production-specific workflow
"""

import requests
import json
import sys

def test_production_backend():
    print("🔍 Testing PRODUCTION backend API endpoints")
    
    # Test data similar to what user would upload
    test_cv = {
        "cv_text": """John Smith
Software Engineer
john@email.com

EXPERIENCE:
Senior Developer at TechCorp (2020-2023)
- Built Python applications using Flask and Django
- React frontend development with TypeScript
- AWS cloud deployment using Docker containers
- Led team of 3 junior developers

SKILLS:
Python, JavaScript, React, AWS, Docker, PostgreSQL"""
    }
    
    test_jd_data = {
        "text": """Senior Software Engineer Position

REQUIREMENTS:
- 5+ years of Python development experience
- Strong React and JavaScript skills
- AWS cloud platform experience  
- Docker containerization knowledge
- Leadership experience mentoring developers

RESPONSIBILITIES:
- Lead development of scalable web applications
- Mentor junior developers
- Design system architecture""",
        "title": "Senior Software Engineer",
        "company": "Test Company"
    }

    try:
        print("📄 Step 1: Test CV upload via production backend...")
        cv_response = requests.post('http://localhost:3001/api/cvs/upload', 
                                  files={'file': ('test_cv.txt', test_cv['cv_text'], 'text/plain')},
                                  timeout=30)
        
        if cv_response.status_code == 200:
            cv_result = cv_response.json()
            print(f"✅ CV uploaded successfully, ID: {cv_result.get('cv', {}).get('id')}")
            cv_id = cv_result['cv']['id']
        else:
            print(f"❌ CV upload failed: {cv_response.status_code}")
            print(cv_response.text)
            return False
        
        print("📋 Step 2: Test JD creation via production backend...")
        jd_response = requests.post('http://localhost:3001/api/job_descriptions', 
                                  json=test_jd_data,
                                  headers={'Content-Type': 'application/json'},
                                  timeout=30)
        
        if jd_response.status_code == 200:
            jd_result = jd_response.json()
            print(f"✅ JD created successfully, ID: {jd_result.get('job_description', {}).get('id')}")
            jd_id = jd_result['job_description']['id']
        else:
            print(f"❌ JD creation failed: {jd_response.status_code}")
            print(jd_response.text)
            return False
        
        print("🔍 Step 3: Test comparison analysis via production backend...")
        comparison_data = {
            "cv_id": cv_id,
            "job_description_id": jd_id
        }
        
        comparison_response = requests.post('http://localhost:3001/api/comparisons', 
                                          json=comparison_data,
                                          headers={'Content-Type': 'application/json'},
                                          timeout=180)
        
        if comparison_response.status_code == 200:
            comparison_result = comparison_response.json()
            print(f"✅ Comparison created successfully")
            
            # Extract the comparison data
            comparison = comparison_result.get('comparison', {})
            highlighted_content = comparison.get('highlighted_content', {})
            
            cv_highlighted = highlighted_content.get('cv_highlighted', '')
            jd_highlighted = highlighted_content.get('jd_highlighted', '')
            
            print(f"📊 Analysis Results:")
            print(f"   • Match score: {comparison.get('match_score', 0)}%")
            print(f"   • CV highlighted length: {len(cv_highlighted)}")
            print(f"   • JD highlighted length: {len(jd_highlighted)}")
            
            # Count highlighting classes in PRODUCTION output
            cv_matches = cv_highlighted.count('class="highlight-match"')
            cv_potentials = cv_highlighted.count('class="highlight-potential"')
            cv_gaps = cv_highlighted.count('class="highlight-gap"')
            
            jd_matches = jd_highlighted.count('class="highlight-match"')
            jd_potentials = jd_highlighted.count('class="highlight-potential"')
            jd_gaps = jd_highlighted.count('class="highlight-gap"')
            
            print(f"🎨 PRODUCTION HTML CLASS COUNTS:")
            print(f"   CV:  Green={cv_matches}, Yellow={cv_potentials}, Red={cv_gaps}")
            print(f"   JD:  Green={jd_matches}, Yellow={jd_potentials}, Red={jd_gaps}")
            
            # Check for "all green" issue in PRODUCTION
            jd_total = jd_matches + jd_potentials + jd_gaps
            if jd_total > 0 and jd_matches == jd_total:
                print("❌ PRODUCTION ISSUE CONFIRMED: ALL JD IS GREEN")
                print("🔍 The production backend is generating all-green highlighting!")
            elif jd_total == 0:
                print("❌ NO HIGHLIGHTING FOUND IN PRODUCTION OUTPUT")
            else:
                print("✅ Production backend generates mixed highlighting")
            
            # Save production output for inspection
            production_html = f"""<!DOCTYPE html>
<html><head>
<title>PRODUCTION Backend Output</title>
<style>
.highlight-match {{ background-color: #27ca3f; color: #000000; padding: 2px 4px; font-weight: 600; }}
.highlight-potential {{ background-color: #ffbd2e; color: #000000; padding: 2px 4px; font-weight: 600; }}
.highlight-gap {{ background-color: #ff5f56; color: #000000; padding: 2px 4px; font-weight: 600; }}
.content {{ font-family: monospace; white-space: pre-wrap; margin: 20px; padding: 20px; background: #111; color: white; }}
</style>
</head><body>
<h1>PRODUCTION Backend Output</h1>
<h2>Match Score: {comparison.get('match_score', 0)}%</h2>

<h3>CV Highlighted (Green={cv_matches}, Yellow={cv_potentials}, Red={cv_gaps}):</h3>
<div class="content">{cv_highlighted}</div>

<h3>JD Highlighted (Green={jd_matches}, Yellow={jd_potentials}, Red={jd_gaps}):</h3>
<div class="content">{jd_highlighted}</div>
</body></html>"""
            
            with open("production_backend_output.html", "w") as f:
                f.write(production_html)
            print("💾 Saved: production_backend_output.html")
            
            # Show a sample of JD highlighting
            if jd_highlighted:
                print(f"\\n📋 Sample JD highlighting (first 500 chars):")
                print(jd_highlighted[:500] + "...")
            
            return True
            
        else:
            print(f"❌ Comparison failed: {comparison_response.status_code}")
            print(comparison_response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_production_backend()
    if success:
        print("\\n🔍 Check production_backend_output.html to see the actual production output!")
    exit(0 if success else 1)