#!/usr/bin/env python3
"""
Test what the user actually sees in the browser - not just API endpoints
"""

from playwright.sync_api import sync_playwright
import time
import os

def test_actual_user_experience():
    print("🌐 Testing ACTUAL user experience in browser...")
    
    with sync_playwright() as p:
        # Launch browser with visible UI so we can see what's happening
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
        
        try:
            # Step 1: Go to analysis page
            print("📍 Step 1: Navigate to analysis page")
            page.goto("http://localhost:3000/analysis")
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # Take screenshot of initial state
            page.screenshot(path="step1_initial.png")
            print("📸 Screenshot saved: step1_initial.png")
            
            # Step 2: Upload CV
            print("📄 Step 2: Upload CV file")
            
            # Create a test CV file
            cv_content = """John Smith
Software Engineer
john.smith@email.com
(555) 123-4567

EXPERIENCE
Senior Software Engineer | Tech Corp | 2020-2023
• Developed Python applications
• Built React frontends
• Worked with AWS cloud

Junior Developer | StartupCo | 2018-2020
• JavaScript development
• Docker containers

SKILLS
• Python, JavaScript, React
• AWS, Docker, PostgreSQL"""
            
            # Save to temp file
            cv_file_path = "/tmp/test_cv.txt"
            with open(cv_file_path, "w") as f:
                f.write(cv_content)
            
            # Find and interact with file upload
            try:
                file_input = page.locator('input[type="file"]')
                if file_input.count() > 0:
                    file_input.set_input_files(cv_file_path)
                    print("✅ CV file uploaded")
                else:
                    print("❌ No file input found - trying dropzone")
                    dropzone = page.locator('.dropzone')
                    if dropzone.count() > 0:
                        # For dropzone, we need to trigger the file input
                        page.evaluate(f"""
                            const input = document.querySelector('input[type="file"]');
                            if (input) {{
                                const dt = new DataTransfer();
                                const file = new File(['{cv_content}'], 'test_cv.txt', {{ type: 'text/plain' }});
                                dt.items.add(file);
                                input.files = dt.files;
                                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            }}
                        """)
                        print("✅ CV uploaded via dropzone")
                    else:
                        print("❌ No upload mechanism found")
                        browser.close()
                        return False
            except Exception as e:
                print(f"❌ Error uploading CV: {e}")
            
            # Wait for CV processing
            print("⏳ Waiting for CV processing...")
            page.wait_for_timeout(5000)
            page.screenshot(path="step2_cv_uploaded.png")
            print("📸 Screenshot saved: step2_cv_uploaded.png")
            
            # Step 3: Add Job Description
            print("📋 Step 3: Add job description")
            
            jd_content = """Senior Software Engineer
Requirements:
• 5+ years Python experience  
• React/JavaScript expertise
• AWS cloud experience
• Strong communication skills

Responsibilities:
• Lead development team
• Architect solutions
• Deploy on cloud"""
            
            try:
                # Look for job description textarea
                jd_textarea = page.locator('textarea')
                if jd_textarea.count() > 0:
                    jd_textarea.fill(jd_content)
                    print("✅ Job description entered")
                else:
                    print("❌ No textarea found for JD")
                    
                # Look for submit button
                submit_buttons = page.locator('button:has-text("PROCESS"), button:has-text("Process"), button:has-text("▶")')
                if submit_buttons.count() > 0:
                    submit_buttons.first.click()
                    print("✅ Submit button clicked")
                else:
                    print("❌ No submit button found")
                    
            except Exception as e:
                print(f"❌ Error with JD: {e}")
            
            # Wait for JD processing
            print("⏳ Waiting for JD processing...")
            page.wait_for_timeout(5000)
            page.screenshot(path="step3_jd_added.png")
            print("📸 Screenshot saved: step3_jd_added.png")
            
            # Step 4: Run Analysis
            print("🔍 Step 4: Run analysis")
            
            try:
                analyze_buttons = page.locator('button:has-text("ANALYZE"), button:has-text("Analyze"), button:has-text("START_ANALYSIS")')
                if analyze_buttons.count() > 0:
                    analyze_buttons.first.click()
                    print("✅ Analysis button clicked")
                else:
                    print("❌ No analysis button found")
                    
            except Exception as e:
                print(f"❌ Error starting analysis: {e}")
            
            # Wait for analysis to complete
            print("⏳ Waiting for analysis to complete...")
            page.wait_for_timeout(15000)  # Wait longer for analysis
            
            # Take final screenshot
            page.screenshot(path="step4_analysis_complete.png")
            print("📸 Screenshot saved: step4_analysis_complete.png")
            
            # Step 5: Examine actual results
            print("🔍 Step 5: Examining actual results on page...")
            
            # Look for highlighted content
            highlighted_elements = page.locator('.highlight-match, .highlight-potential, .highlight-gap')
            highlighted_count = highlighted_elements.count()
            print(f"🎨 Found {highlighted_count} highlighted elements")
            
            # Look for analysis scores
            score_elements = page.locator(':text-matches("\\d+%")')
            score_count = score_elements.count() 
            print(f"📊 Found {score_count} score elements")
            
            # Look for side-by-side content
            cv_content_elements = page.locator('.panel-content:has(.cv-content), [class*="cv"], [class*="CV"]')
            jd_content_elements = page.locator('.panel-content:has(.jd-content), [class*="jd"], [class*="JD"]')
            print(f"📄 Found {cv_content_elements.count()} CV content areas")
            print(f"📋 Found {jd_content_elements.count()} JD content areas")
            
            # Get page content to analyze
            page_content = page.content()
            
            # Look for specific issues
            if "highlight-match" not in page_content:
                print("❌ NO highlight-match class found in page")
            else:
                print("✅ highlight-match class found in page")
                
            if "pre class=" not in page_content and "cv-content" not in page_content:
                print("❌ NO CV content formatting found")
            else:
                print("✅ CV content formatting found")
                
            # Look for the "all green" issue
            green_elements = page.locator('.highlight-match')
            green_count = green_elements.count()
            total_highlighted = page.locator('[class*="highlight"]').count()
            
            print(f"🟢 Green highlighted elements: {green_count}")
            print(f"🎨 Total highlighted elements: {total_highlighted}")
            
            if green_count == total_highlighted and total_highlighted > 5:
                print("❌ ISSUE CONFIRMED: All text appears to be highlighted green")
            else:
                print("✅ Highlighting appears varied")
            
            # Save final page state
            with open("final_page_content.html", "w") as f:
                f.write(page_content)
            print("💾 Full page content saved to final_page_content.html")
            
            # Keep browser open for manual inspection
            print("\n🔍 BROWSER KEPT OPEN FOR MANUAL INSPECTION")
            print("Check the screenshots and final_page_content.html")
            print("Press Enter to close browser...")
            input()
            
            return True
            
        except Exception as e:
            print(f"❌ Browser test failed: {e}")
            page.screenshot(path="error_screenshot.png")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    test_actual_user_experience()