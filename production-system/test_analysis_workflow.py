#!/usr/bin/env python3

import asyncio
import os
import tempfile
from playwright.async_api import async_playwright
import requests
import time

async def test_analysis_workflow():
    """
    Automated test of the complete CV-JD analysis workflow using Playwright
    """
    print("🚀 Starting automated CV analysis workflow test...")
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Step 1: Navigate to the application
            print("📄 Navigating to application...")
            await page.goto('http://localhost:3000')
            await page.wait_for_load_state('networkidle')
            
            # Step 2: Login as admin
            print("🔐 Logging in as admin...")
            await page.fill('input[type="email"]', 'admin@cvanalyzer.com')
            await page.fill('input[type="password"]', 'admin123')
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            # Step 3: Navigate to Analysis page
            print("📊 Navigating to Analysis page...")
            await page.click('text=ANALYSIS')
            await page.wait_for_load_state('networkidle')
            
            # Step 4: Create a test CV file
            print("📄 Creating test CV file...")
            test_cv_content = """
Eugene Sidorins
Senior Software Engineer

Email: eugene.sidorins@gmail.com
Phone: +371 26 548 778
Location: Riga, Latvia

PROFESSIONAL SUMMARY
Experienced software engineer with 10+ years in full-stack development.
Specializing in JavaScript, Python, React, and Node.js.

WORK EXPERIENCE
Senior Software Engineer | Accenture Latvia | 2019 - Present
- Lead development of enterprise React applications
- Implemented microservices using Node.js and Express
- Mentored junior developers and conducted code reviews

Software Developer | Tieto Latvia | 2016 - 2019  
- Developed web applications using JavaScript and Python
- Worked with PostgreSQL and MongoDB databases
- Implemented REST APIs and automated testing

EDUCATION
Master's Degree in Computer Science | University of Latvia | 2016
Bachelor's Degree in Computer Engineering | Riga Technical University | 2014

SKILLS
JavaScript, TypeScript, Python, React, Node.js, Express, PostgreSQL, MongoDB, AWS, Docker, Git
"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(test_cv_content)
                cv_file_path = f.name
            
            # Step 5: Upload CV
            print("📤 Uploading CV file...")
            await page.set_input_files('input[type="file"]', cv_file_path)
            await page.wait_for_timeout(3000)  # Wait for CV processing
            
            # Wait for CV upload to complete and JD step to become available
            await page.wait_for_selector('[data-testid="jd-input"], textarea, input[type="url"]', timeout=30000)
            print("✅ CV upload completed, JD input now available")
            
            # Step 6: Add job description
            print("📝 Adding job description...")
            jd_text = """
VP, Data & Analytics Position

We are seeking a VP of Data & Analytics to lead our data strategy and analytics initiatives.

Requirements:
- 10+ years of experience in data analytics and management
- Strong skills in Python, SQL, and machine learning
- Experience with cloud platforms (AWS, Azure, GCP)
- Leadership experience managing analytics teams
- Advanced degree in Computer Science, Statistics, or related field

Responsibilities:
- Lead data strategy and analytics for the organization
- Manage a team of data scientists and analysts
- Implement machine learning models and data pipelines
- Collaborate with executive team on data-driven decisions
- Ensure data governance and quality standards

Skills:
Python, SQL, Machine Learning, AWS, Tableau, Apache Spark, Leadership
"""
            
            # Try to find textarea or text input for JD
            jd_input = await page.query_selector('textarea')
            if jd_input:
                await jd_input.fill(jd_text)
                print("📝 Job description added via textarea")
            else:
                # Try URL input if text input not found
                url_input = await page.query_selector('input[type="url"]')
                if url_input:
                    await page.click('button:has-text("[TEXT]")')  # Switch to text mode
                    await page.wait_for_timeout(1000)
                    textarea = await page.query_selector('textarea')
                    if textarea:
                        await textarea.fill(jd_text)
                        print("📝 Job description added via textarea after switching to text mode")
            
            # Click process JD button
            process_jd_button = await page.query_selector('button:has-text("PROCESS"), button:has-text("ANALYZE")')
            if process_jd_button:
                await process_jd_button.click()
                print("🔄 Processing job description...")
                await page.wait_for_timeout(5000)  # Wait for JD processing
            
            # Step 7: Run analysis
            print("🔬 Running analysis...")
            analysis_button = await page.query_selector('button:has-text("START_ANALYSIS"), button:has-text("ANALYZE")')
            if analysis_button:
                await analysis_button.click()
                print("🔄 Analysis started...")
                
                # Wait for analysis to complete (up to 60 seconds)
                await page.wait_for_timeout(60000)
                
                # Step 8: Check results
                print("📊 Checking analysis results...")
                
                # Look for match scores
                match_score = await page.query_selector('text=/\d+%/')
                if match_score:
                    score_text = await match_score.text_content()
                    print(f"✅ Found match score: {score_text}")
                else:
                    print("❌ No match score found")
                
                # Look for recommendations
                recommendations = await page.query_selector('text=/RECOMMENDATIONS|recommendations/')
                if recommendations:
                    print("✅ Found recommendations section")
                else:
                    print("❌ No recommendations found")
                
                # Look for highlighted content
                highlighted = await page.query_selector('text=/CV_ANALYSIS|JOB_DESCRIPTION_ANALYSIS/')
                if highlighted:
                    print("✅ Found highlighted content sections")
                else:
                    print("❌ No highlighted content found")
                
                # Take a screenshot of the results
                await page.screenshot(path='analysis_results.png')
                print("📸 Screenshot saved as analysis_results.png")
                
            else:
                print("❌ Analysis button not found")
            
            print("🏁 Test completed!")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            
            # Take error screenshot
            await page.screenshot(path='error_screenshot.png')
            print("📸 Error screenshot saved as error_screenshot.png")
            
        finally:
            # Cleanup
            if 'cv_file_path' in locals():
                os.unlink(cv_file_path)
            await browser.close()

async def check_backend_logs():
    """Check backend logs for any errors"""
    print("📋 Checking backend logs...")
    try:
        # You could implement log checking here if needed
        pass
    except Exception as e:
        print(f"⚠️ Could not check logs: {e}")

if __name__ == "__main__":
    print("🧪 Starting automated analysis workflow test...")
    print("📋 Make sure the frontend (localhost:3000) and backend (localhost:8000) are running")
    
    # Run the test
    asyncio.run(test_analysis_workflow())