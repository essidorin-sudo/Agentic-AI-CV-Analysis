#!/usr/bin/env python3
"""
Direct backend test - simulate exact user workflow and check final HTML output
This bypasses all frontend/auth complexity and tests what actually gets generated
"""

import requests
import json
import sys
import os

def test_complete_backend_flow():
    print("🔍 TESTING COMPLETE BACKEND FLOW (what user actually sees)")
    
    # Real user data
    cv_content = """John Smith
Software Engineer
john.smith@email.com
Phone: (555) 123-4567

EXPERIENCE:
Senior Software Developer at TechCorp (2020-2023)
• Built scalable Python applications using Flask and Django frameworks
• Developed React frontend applications with TypeScript and modern JavaScript
• Deployed cloud infrastructure on AWS using Docker containers
• Led a team of 3 junior developers on multiple projects
• Designed PostgreSQL database schemas for large-scale applications

Junior Developer at StartupCo (2018-2020)
• JavaScript web application development
• Database design and optimization with PostgreSQL
• Collaborated with cross-functional teams on agile projects

EDUCATION:
Bachelor of Science in Computer Science
University of Technology (2014-2018)

SKILLS:
Programming Languages: Python, JavaScript, TypeScript, SQL
Frameworks: Flask, Django, React, Node.js
Cloud & DevOps: AWS, Docker, Git, CI/CD
Databases: PostgreSQL, MongoDB
Other: Agile/Scrum, Team Leadership"""

    jd_content = """Senior Software Engineer Position
San Francisco, CA | Remote-Friendly
Salary: $120,000 - $160,000

ABOUT THE ROLE:
We are seeking a Senior Software Engineer to join our growing engineering team. You will be responsible for designing, developing, and maintaining scalable web applications that serve millions of users worldwide.

REQUIREMENTS:
• 5+ years of professional Python development experience
• Strong experience with React and modern JavaScript frameworks
• Proficiency with AWS cloud platform and containerization (Docker)
• Experience with Docker containerization and deployment
• Database design experience, preferably PostgreSQL
• Leadership experience mentoring junior developers
• Bachelor's degree in Computer Science or related field

RESPONSIBILITIES:
• Lead development of scalable web applications and APIs
• Mentor and guide junior developers in best practices
• Design and implement system architecture and technical solutions
• Deploy and maintain cloud infrastructure on AWS
• Collaborate with product and design teams on feature development
• Participate in code reviews and maintain high coding standards

NICE TO HAVE:
• Experience with microservices architecture
• Knowledge of machine learning and AI technologies
• Experience with agile development methodologies
• Open source contributions

BENEFITS:
• Competitive salary and equity package
• Comprehensive health, dental, and vision insurance
• 401(k) with company matching
• Flexible PTO policy
• $2,000 annual learning and development budget"""

    try:
        print("📄 Step 1: Processing CV...")
        cv_response = requests.post('http://localhost:5005/parse', 
                                  json={'cv_text': cv_content}, 
                                  timeout=30)
        
        if cv_response.status_code != 200:
            print(f"❌ CV processing failed: {cv_response.status_code}")
            print(cv_response.text)
            return False
            
        cv_data = cv_response.json()['result']
        print(f"✅ CV processed successfully")
        print(f"   • Raw text length: {len(cv_data.get('raw_text', ''))}")
        
        print("📋 Step 2: Processing JD...")
        jd_response = requests.post('http://localhost:5007/parse', 
                                  json={'jd_text': jd_content}, 
                                  timeout=30)
        
        if jd_response.status_code != 200:
            print(f"❌ JD processing failed: {jd_response.status_code}")
            print(jd_response.text)
            return False
            
        jd_data = jd_response.json()['result']
        print(f"✅ JD processed successfully")
        print(f"   • Raw text length: {len(jd_data.get('raw_text', ''))}")
        
        print("🔍 Step 3: Running Gap Analysis...")
        gap_response = requests.post('http://localhost:5008/analyze_gap', 
                                   json={
                                       'cv_data': cv_data,
                                       'jd_data': jd_data
                                   }, 
                                   timeout=180)
        
        if gap_response.status_code != 200:
            print(f"❌ Gap analysis failed: {gap_response.status_code}")
            print(gap_response.text)
            return False
            
        gap_data = gap_response.json()['result']
        print(f"✅ Gap analysis completed")
        print(f"   • Overall match score: {gap_data.get('match_score', {}).get('overall_score', 0)}%")
        
        # Get highlighting instructions
        cv_highlighting = gap_data.get('cv_highlighted', [])
        jd_highlighting = gap_data.get('jd_highlighted', [])
        
        print(f"   • CV highlighting instructions: {len(cv_highlighting)}")
        print(f"   • JD highlighting instructions: {len(jd_highlighting)}")
        
        # Analyze highlighting distribution
        jd_match_count = sum(1 for inst in jd_highlighting if inst.get('class') == 'highlight-match')
        jd_potential_count = sum(1 for inst in jd_highlighting if inst.get('class') == 'highlight-potential')
        jd_gap_count = sum(1 for inst in jd_highlighting if inst.get('class') == 'highlight-gap')
        
        print(f"🎨 JD Highlighting Distribution:")
        print(f"   • Green (match): {jd_match_count}")
        print(f"   • Yellow (potential): {jd_potential_count}")
        print(f"   • Red (gap): {jd_gap_count}")
        
        if jd_match_count > 0 and jd_potential_count == 0 and jd_gap_count == 0:
            print("❌ PROBLEM CONFIRMED: All JD highlighting is green (matches user complaint)")
        else:
            print("✅ JD highlighting appears mixed")
        
        print("🎨 Step 4: Generating final HTML (what user sees)...")
        
        # Import the backend function to simulate what happens
        sys.path.append('/Users/eugenes/Desktop/Agentic-AI-CV-Analysis/production-system/backend')
        from app import apply_highlighting_instructions
        
        cv_raw_text = cv_data.get('raw_text', '')
        jd_raw_text = jd_data.get('raw_text', '')
        
        # Generate the exact HTML the user would see
        cv_highlighted_html = apply_highlighting_instructions(cv_raw_text, cv_highlighting)
        jd_highlighted_html = apply_highlighting_instructions(jd_raw_text, jd_highlighting)
        
        print(f"✅ HTML generated:")
        print(f"   • CV HTML length: {len(cv_highlighted_html)}")
        print(f"   • JD HTML length: {len(jd_highlighted_html)}")
        
        # Count actual HTML highlighting classes
        cv_html_matches = cv_highlighted_html.count('class="highlight-match"')
        cv_html_potentials = cv_highlighted_html.count('class="highlight-potential"')
        cv_html_gaps = cv_highlighted_html.count('class="highlight-gap"')
        
        jd_html_matches = jd_highlighted_html.count('class="highlight-match"')
        jd_html_potentials = jd_highlighted_html.count('class="highlight-potential"')
        jd_html_gaps = jd_highlighted_html.count('class="highlight-gap"')
        
        print(f"🎨 FINAL HTML CLASS COUNTS:")
        print(f"   CV:  Green={cv_html_matches}, Yellow={cv_html_potentials}, Red={cv_html_gaps}")
        print(f"   JD:  Green={jd_html_matches}, Yellow={jd_html_potentials}, Red={jd_html_gaps}")
        
        # CRITICAL DIAGNOSIS
        jd_total = jd_html_matches + jd_html_potentials + jd_html_gaps
        if jd_total > 0 and jd_html_matches == jd_total:
            print("❌ CONFIRMED USER ISSUE: ALL JD HTML IS GREEN")
            print("🔍 This matches exactly what the user reported!")
        else:
            print("✅ JD HTML has mixed highlighting")
        
        # Step 5: Create exact replica of what user sees
        print("💾 Step 5: Creating exact user experience files...")
        
        # Create the exact HTML that would be rendered in the browser
        full_page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV Analysis Results - What User Actually Sees</title>
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            margin: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .results-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }}
        
        .panel {{
            background: #111111;
            border: 1px solid #333333;
            border-radius: 8px;
        }}
        
        .panel-header {{
            background: #1a1a1a;
            border-bottom: 1px solid #333333;
            padding: 12px 16px;
            font-weight: 600;
            font-size: 14px;
        }}
        
        .panel-content {{
            padding: 16px;
            min-width: 0;
            width: 100%;
            box-sizing: border-box;
        }}
        
        /* This is the EXACT CSS from the frontend */
        .cv-content {{
            min-width: 0;
            width: 100%;
            box-sizing: border-box;
            font-family: monospace;
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
            background: #0a0a0a;
            color: white;
            padding: 16px;
            border: 1px solid #333;
        }}
        
        .highlight-match {{
            background-color: #27ca3f;
            color: #000000;
            padding: 2px 4px;
            font-weight: 600;
        }}
        
        .highlight-potential {{
            background-color: #ffbd2e;
            color: #000000;
            padding: 2px 4px;
            font-weight: 600;
        }}
        
        .highlight-gap {{
            background-color: #ff5f56;
            color: #ffffff;
            padding: 2px 4px;
            font-weight: 600;
        }}
        
        .diagnosis {{
            background: #ff0000;
            color: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            font-weight: bold;
        }}
        
        .success {{
            background: #00ff00;
            color: black;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>CV ANALYSIS RESULTS - EXACT USER EXPERIENCE</h1>
        
        <div class="{'diagnosis' if jd_total > 0 and jd_html_matches == jd_total else 'success'}">
            {'❌ PROBLEM CONFIRMED: ALL JD TEXT IS HIGHLIGHTED GREEN!' if jd_total > 0 and jd_html_matches == jd_total else '✅ Mixed highlighting detected'}
        </div>
        
        <p><strong>Match Score:</strong> {gap_data.get('match_score', {}).get('overall_score', 0)}%</p>
        <p><strong>Highlighting Counts:</strong></p>
        <ul>
            <li>CV: Green={cv_html_matches}, Yellow={cv_html_potentials}, Red={cv_html_gaps}</li>
            <li>JD: Green={jd_html_matches}, Yellow={jd_html_potentials}, Red={jd_html_gaps}</li>
        </ul>
        
        <div class="results-grid">
            <div class="panel">
                <div class="panel-header">CV ANALYSIS</div>
                <div class="panel-content">
                    {cv_highlighted_html}
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">JOB DESCRIPTION ANALYSIS</div>
                <div class="panel-content">
                    {jd_highlighted_html}
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
        
        with open("exact_user_experience.html", "w") as f:
            f.write(full_page_html)
        
        print("📄 Files created:")
        print("   • exact_user_experience.html - EXACT replica of what user sees")
        
        # Also save individual components
        with open("cv_highlighted_only.html", "w") as f:
            f.write(f"<html><head><style>.highlight-match{{background:#27ca3f;color:#000}}.highlight-potential{{background:#ffbd2e;color:#000}}.highlight-gap{{background:#ff5f56;color:#fff}}</style></head><body>{cv_highlighted_html}</body></html>")
        
        with open("jd_highlighted_only.html", "w") as f:
            f.write(f"<html><head><style>.highlight-match{{background:#27ca3f;color:#000}}.highlight-potential{{background:#ffbd2e;color:#000}}.highlight-gap{{background:#ff5f56;color:#fff}}</style></head><body>{jd_highlighted_html}</body></html>")
        
        print("   • cv_highlighted_only.html")
        print("   • jd_highlighted_only.html")
        
        print("\\n🔍 FINAL DIAGNOSIS:")
        if jd_total > 0 and jd_html_matches == jd_total:
            print("❌ USER'S COMPLAINT IS VALID:")
            print("   • All JD text is indeed highlighted green")
            print("   • This confirms the user's report")
            print("   • The issue is in the Gap Analyst logic, not frontend")
        else:
            print("✅ Mixed highlighting detected - issue may be elsewhere")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_backend_flow()
    print("\\n🔍 Open 'exact_user_experience.html' to see what the user actually sees!")
    exit(0 if success else 1)