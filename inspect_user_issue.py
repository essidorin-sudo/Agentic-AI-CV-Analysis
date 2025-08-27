#!/usr/bin/env python3
"""
Inspect the exact user issue: formatting and all-green highlighting
Focus only on what the user actually experiences in the frontend
"""

from playwright.sync_api import sync_playwright
import time

def inspect_user_issue():
    print("🔍 INSPECTING USER'S EXACT ISSUES")
    print("Issue 1: Formatting not preserved")  
    print("Issue 2: All JD text highlighted green")
    print("="*50)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        try:
            # Go directly to the production site
            print("🌐 Accessing production site...")
            page.goto("http://localhost:3000")
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # Try simple login
            try:
                email_field = page.locator('input[type="email"]')
                password_field = page.locator('input[name="password"]').first
                
                if email_field.count() > 0:
                    email_field.fill("test@example.com")
                    password_field.fill("password123")
                    
                    login_btn = page.locator('button:has-text("LOGIN")')
                    if login_btn.count() > 0:
                        login_btn.click()
                        page.wait_for_timeout(3000)
            except:
                pass
            
            # Navigate to analysis
            print("📍 Going to analysis page...")
            page.goto("http://localhost:3000/analysis")
            page.wait_for_timeout(5000)
            
            # Look for upload mechanism
            page.screenshot(path="user_issue_step1.png")
            
            # Upload a simple CV
            print("📄 Uploading CV...")
            cv_content = """John Smith
Software Engineer
john@email.com

EXPERIENCE:
Senior Developer at TechCorp (2020-2023)
- Python web development
- React frontend applications  
- AWS cloud deployment

SKILLS:
Python, JavaScript, React, AWS"""

            with open("/tmp/simple_cv.txt", "w") as f:
                f.write(cv_content)
            
            file_input = page.locator('input[type="file"]')
            if file_input.count() > 0:
                file_input.set_input_files("/tmp/simple_cv.txt")
                page.wait_for_timeout(8000)
                print("✅ CV uploaded")
                
                # Add JD
                print("📋 Adding job description...")
                jd_content = """Senior Software Engineer
Requirements:
- 5+ years Python experience
- React/JavaScript skills
- AWS cloud knowledge
- Leadership experience"""
                
                textarea = page.locator('textarea')
                if textarea.count() > 0:
                    textarea.fill(jd_content)
                    
                    # Process JD
                    process_btn = page.locator('button:has-text("PROCESS")')
                    if process_btn.count() > 0:
                        process_btn.click()
                        page.wait_for_timeout(5000)
                        print("✅ JD processed")
                        
                        # Start analysis
                        print("⚡ Starting analysis...")
                        analysis_btn = page.locator('button:has-text("ANALYSIS"), button:has-text("START")')
                        if analysis_btn.count() > 0:
                            analysis_btn.click()
                            page.wait_for_timeout(25000)
                            
                            # Capture the final result
                            print("📸 Capturing user's actual experience...")
                            page.screenshot(path="user_issue_final_result.png")
                            
                            # Get the actual HTML content
                            final_content = page.content()
                            
                            # Save for inspection
                            with open("user_actual_experience.html", "w") as f:
                                f.write(final_content)
                            
                            # Analyze the issues
                            print("🔍 ANALYZING USER'S ISSUES:")
                            
                            # Issue 1: Formatting preservation
                            print("\n📐 Issue 1 - FORMATTING:")
                            pre_tags = final_content.count('<pre')
                            div_tags_with_cv = final_content.count('<div class="cv-content"')
                            
                            print(f"   • <pre> tags found: {pre_tags}")
                            print(f"   • <div class='cv-content'> tags: {div_tags_with_cv}")
                            
                            if '<pre' in final_content and 'display: grid' in final_content:
                                print("   ❌ FORMATTING ISSUE CONFIRMED: <pre> tags in grid layout")
                            
                            # Issue 2: All green highlighting
                            print("\n🎨 Issue 2 - HIGHLIGHTING:")
                            jd_green = final_content.count('highlight-match')
                            jd_yellow = final_content.count('highlight-potential') 
                            jd_red = final_content.count('highlight-gap')
                            
                            print(f"   • Green highlights: {jd_green}")
                            print(f"   • Yellow highlights: {jd_yellow}")
                            print(f"   • Red highlights: {jd_red}")
                            
                            if jd_yellow == 0 and jd_red == 0 and jd_green > 0:
                                print("   ❌ ALL GREEN ISSUE CONFIRMED")
                            elif jd_green == 0 and jd_yellow == 0 and jd_red == 0:
                                print("   ❌ NO HIGHLIGHTING ISSUE")
                            else:
                                print("   ✅ Mixed highlighting detected")
                            
                            # Show specific sections with issues
                            print("\n🔍 SPECIFIC ISSUES TO FIX:")
                            if '<pre' in final_content and 'display: grid' in final_content:
                                print("   • Replace <pre> with <div> in highlighted content")
                                print("   • Fix CSS grid compatibility")
                            
                            if jd_yellow == 0 and jd_red == 0:
                                print("   • Gap Analyst generating only 'match' classifications")
                                print("   • Need to check Gap Analyst prompt or logic")
                            
                            print(f"\n💾 Files saved:")
                            print(f"   • user_issue_final_result.png - Screenshot")
                            print(f"   • user_actual_experience.html - Full page HTML")
                            
                            print("\n⏳ Keeping browser open for manual inspection...")
                            input("Press Enter to close browser and fix issues...")
                            
        except Exception as e:
            print(f"❌ Error: {e}")
            page.screenshot(path="user_issue_error.png")
            
        finally:
            browser.close()

if __name__ == "__main__":
    inspect_user_issue()