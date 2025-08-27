#!/usr/bin/env python3
"""
Test the REAL user flow including authentication
"""

from playwright.sync_api import sync_playwright
import time

def test_complete_user_flow():
    print("🌐 Testing COMPLETE user flow with authentication...")
    
    with sync_playwright() as p:
        # Launch visible browser
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        try:
            # Step 1: Go to main page and handle login
            print("🔐 Step 1: Handle authentication")
            page.goto("http://localhost:3000")
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # Check if we need to login
            if "LOGIN" in page.content() or "SYSTEM LOGIN" in page.content():
                print("🔑 Login required - creating account or logging in")
                
                # Try to create account first
                create_account = page.locator('button:has-text("CREATE_ACCOUNT"), a:has-text("CREATE_ACCOUNT")')
                if create_account.count() > 0:
                    create_account.first.click()
                    page.wait_for_timeout(2000)
                    
                    # Fill registration form
                    email_input = page.locator('input[type="email"], input[name="email"]')
                    password_input = page.locator('input[name="password"]')
                    confirm_password_input = page.locator('input[name="confirmPassword"]')
                    
                    if email_input.count() > 0:
                        email_input.fill("test@example.com")
                        if password_input.count() > 0:
                            password_input.fill("password123")
                        if confirm_password_input.count() > 0:
                            confirm_password_input.fill("password123")
                        
                        register_btn = page.locator('button:has-text("REGISTER"), button:has-text("CREATE")')
                        if register_btn.count() > 0:
                            register_btn.first.click()
                            page.wait_for_timeout(3000)
                
                # If still on login page, try to login
                if "LOGIN" in page.content():
                    email_input = page.locator('input[type="email"], input[placeholder*="email"]')
                    password_input = page.locator('input[type="password"]')
                    
                    if email_input.count() > 0:
                        email_input.fill("test@example.com")
                        password_input.fill("password123")
                        
                        login_btn = page.locator('button:has-text("LOGIN")')
                        if login_btn.count() > 0:
                            login_btn.first.click()
                            page.wait_for_timeout(3000)
            
            # Step 2: Navigate to analysis page
            print("📍 Step 2: Navigate to analysis")
            page.goto("http://localhost:3000/analysis")
            page.wait_for_load_state("networkidle", timeout=10000)
            page.screenshot(path="real_step1_analysis_page.png")
            
            if "CV_JD_ANALYSIS" not in page.content():
                print("❌ Still not on analysis page, trying different routes...")
                # Try different possible routes
                possible_routes = ["/", "/dashboard", "/analyze"]
                for route in possible_routes:
                    page.goto(f"http://localhost:3000{route}")
                    page.wait_for_timeout(2000)
                    if "upload" in page.content().lower() or "cv" in page.content().lower():
                        print(f"✅ Found analysis interface at {route}")
                        break
                else:
                    print("❌ Cannot find analysis interface")
                    page.screenshot(path="real_error_no_analysis.png")
                    print("🔍 Current page content preview:")
                    print(page.content()[:500] + "...")
                    browser.close()
                    return False
            
            # Step 3: Look for actual CV upload
            print("📄 Step 3: Looking for CV upload mechanism")
            page.screenshot(path="real_step2_looking_for_upload.png")
            
            # Try to find upload elements - react-dropzone creates hidden input
            file_inputs = page.locator('input[type="file"]')
            dropzones = page.locator('.dropzone')
            upload_areas = page.locator('[class*="dropzone"], [class*="drag"], div:has(input[type="file"])')
            
            print(f"🔍 Found {file_inputs.count()} file inputs")
            print(f"🔍 Found {dropzones.count()} dropzones") 
            print(f"🔍 Found {upload_areas.count()} upload areas")
            
            if file_inputs.count() == 0 and dropzones.count() == 0 and upload_areas.count() == 0:
                print("❌ NO UPLOAD MECHANISM FOUND")
                print("🔍 Searching for STEP_1 content...")
                step1_content = page.locator('text="[STEP_1]"')
                if step1_content.count() > 0:
                    print("✅ Found STEP_1 content - upload area should be nearby")
                    # Look for any clickable area near step 1
                    upload_areas = page.locator('div:near(:text("[STEP_1]"))')
                    print(f"🔍 Found {upload_areas.count()} areas near STEP_1")
                    if upload_areas.count() > 0:
                        dropzones = upload_areas
                else:
                    print("❌ NO STEP_1 CONTENT FOUND")
                    print("🔍 Page content preview:")
                    print(page.content()[:1000])
                    browser.close()
                    return False
                
            # Step 4: Actually perform upload if possible
            print("📤 Step 4: Attempting upload")
            
            # Create test files
            cv_content = """John Smith
Software Engineer
john@email.com

EXPERIENCE:
Senior Developer at TechCorp (2020-2023)
- Built Python applications
- React frontend development  
- AWS cloud deployment

SKILLS:
Python, JavaScript, React, AWS"""
            
            # Save test CV
            with open("/tmp/test_cv.txt", "w") as f:
                f.write(cv_content)
            
            # Try different upload approaches
            if file_inputs.count() > 0:
                print("📤 Using direct file input")
                file_inputs.first.set_input_files("/tmp/test_cv.txt")
                print("✅ File uploaded via input")
            elif dropzones.count() > 0:
                print("📤 Using dropzone click method")
                # For react-dropzone, we need to find the hidden file input within the dropzone
                hidden_input = dropzones.first.locator('input[type="file"]')
                if hidden_input.count() > 0:
                    hidden_input.set_input_files("/tmp/test_cv.txt")
                    print("✅ File uploaded via dropzone hidden input")
                else:
                    # Click dropzone to trigger file dialog (may not work in headless mode)
                    dropzones.first.click()
                    page.wait_for_timeout(1000)
                    print("⚠️ Clicked dropzone (file dialog may not work in automated testing)")
            else:
                print("❌ No suitable upload method found")
                
            page.wait_for_timeout(5000)  # Wait for processing
            page.screenshot(path="real_step3_after_cv_upload.png")
            
            # Step 5: Add job description
            print("📋 Step 5: Adding job description")
            
            jd_content = """Senior Software Engineer
Requirements:
- 5+ years Python experience
- React/JavaScript skills  
- AWS cloud knowledge
- Team leadership"""
            
            textareas = page.locator('textarea')
            text_inputs = page.locator('input[type="text"]:not([type="file"])')
            
            if textareas.count() > 0:
                textareas.first.fill(jd_content)
                print("✅ JD entered in textarea")
            elif text_inputs.count() > 0:
                text_inputs.first.fill(jd_content)
                print("✅ JD entered in text input")
                
            page.wait_for_timeout(2000)
            page.screenshot(path="real_step4_jd_entered.png")
            
            # Step 6: Process/Submit
            print("⚡ Step 6: Processing submission")
            
            submit_buttons = page.locator('button:has-text("PROCESS"), button:has-text("ANALYZE"), button:has-text("START"), button:has-text("▶")')
            if submit_buttons.count() > 0:
                print(f"🔍 Found {submit_buttons.count()} potential submit buttons")
                submit_buttons.first.click()
                print("✅ Submit button clicked")
            
            # Wait for processing and analysis
            print("⏳ Waiting for analysis to complete...")
            page.wait_for_timeout(20000)  # Wait longer for full analysis
            
            # Step 7: Take final screenshot and analyze results
            page.screenshot(path="real_final_results.png")
            print("📸 Final screenshot taken: real_final_results.png")
            
            # Analyze what's actually displayed
            print("🔍 Step 7: Analyzing ACTUAL results displayed...")
            
            final_content = page.content()
            
            # Check for highlighting issues
            highlight_matches = final_content.count('class="highlight-match"')
            highlight_potentials = final_content.count('class="highlight-potential"') 
            highlight_gaps = final_content.count('class="highlight-gap"')
            
            print(f"🟢 Green highlights (match): {highlight_matches}")
            print(f"🟡 Yellow highlights (potential): {highlight_potentials}")
            print(f"🔴 Red highlights (gap): {highlight_gaps}")
            
            total_highlights = highlight_matches + highlight_potentials + highlight_gaps
            
            if total_highlights == 0:
                print("❌ NO HIGHLIGHTING FOUND AT ALL")
            elif highlight_potentials == 0 and highlight_gaps == 0 and highlight_matches > 0:
                print("❌ CONFIRMED: Only green highlighting - all text appears green")
            else:
                print("✅ Mixed highlighting found")
                
            # Check formatting issues
            if '<pre class=' not in final_content and '.cv-content' not in final_content:
                print("❌ NO PROPER CONTENT FORMATTING")
            else:
                print("✅ Content formatting found")
                
            # Save full HTML for inspection
            with open("real_final_page.html", "w") as f:
                f.write(final_content)
            print("💾 Full page HTML saved: real_final_page.html")
            
            # Look for specific broken formatting
            if final_content.count('<pre') > 10:
                print("⚠️  Many <pre> tags found - possible formatting issues")
                
            if 'style="display: grid"' in final_content and '<pre' in final_content:
                print("⚠️  Grid layout with <pre> tags - likely causing layout issues")
            
            print("\n📋 KEEPING BROWSER OPEN FOR MANUAL INSPECTION")
            print("Please manually check the browser window and press Enter when done...")
            input("Press Enter to close browser...")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            page.screenshot(path="real_error_final.png")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    test_complete_user_flow()