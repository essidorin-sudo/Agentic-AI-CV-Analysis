#!/usr/bin/env python3
"""
Debug the actual highlighting instructions and see what's going wrong
"""

import requests
import json
import sys
import os
sys.path.append('/Users/eugenes/Desktop/Agentic-AI-CV-Analysis/production-system/backend')

def debug_highlighting():
    print("🔍 DEBUGGING HIGHLIGHTING INSTRUCTIONS...")
    
    # Test data
    cv_content = """John Smith
Software Engineer
john@email.com

EXPERIENCE:
Senior Developer at TechCorp (2020-2023)
- Built Python applications with Flask and Django
- React frontend development with TypeScript
- AWS cloud deployment using Docker

SKILLS:
Python, JavaScript, React, AWS, Docker, PostgreSQL"""

    jd_content = """Senior Software Engineer Position

REQUIREMENTS:
- 5+ years of Python development experience
- Strong React and JavaScript skills  
- AWS cloud platform experience
- Docker containerization knowledge

RESPONSIBILITIES:
- Lead development of scalable web applications
- Mentor junior developers"""

    try:
        # Get parsed data
        print("📄 Getting CV data...")
        cv_response = requests.post('http://localhost:5005/parse', json={'cv_text': cv_content})
        cv_data = cv_response.json()['result']
        
        print("📋 Getting JD data...")
        jd_response = requests.post('http://localhost:5007/parse', json={'jd_text': jd_content})
        jd_data = jd_response.json()['result']
        
        print("\n🔍 EXAMINING RAW TEXT WITH ADDRESS MARKUP...")
        cv_raw = cv_data.get('raw_text', '')
        jd_raw = jd_data.get('raw_text', '')
        
        print(f"CV Raw Text (first 300 chars):")
        print(cv_raw[:300] + "...")
        print(f"\nJD Raw Text (first 300 chars):")
        print(jd_raw[:300] + "...")
        
        # Get highlighting instructions
        print("\n🔍 Getting highlighting instructions...")
        gap_response = requests.post('http://localhost:5008/analyze_gap', json={
            'cv_data': cv_data,
            'jd_data': jd_data
        })
        gap_data = gap_response.json()['result']
        
        cv_instructions = gap_data.get('cv_highlighted', [])
        jd_instructions = gap_data.get('jd_highlighted', [])
        
        print(f"\n📊 HIGHLIGHTING INSTRUCTIONS ANALYSIS:")
        print(f"CV Instructions: {len(cv_instructions)}")
        print(f"JD Instructions: {len(jd_instructions)}")
        
        print(f"\n🎨 CV HIGHLIGHTING INSTRUCTIONS:")
        for i, inst in enumerate(cv_instructions):
            print(f"  {i+1}. Address: {inst.get('address', 'N/A')}")
            print(f"     Class: {inst.get('class', 'N/A')}")
            print(f"     Reason: {inst.get('reason', 'N/A')[:50]}...")
            print()
            
        print(f"\n🎨 JD HIGHLIGHTING INSTRUCTIONS:")
        for i, inst in enumerate(jd_instructions):
            print(f"  {i+1}. Address: {inst.get('address', 'N/A')}")
            print(f"     Class: {inst.get('class', 'N/A')}")
            print(f"     Reason: {inst.get('reason', 'N/A')[:50]}...")
            print()
        
        # Count classes
        cv_match_count = sum(1 for inst in cv_instructions if inst.get('class') == 'highlight-match')
        cv_potential_count = sum(1 for inst in cv_instructions if inst.get('class') == 'highlight-potential') 
        cv_gap_count = sum(1 for inst in cv_instructions if inst.get('class') == 'highlight-gap')
        
        jd_match_count = sum(1 for inst in jd_instructions if inst.get('class') == 'highlight-match')
        jd_potential_count = sum(1 for inst in jd_instructions if inst.get('class') == 'highlight-potential')
        jd_gap_count = sum(1 for inst in jd_instructions if inst.get('class') == 'highlight-gap')
        
        print(f"\n📈 CLASS DISTRIBUTION:")
        print(f"CV:  Green={cv_match_count}, Yellow={cv_potential_count}, Red={cv_gap_count}")
        print(f"JD:  Green={jd_match_count}, Yellow={jd_potential_count}, Red={jd_gap_count}")
        
        # Check for "all green" issue at the instruction level
        if jd_match_count == len(jd_instructions) and len(jd_instructions) > 0:
            print("❌ PROBLEM FOUND: All JD instructions are 'highlight-match' (green)")
        else:
            print("✅ JD instructions have mixed classes")
            
        if cv_match_count == len(cv_instructions) and len(cv_instructions) > 0:
            print("❌ PROBLEM FOUND: All CV instructions are 'highlight-match' (green)")
        else:
            print("✅ CV instructions have mixed classes")
        
        # Now test the backend function directly
        print(f"\n🔧 TESTING BACKEND HIGHLIGHTING FUNCTION...")
        
        # Import and test the actual function
        from app import apply_highlighting_instructions
        
        cv_highlighted = apply_highlighting_instructions(cv_raw, cv_instructions)
        jd_highlighted = apply_highlighting_instructions(jd_raw, jd_instructions)
        
        print(f"Generated CV HTML length: {len(cv_highlighted)}")
        print(f"Generated JD HTML length: {len(jd_highlighted)}")
        
        # Count actual HTML classes
        cv_html_matches = cv_highlighted.count('class="highlight-match"')
        cv_html_potentials = cv_highlighted.count('class="highlight-potential"')
        cv_html_gaps = cv_highlighted.count('class="highlight-gap"')
        
        jd_html_matches = jd_highlighted.count('class="highlight-match"')
        jd_html_potentials = jd_highlighted.count('class="highlight-potential"')
        jd_html_gaps = jd_highlighted.count('class="highlight-gap"')
        
        print(f"\n🎨 ACTUAL HTML CLASSES:")
        print(f"CV HTML:  Green={cv_html_matches}, Yellow={cv_html_potentials}, Red={cv_html_gaps}")
        print(f"JD HTML:  Green={jd_html_matches}, Yellow={jd_html_potentials}, Red={jd_html_gaps}")
        
        # Final diagnosis
        print(f"\n🏥 DIAGNOSIS:")
        if jd_html_matches > 0 and jd_html_potentials == 0 and jd_html_gaps == 0:
            print("❌ CONFIRMED: JD HTML only has green highlighting")
            print("🔍 Root cause: Gap Analyst only returning 'highlight-match' instructions for JD")
        else:
            print("✅ JD HTML has mixed highlighting")
            
        # Save sample HTML files
        with open("debug_cv.html", "w") as f:
            f.write(f"""<!DOCTYPE html><html><head><style>
.cv-content {{ font-family: monospace; white-space: pre-wrap; background: #000; color: #fff; padding: 10px; }}
.highlight-match {{ background-color: #27ca3f; color: #000; padding: 2px; font-weight: bold; }}
.highlight-potential {{ background-color: #ffca28; color: #000; padding: 2px; font-weight: bold; }}
.highlight-gap {{ background-color: #ef5350; color: #fff; padding: 2px; font-weight: bold; }}
</style></head><body>{cv_highlighted}</body></html>""")
            
        with open("debug_jd.html", "w") as f:
            f.write(f"""<!DOCTYPE html><html><head><style>
.cv-content {{ font-family: monospace; white-space: pre-wrap; background: #000; color: #fff; padding: 10px; }}
.highlight-match {{ background-color: #27ca3f; color: #000; padding: 2px; font-weight: bold; }}
.highlight-potential {{ background-color: #ffca28; color: #000; padding: 2px; font-weight: bold; }}
.highlight-gap {{ background-color: #ef5350; color: #fff; padding: 2px; font-weight: bold; }}
</style></head><body>{jd_highlighted}</body></html>""")
            
        print(f"\n💾 Debug HTML files saved:")
        print(f"  • debug_cv.html")
        print(f"  • debug_jd.html")
        print(f"\n🔍 Open these files to see the EXACT output!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Change to backend directory to import the function
    os.chdir('/Users/eugenes/Desktop/Agentic-AI-CV-Analysis/production-system/backend')
    debug_highlighting()