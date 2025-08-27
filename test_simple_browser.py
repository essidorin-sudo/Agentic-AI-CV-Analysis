#!/usr/bin/env python3
"""
Simple browser test to verify what the user actually sees
Focus only on testing the highlighting and formatting issues
"""

from playwright.sync_api import sync_playwright
import time

def test_simple_user_experience():
    print("🌐 Testing user experience with simple login...")
    
    with sync_playwright() as p:
        # Launch visible browser
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
        
        try:
            # Step 1: Go to main page
            print("🔐 Step 1: Accessing application")
            page.goto("http://localhost:3000")
            page.wait_for_load_state("networkidle", timeout=10000)
            page.screenshot(path="simple_step1_initial.png")
            
            # Step 2: Try to login with existing account (not create new)
            print("🔑 Step 2: Login with existing credentials")
            
            # Look for login form (not create account)
            login_form = page.locator('form, div:has(input[type="email"])')
            if login_form.count() > 0:
                # Fill login credentials
                email_field = page.locator('input[type="email"]')
                password_field = page.locator('input[type="password"]').first  # Use first password field for login
                
                if email_field.count() > 0:
                    email_field.fill("test@example.com")
                    password_field.fill("password123")
                    
                    # Look for LOGIN button (not register)
                    login_btn = page.locator('button:has-text("LOGIN"), button:has-text("Log in"), button:has-text("Sign in")')
                    if login_btn.count() > 0:
                        login_btn.first.click()
                        print("✅ Login attempted")
                        page.wait_for_timeout(3000)
                    else:
                        print("⚠️ No login button found, will try alternative")
                        # Try pressing Enter
                        password_field.press("Enter")
                        page.wait_for_timeout(3000)
            
            # Step 3: Navigate to analysis regardless of login success
            print("📍 Step 3: Go to analysis page")
            page.goto("http://localhost:3000/analysis")
            page.wait_for_timeout(5000)  # Give more time for React to load
            page.screenshot(path="simple_step2_analysis.png")
            
            # Step 4: Look for the actual page content
            print("🔍 Step 4: Check if analysis page loaded")
            
            # Wait for React content to appear
            try:
                page.wait_for_selector('[class*="terminal"], [class*="panel"], .dropzone', timeout=10000)
                print("✅ React content detected")
            except:
                print("⚠️ React content may not have loaded, continuing...")
            
            page_content = page.content()
            
            # Check for key elements
            has_cv_upload = "STEP_1" in page_content or "CV_UPLOAD" in page_content or "dropzone" in page_content
            has_step_content = "[STEP_" in page_content or "UPLOAD_CV" in page_content
            
            print(f"📊 Page analysis:")
            print(f"  • Has CV upload elements: {has_cv_upload}")
            print(f"  • Has step content: {has_step_content}")
            print(f"  • Page content length: {len(page_content)}")
            
            # If we found the upload interface, try to use it
            if has_cv_upload or has_step_content:
                print("✅ Found upload interface, proceeding with test...")
                
                # Step 5: Upload CV
                print("📄 Step 5: Upload CV")
                
                # Create test file
                cv_content = """John Smith
Software Engineer
john@email.com

EXPERIENCE:
Senior Developer at TechCorp (2020-2023)
- Built Python applications
- React development
- AWS deployment

SKILLS:
Python, JavaScript, React, AWS"""
                
                with open("/tmp/test_cv.txt", "w") as f:
                    f.write(cv_content)
                
                # Look for file input (hidden or visible)
                file_input = page.locator('input[type="file"]')
                if file_input.count() > 0:
                    print("📤 Found file input, uploading...")
                    file_input.first.set_input_files("/tmp/test_cv.txt")
                    page.wait_for_timeout(8000)  # Wait for processing
                    page.screenshot(path="simple_step3_cv_uploaded.png")
                    print("✅ CV uploaded")
                    
                    # Step 6: Add job description
                    print("📋 Step 6: Add job description")
                    
                    # Wait for next step or look for JD input
                    page.wait_for_timeout(2000)
                    
                    jd_content = """Senior Software Engineer
Requirements:
- 5+ years Python
- React/JavaScript
- AWS cloud knowledge"""
                    
                    # Look for textarea
                    textarea = page.locator('textarea')
                    if textarea.count() > 0:
                        textarea.fill(jd_content)
                        print("✅ JD entered")
                        
                        # Look for process button
                        process_btn = page.locator('button:has-text("PROCESS"), button:has-text("▶")')
                        if process_btn.count() > 0:
                            process_btn.first.click()
                            print("✅ JD processing initiated")
                            page.wait_for_timeout(5000)
                            
                            # Step 7: Start analysis
                            print("⚡ Step 7: Start analysis")
                            
                            analysis_btn = page.locator('button:has-text("ANALYSIS"), button:has-text("START")')
                            if analysis_btn.count() > 0:
                                analysis_btn.first.click()
                                print("✅ Analysis started")
                                
                                # Wait for results
                                print("⏳ Waiting for analysis results...")
                                page.wait_for_timeout(25000)  # Wait longer for analysis
                                
                                # Step 8: Check final results
                                print("🔍 Step 8: Examining final results")
                                page.screenshot(path="simple_final_results.png")
                                
                                final_content = page.content()
                                
                                # Check for highlighting
                                highlight_matches = final_content.count('class="highlight-match"')
                                highlight_potentials = final_content.count('class="highlight-potential"')
                                highlight_gaps = final_content.count('class="highlight-gap"')
                                
                                print(f"🎨 Highlighting analysis:")
                                print(f"  • Green highlights: {highlight_matches}")
                                print(f"  • Yellow highlights: {highlight_potentials}")
                                print(f"  • Red highlights: {highlight_gaps}")
                                
                                total_highlights = highlight_matches + highlight_potentials + highlight_gaps
                                
                                if total_highlights == 0:
                                    print("❌ NO HIGHLIGHTING FOUND")
                                elif highlight_potentials == 0 and highlight_gaps == 0:
                                    print("❌ CONFIRMED: Only green highlighting (user's issue)")
                                else:
                                    print("✅ Mixed highlighting found")
                                
                                # Check for formatting issues
                                if '<pre' in final_content and 'grid' in final_content:
                                    print("⚠️ Potential grid+pre formatting conflict")
                                
                                # Save full results
                                with open("simple_final_results.html", "w") as f:
                                    f.write(final_content)
                                print("💾 Full results saved: simple_final_results.html")
                                
                            else:
                                print("❌ No analysis button found")
                        else:
                            print("❌ No JD process button found")
                    else:
                        print("❌ No textarea found for JD")
                        
                else:
                    print("❌ No file input found")
            else:
                print("❌ Upload interface not detected")
                
            print("\\n🔍 MANUAL INSPECTION TIME")
            print("Check the browser window to see what the user actually experiences")
            input("Press Enter when you're done inspecting...")
            
        except Exception as e:
            print(f"❌ Test error: {e}")
            page.screenshot(path="simple_error.png")
            
        finally:
            browser.close()

if __name__ == "__main__":
    test_simple_user_experience()