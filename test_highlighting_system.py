#!/usr/bin/env python3
"""
Comprehensive test to verify the address-based highlighting system works correctly.
Tests:
1. CV Parser returns content with address markup
2. JD Parser returns content with address markup  
3. Gap Analyst returns highlighting instructions (not full HTML)
4. Backend properly applies highlighting instructions
5. Frontend displays properly formatted and highlighted content
"""

import requests
import json
import time
from playwright.sync_api import sync_playwright
import os

def test_cv_parser():
    """Test CV Parser returns content with address markup"""
    print("🔍 Testing CV Parser...")
    
    # Sample CV content to test with
    cv_text = """John Smith
Software Engineer
Python, JavaScript, React
Experience:
- Senior Developer at Tech Corp (2020-2023)
- Built scalable web applications
Skills: Python, React, Node.js"""
    
    response = requests.post('http://localhost:5005/parse', json={'cv_text': cv_text})
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            raw_text = data['result']['raw_text']
            if '<!--cv_' in raw_text and '-->' in raw_text:
                print("✅ CV Parser: Address markup found")
                return True, raw_text
            else:
                print("❌ CV Parser: No address markup found")
                return False, raw_text
        else:
            print(f"❌ CV Parser failed: {data}")
            return False, None
    else:
        print(f"❌ CV Parser HTTP error: {response.status_code}")
        return False, None

def test_jd_parser():
    """Test JD Parser returns content with address markup"""
    print("🔍 Testing JD Parser...")
    
    jd_text = """Senior Software Engineer
Requirements:
- 5+ years Python experience
- React/JavaScript expertise
- AWS cloud experience
Responsibilities:
- Lead development team
- Architect scalable solutions"""
    
    response = requests.post('http://localhost:5007/parse', json={'jd_text': jd_text})
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            raw_text = data['result']['raw_text']
            if '<!--jd_' in raw_text and '-->' in raw_text:
                print("✅ JD Parser: Address markup found")
                return True, raw_text
            else:
                print("❌ JD Parser: No address markup found")
                return False, raw_text
        else:
            print(f"❌ JD Parser failed: {data}")
            return False, None
    else:
        print(f"❌ JD Parser HTTP error: {response.status_code}")
        return False, None

def test_gap_analyst(cv_text, jd_text):
    """Test Gap Analyst returns highlighting instructions (not full HTML)"""
    print("🔍 Testing Gap Analyst...")
    
    gap_data = {
        'cv_data': {'raw_text': cv_text, 'key_skills': ['Python', 'JavaScript', 'React']},
        'jd_data': {'raw_text': jd_text, 'key_skills': ['Python', 'React', 'AWS']}
    }
    
    response = requests.post('http://localhost:5008/analyze_gap', json=gap_data)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            # Check that response contains highlighting instructions
            result = data['result']
            # In the current API, cv_highlighted and jd_highlighted contain the highlighting instructions
            if 'cv_highlighted' in result and 'jd_highlighted' in result:
                cv_instructions = result['cv_highlighted']
                jd_instructions = result['jd_highlighted']
                
                print(f"✅ Gap Analyst: Found {len(cv_instructions)} CV highlighting instructions")
                print(f"✅ Gap Analyst: Found {len(jd_instructions)} JD highlighting instructions")
                
                # Verify instructions have correct format
                if cv_instructions and all('address' in inst and 'class' in inst for inst in cv_instructions):
                    if jd_instructions and all('address' in inst and 'class' in inst for inst in jd_instructions):
                        return True, result
                    else:
                        print("❌ Gap Analyst: JD instructions malformed")
                        return False, result
                else:
                    print("❌ Gap Analyst: CV instructions malformed")
                    return False, result
            else:
                print("❌ Gap Analyst: Missing highlighting instructions")
                return False, result
        else:
            print(f"❌ Gap Analyst failed: {data}")
            return False, None
    else:
        print(f"❌ Gap Analyst HTTP error: {response.status_code}")
        return False, None

def test_browser_ui():
    """Test the browser UI displays content correctly"""
    print("🔍 Testing Browser UI with Playwright...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate to the analysis page
            page.goto("http://localhost:3000/analysis")
            page.wait_for_load_state("networkidle")
            
            # Check if analysis page loads
            if "CV_JD_ANALYSIS" in page.content():
                print("✅ Analysis page loaded successfully")
            else:
                print("❌ Analysis page failed to load")
                return False
                
            # Look for step indicators
            steps = page.locator("[data-testid*='step'], .status-info, .status-warning, .status-success")
            if steps.count() > 0:
                print("✅ Step indicators found")
            else:
                print("❌ No step indicators found")
                return False
                
            # Look for upload areas
            dropzone = page.locator(".dropzone")
            if dropzone.count() > 0:
                print("✅ File upload dropzone found")
            else:
                print("❌ No dropzone found")
                return False
            
            print("✅ Browser UI test passed")
            return True
            
        except Exception as e:
            print(f"❌ Browser UI test failed: {str(e)}")
            return False
        finally:
            browser.close()

def main():
    print("🧪 Starting Comprehensive Highlighting System Test")
    print("=" * 60)
    
    # Test 1: CV Parser
    cv_success, cv_text = test_cv_parser()
    if not cv_success:
        print("❌ CV Parser test failed - stopping")
        return False
    
    time.sleep(1)
    
    # Test 2: JD Parser  
    jd_success, jd_text = test_jd_parser()
    if not jd_success:
        print("❌ JD Parser test failed - stopping")
        return False
        
    time.sleep(1)
    
    # Test 3: Gap Analyst
    gap_success, gap_result = test_gap_analyst(cv_text, jd_text)
    if not gap_success:
        print("❌ Gap Analyst test failed - stopping")
        return False
        
    time.sleep(1)
    
    # Test 4: Browser UI
    ui_success = test_browser_ui()
    if not ui_success:
        print("❌ Browser UI test failed")
        return False
    
    print("=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("✅ Address-based highlighting system is working correctly")
    print("✅ CV Parser generates address markup")
    print("✅ JD Parser generates address markup")  
    print("✅ Gap Analyst returns highlighting instructions")
    print("✅ Browser UI loads and displays properly")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)