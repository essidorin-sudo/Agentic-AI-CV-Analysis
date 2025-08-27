#!/usr/bin/env python3
"""
Skip the auth complexity and directly inspect what the backend is producing
by making API calls and checking the HTML output that would be displayed
"""

import requests
import json
import re
from pathlib import Path

def test_backend_html_output():
    print("🔍 Testing what HTML the backend actually produces...")
    
    # Create test data
    cv_content = """John Smith
Software Engineer
john@email.com

EXPERIENCE:
Senior Developer at TechCorp (2020-2023)
- Built Python applications with Flask and Django
- React frontend development with TypeScript
- AWS cloud deployment using Docker

Junior Developer at StartupCo (2018-2020)
- JavaScript development
- Database design with PostgreSQL

SKILLS:
Python, JavaScript, React, AWS, Docker, PostgreSQL"""

    jd_content = """Senior Software Engineer Position
San Francisco, CA

REQUIREMENTS:
- 5+ years of Python development experience
- Strong React and JavaScript skills  
- AWS cloud platform experience
- Docker containerization knowledge
- Database design experience (PostgreSQL preferred)
- Leadership experience

RESPONSIBILITIES:
- Lead development of scalable web applications
- Mentor junior developers
- Design system architecture
- Deploy and maintain cloud infrastructure

QUALIFICATIONS:
- Bachelor's degree in Computer Science
- Experience with agile methodologies"""

    try:
        print("📄 Step 1: Processing CV...")
        cv_response = requests.post('http://localhost:5005/parse', json={'cv_text': cv_content})
        if cv_response.status_code != 200:
            print(f"❌ CV Parser failed: {cv_response.status_code}")
            return False
        cv_data = cv_response.json()['result']
        print(f"✅ CV parsed, raw_text length: {len(cv_data.get('raw_text', ''))}")
        
        print("📋 Step 2: Processing JD...")
        jd_response = requests.post('http://localhost:5007/parse', json={'jd_text': jd_content})
        if jd_response.status_code != 200:
            print(f"❌ JD Parser failed: {jd_response.status_code}")
            return False
        jd_data = jd_response.json()['result']
        print(f"✅ JD parsed, raw_text length: {len(jd_data.get('raw_text', ''))}")
        
        print("🔍 Step 3: Running Gap Analysis...")
        gap_response = requests.post('http://localhost:5008/analyze_gap', json={
            'cv_data': cv_data,
            'jd_data': jd_data
        })
        if gap_response.status_code != 200:
            print(f"❌ Gap Analysis failed: {gap_response.status_code}")
            return False
        
        gap_data = gap_response.json()['result']
        cv_highlighting = gap_data.get('cv_highlighted', [])
        jd_highlighting = gap_data.get('jd_highlighted', [])
        
        print(f"✅ Gap Analysis complete:")
        print(f"  • CV highlighting instructions: {len(cv_highlighting)}")
        print(f"  • JD highlighting instructions: {len(jd_highlighting)}")
        print(f"  • Match score: {gap_data.get('match_score', {}).get('overall_score', 0)}%")
        
        # Step 4: Simulate what the backend does to create highlighted HTML
        print("🎨 Step 4: Simulating backend HTML generation...")
        
        from production_system.backend.app import apply_highlighting_instructions
        
        cv_raw_text = cv_data.get('raw_text', '')
        jd_raw_text = jd_data.get('raw_text', '')
        
        # Apply highlighting using the actual backend function
        cv_highlighted_html = apply_highlighting_instructions(cv_raw_text, cv_highlighting)
        jd_highlighted_html = apply_highlighting_instructions(jd_raw_text, jd_highlighting)
        
        print(f"✅ Generated highlighted HTML:")
        print(f"  • CV HTML length: {len(cv_highlighted_html)}")
        print(f"  • JD HTML length: {len(jd_highlighted_html)}")
        
        # Step 5: Analyze the HTML for issues
        print("🔍 Step 5: Analyzing generated HTML...")
        
        # Count highlighting classes
        cv_match_count = cv_highlighted_html.count('class="highlight-match"')
        cv_potential_count = cv_highlighted_html.count('class="highlight-potential"')
        cv_gap_count = cv_highlighted_html.count('class="highlight-gap"')
        
        jd_match_count = jd_highlighted_html.count('class="highlight-match"')
        jd_potential_count = jd_highlighted_html.count('class="highlight-potential"')
        jd_gap_count = jd_highlighted_html.count('class="highlight-gap"')
        
        print(f"🎨 CV Highlighting breakdown:")
        print(f"  • Green (match): {cv_match_count}")
        print(f"  • Yellow (potential): {cv_potential_count}")
        print(f"  • Red (gap): {cv_gap_count}")
        
        print(f"🎨 JD Highlighting breakdown:")
        print(f"  • Green (match): {jd_match_count}")
        print(f"  • Yellow (potential): {jd_potential_count}")
        print(f"  • Red (gap): {jd_gap_count}")
        
        # Check for "all green" issue
        cv_total = cv_match_count + cv_potential_count + cv_gap_count
        jd_total = jd_match_count + jd_potential_count + jd_gap_count
        
        if jd_total > 0 and jd_match_count == jd_total:
            print("❌ ISSUE FOUND: ALL JD text is highlighted green (match)")
        else:
            print("✅ JD highlighting appears varied")
            
        if cv_total > 0 and cv_match_count == cv_total:
            print("❌ ISSUE FOUND: ALL CV text is highlighted green (match)")
        else:
            print("✅ CV highlighting appears varied")
        
        # Step 6: Check formatting issues
        print("📐 Step 6: Checking formatting...")
        
        if '<pre class=' in cv_highlighted_html or '<pre class=' in jd_highlighted_html:
            print("⚠️  Using <pre> tags - may cause grid layout issues")
        
        if '<div class=' in cv_highlighted_html or '<div class=' in jd_highlighted_html:
            print("✅ Using <div> tags - better for grid layouts")
        
        # Step 7: Save HTML files for inspection
        print("💾 Step 7: Saving HTML files for inspection...")
        
        with open("generated_cv_highlighted.html", "w") as f:
            f.write(f"""<!DOCTYPE html>
<html><head>
<style>
.cv-content {{ 
    font-family: monospace; 
    font-size: 13px; 
    line-height: 1.6; 
    white-space: pre-wrap; 
    background: #0a0a0a; 
    color: white; 
    padding: 16px; 
    border: 1px solid #333; 
}}
.highlight-match {{ background-color: #27ca3f; color: #000; padding: 2px 4px; font-weight: 600; }}
.highlight-potential {{ background-color: #ffca28; color: #000; padding: 2px 4px; font-weight: 600; }}
.highlight-gap {{ background-color: #ef5350; color: #fff; padding: 2px 4px; font-weight: 600; }}
</style>
</head><body>
{cv_highlighted_html}
</body></html>""")
        
        with open("generated_jd_highlighted.html", "w") as f:
            f.write(f"""<!DOCTYPE html>
<html><head>
<style>
.cv-content {{ 
    font-family: monospace; 
    font-size: 13px; 
    line-height: 1.6; 
    white-space: pre-wrap; 
    background: #0a0a0a; 
    color: white; 
    padding: 16px; 
    border: 1px solid #333; 
}}
.highlight-match {{ background-color: #27ca3f; color: #000; padding: 2px 4px; font-weight: 600; }}
.highlight-potential {{ background-color: #ffca28; color: #000; padding: 2px 4px; font-weight: 600; }}
.highlight-gap {{ background-color: #ef5350; color: #fff; padding: 2px 4px; font-weight: 600; }}
</style>
</head><body>
{jd_highlighted_html}
</body></html>""")
        
        print("📄 Files saved:")
        print("  • generated_cv_highlighted.html")
        print("  • generated_jd_highlighted.html")
        print("\n🔍 Open these files in a browser to see exactly what would be displayed!")
        
        # Step 8: Print sample HTML for debugging
        print("\n📋 Sample CV HTML (first 500 chars):")
        print(cv_highlighted_html[:500] + "...")
        
        print("\n📋 Sample JD HTML (first 500 chars):")
        print(jd_highlighted_html[:500] + "...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_backend_html_output()
    exit(0 if success else 1)