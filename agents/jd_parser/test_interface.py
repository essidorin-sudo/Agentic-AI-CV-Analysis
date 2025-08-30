#!/usr/bin/env python3
"""
JD Parser Agent - Testing Interface

Simple web interface for testing the JD Parser Agent with different
job descriptions and comparing results between different configurations.
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from agent import JDParserAgent
import traceback
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import time
import platform

# Selenium imports for JavaScript-heavy sites
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
    print("✅ Selenium WebDriver available for JavaScript rendering")
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not available - JavaScript-heavy sites may not work properly")

# requests-html for easier JavaScript rendering
try:
    from requests_html import HTMLSession
    REQUESTS_HTML_AVAILABLE = True
    print("✅ requests-html available for JavaScript rendering")
except ImportError:
    REQUESTS_HTML_AVAILABLE = False
    print("⚠️  requests-html not available")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global agent instance
jd_agent = JDParserAgent()

# Sample job descriptions for testing
SAMPLE_JDS = {
    "tech_senior": """Senior Software Engineer - Full Stack
TechCorp Solutions

Join our innovative team as a Senior Software Engineer where you'll build scalable web applications and lead technical initiatives.

Key Responsibilities:
• Design and develop full-stack web applications using React and Node.js
• Lead code reviews and mentor junior developers
• Collaborate with product managers and designers
• Implement CI/CD pipelines and automated testing

Required Qualifications:
• Bachelor's degree in Computer Science or related field
• 5+ years of software development experience
• Proficiency in JavaScript, Python, and SQL
• Experience with React, Node.js, and cloud platforms (AWS/Azure)
• Strong communication and leadership skills

Preferred Qualifications:
• Master's degree in Computer Science
• Experience with Docker and Kubernetes
• Previous startup experience
• Open source contributions

We offer competitive salary ($120k-160k), comprehensive health benefits, equity package, and flexible remote work options.

TechCorp is a fast-growing startup focused on AI-powered business solutions.""",

    "finance_analyst": """Financial Analyst
Global Finance Corp

We are seeking a detail-oriented Financial Analyst to join our corporate finance team and support strategic decision-making.

About the Role:
The Financial Analyst will be responsible for financial modeling, variance analysis, and preparing executive reports. You will work closely with senior management to provide insights that drive business growth.

Essential Requirements:
• Bachelor's degree in Finance, Economics, or Accounting
• 3-5 years of experience in financial analysis
• Advanced Excel skills and financial modeling expertise
• Experience with SQL and data analysis tools
• Strong analytical and problem-solving abilities
• Excellent written and verbal communication skills

Nice to Have:
• CFA certification or progress toward CFA
• Experience with Tableau or Power BI
• Knowledge of Python or R for data analysis
• Previous experience in investment banking or consulting

Benefits package includes health insurance, 401(k) matching, three weeks vacation, and professional development opportunities.

Global Finance Corp has been a leader in corporate finance for over 20 years, serving Fortune 500 companies worldwide.""",

    "marketing_manager": """Marketing Manager - Digital Growth
InnovateBrand Agency

Drive digital marketing initiatives and lead our growing marketing team in this exciting opportunity.

What You'll Do:
- Develop and execute comprehensive digital marketing strategies
- Manage social media campaigns across multiple platforms  
- Lead a team of 3-5 marketing specialists
- Analyze campaign performance and optimize for ROI
- Collaborate with sales teams to generate qualified leads

Must Have:
- Bachelor's degree in Marketing or Business
- 4+ years digital marketing experience
- Proven track record with Google Ads and Facebook advertising
- Team leadership experience
- Strong analytical skills and data-driven mindset

Preferred:
- MBA or advanced marketing certification
- Experience with marketing automation tools (HubSpot, Marketo)
- B2B SaaS marketing background
- Creative design skills

Join our team and enjoy competitive compensation, unlimited PTO, health benefits, and a creative work environment."""
}


@app.route('/')
def index():
    """Main testing interface"""
    return render_template('test_interface.html', sample_jds=SAMPLE_JDS)


@app.route('/get_current_prompt', methods=['GET'])
def get_current_prompt():
    """Get the current parsing prompt"""
    try:
        return jsonify({
            'success': True,
            'prompt': jd_agent.get_prompt(),
            'prompt_id': 'default',
            'prompt_name': 'Default Parsing Prompt'
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/update_prompt', methods=['POST'])
def update_prompt():
    """Update the parsing prompt"""
    try:
        data = request.get_json()
        new_prompt = data.get('prompt', '').strip()
        
        if not new_prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        # Update the agent's prompt
        jd_agent.update_prompt(new_prompt)
        
        return jsonify({
            'success': True,
            'message': 'Prompt updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/set_default_prompt', methods=['POST'])
def set_default_prompt():
    """Set a prompt as the new default"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        # Save as default prompt
        success = jd_agent.save_as_default_prompt(prompt)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Prompt saved as new default successfully'
            })
        else:
            return jsonify({
                'error': 'Failed to save prompt as default'
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/parse_with_prompt', methods=['POST'])
def parse_with_prompt():
    """Parse job description with a specific prompt"""
    try:
        data = request.get_json()
        jd_text = data.get('jd_text', '').strip()
        jd_url = data.get('jd_url', '').strip()
        custom_prompt = data.get('prompt', '').strip()
        
        # If URL is provided, fetch content from the web
        if jd_url:
            try:
                jd_text = fetch_job_description_from_url(jd_url)
                if not jd_text:
                    return jsonify({'error': 'Could not extract job description content from the provided URL'}), 400
            except Exception as e:
                return jsonify({'error': f'Failed to fetch content from URL: {str(e)}'}), 400
        
        if not jd_text:
            return jsonify({'error': 'No job description text or URL provided'}), 400
        
        # Save original prompt
        original_prompt = jd_agent.get_prompt()
        
        try:
            # Temporarily use custom prompt if provided
            if custom_prompt:
                jd_agent.update_prompt(custom_prompt)
            
            # Parse the job description
            result = jd_agent.parse_job_description(jd_text)
            
            # Convert to dictionary for JSON response
            result_dict = jd_agent.to_dict(result)
            
            response_data = {
                'success': True,
                'result': result_dict,
                'agent_info': {
                    'version': jd_agent.version,
                    'agent_id': jd_agent.agent_id
                },
                'prompt_used': custom_prompt if custom_prompt else original_prompt
            }
            
            # Include source info if URL was used
            if jd_url:
                response_data['source'] = {
                    'type': 'url',
                    'url': jd_url,
                    'extracted_text_length': len(jd_text)
                }
            
            return jsonify(response_data)
            
        finally:
            # Always restore original prompt
            if custom_prompt:
                jd_agent.update_prompt(original_prompt)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/parse', methods=['POST'])
def parse_jd():
    """Parse a job description and return structured results"""
    try:
        data = request.get_json()
        jd_text = data.get('jd_text', '').strip()
        jd_url = data.get('jd_url', '').strip()
        
        # If URL is provided, fetch content from the web
        if jd_url:
            try:
                jd_text = fetch_job_description_from_url(jd_url)
                if not jd_text:
                    return jsonify({'error': 'Could not extract job description content from the provided URL'}), 400
            except Exception as e:
                return jsonify({'error': f'Failed to fetch content from URL: {str(e)}'}), 400
        
        if not jd_text:
            return jsonify({'error': 'No job description text or URL provided'}), 400
        
        # Parse the job description
        result = jd_agent.parse_job_description(jd_text)
        
        # Convert to dictionary for JSON response
        result_dict = jd_agent.to_dict(result)
        
        response_data = {
            'success': True,
            'result': result_dict,
            'agent_info': {
                'version': jd_agent.version,
                'agent_id': jd_agent.agent_id
            }
        }
        
        # Include source info if URL was used
        if jd_url:
            response_data['source'] = {
                'type': 'url',
                'url': jd_url,
                'extracted_text_length': len(jd_text)
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/compare', methods=['POST'])
def compare_results():
    """Compare parsing results between different JD texts"""
    try:
        data = request.get_json()
        jd_texts = data.get('jd_texts', [])
        
        if len(jd_texts) < 2:
            return jsonify({'error': 'Need at least 2 job descriptions to compare'}), 400
        
        results = []
        for i, jd_text in enumerate(jd_texts[:5]):  # Limit to 5 comparisons
            if jd_text.strip():
                result = jd_agent.parse_job_description(jd_text.strip())
                results.append({
                    'index': i,
                    'parsed_result': jd_agent.to_dict(result)
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'comparison_summary': _generate_comparison_summary(results)
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


def _generate_comparison_summary(results):
    """Generate a summary comparing multiple parsing results"""
    
    summary = {
        'total_jobs': len(results),
        'avg_confidence': 0.0,
        'skills_comparison': {},
        'sections_comparison': {}
    }
    
    if not results:
        return summary
    
    # Calculate averages
    total_confidence = sum(r['parsed_result']['confidence_score'] for r in results)
    summary['avg_confidence'] = total_confidence / len(results)
    
    # Compare skills across jobs
    all_required_skills = []
    all_preferred_skills = []
    
    for result in results:
        all_required_skills.extend(result['parsed_result']['required_skills'])
        all_preferred_skills.extend(result['parsed_result']['preferred_skills'])
    
    summary['skills_comparison'] = {
        'common_required_skills': _find_common_items(results, 'required_skills'),
        'common_preferred_skills': _find_common_items(results, 'preferred_skills'),
        'total_unique_required': len(set(all_required_skills)),
        'total_unique_preferred': len(set(all_preferred_skills))
    }
    
    # Compare section completeness
    section_counts = {}
    for result in results:
        for section_name, section_data in result['parsed_result'].items():
            if isinstance(section_data, list):
                section_counts[section_name] = section_counts.get(section_name, 0) + len(section_data)
    
    summary['sections_comparison'] = section_counts
    
    return summary


def _find_common_items(results, field_name):
    """Find items that appear in multiple results"""
    if not results:
        return []
    
    # Get all items from first result
    first_items = set(results[0]['parsed_result'].get(field_name, []))
    
    # Find intersection with other results
    for result in results[1:]:
        result_items = set(result['parsed_result'].get(field_name, []))
        first_items = first_items.intersection(result_items)
    
    return list(first_items)


def fetch_job_description_with_requests_html(url):
    """Enhanced web scraper using requests-html for JavaScript-heavy sites"""
    
    if not REQUESTS_HTML_AVAILABLE:
        raise Exception("requests-html not available. Install with: pip install requests-html")
    
    try:
        print(f"🌐 Using requests-html for JavaScript rendering: {url}")
        
        session = HTMLSession()
        
        # Set a user agent
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Get the page
        response = session.get(url, timeout=30)
        
        # Render JavaScript with longer timeout and retry logic
        print("🔄 Rendering JavaScript content...")
        try:
            response.html.render(timeout=60, keep_page=True, sleep=5, wait=2)
        except Exception as render_error:
            print(f"⚠️  First render attempt failed: {render_error}")
            # Try again with different settings
            try:
                print("🔄 Retrying with simpler settings...")
                response.html.render(timeout=45, sleep=2)
            except Exception as retry_error:
                print(f"⚠️  Retry failed: {retry_error}")
                # Fall back to raw HTML without JavaScript
                print("🔄 Using raw HTML without JavaScript rendering")
                page_source = response.html.html
        
        # Extract content
        title = response.html.find('title', first=True)
        page_title = title.text if title else ""
        
        # Get all text content
        text_content = response.html.text
        
        # Look for Microsoft-specific patterns
        if "microsoft.com" in url:
            print("🔍 Using Microsoft-specific content extraction")
            # Try to find job description specific elements
            job_elements = response.html.find('[data-automation-id*="job"], [data-automation-id*="description"]')
            if job_elements:
                microsoft_content = ""
                for element in job_elements:
                    element_text = element.text
                    if len(element_text) > 50:  # Only include substantial content
                        microsoft_content += f"\n{element_text}\n"
                
                if microsoft_content.strip():
                    text_content = microsoft_content
        
        # Add title information
        if page_title:
            clean_title = page_title.split(' - ')[0].split(' | ')[0].strip()
            text_content = f"JOB TITLE: {clean_title}\n\nJOB DESCRIPTION:\n{text_content}"
        
        # Clean up the text
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_content = ' '.join(chunk for chunk in chunks if chunk)
        
        # Remove excessive whitespace
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # Validate content length
        if len(clean_content) < 100:
            raise Exception(f"Extracted content is too short ({len(clean_content)} chars). The page may not have loaded properly or content may be dynamically loaded.")
        
        print(f"✅ Successfully extracted {len(clean_content)} characters using requests-html")
        return clean_content
        
    except Exception as e:
        raise Exception(f"requests-html scraping failed: {str(e)}")
    finally:
        # Close the session
        try:
            session.close()
        except:
            pass


def fetch_job_description_with_selenium(url):
    """Enhanced web scraper using Selenium for JavaScript-heavy sites like Microsoft careers"""
    
    if not SELENIUM_AVAILABLE:
        raise Exception("Selenium WebDriver not available. Install with: pip install selenium webdriver-manager")
    
    driver = None
    try:
        print(f"🌐 Using Selenium WebDriver for JavaScript rendering: {url}")
        
        # Set up Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--disable-web-security')  # For local development
        
        # Disable images for faster loading but KEEP JavaScript enabled for SPA sites
        chrome_options.add_argument('--disable-images')
        # Note: JavaScript MUST be enabled for Microsoft careers and other SPA sites
        
        # User agent to avoid detection
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Explicitly set Chrome binary path on macOS
        if platform.system() == 'Darwin':  # macOS
            chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        
        # Set up the Chrome driver using WebDriver Manager with explicit version handling
        try:
            # Force a fresh download to fix compatibility issues
            import os
            os.environ['WDM_FORCE_RESTART'] = '1'
            service = Service(ChromeDriverManager().install())
        except Exception as e:
            print(f"⚠️  ChromeDriverManager failed: {e}")
            # Try alternative paths
            possible_paths = [
                '/usr/local/bin/chromedriver',
                '/opt/homebrew/bin/chromedriver',
                '/usr/bin/chromedriver'
            ]
            
            service = None
            for path in possible_paths:
                if os.path.exists(path):
                    try:
                        service = Service(path)
                        print(f"✅ Using ChromeDriver at: {path}")
                        break
                    except:
                        continue
            
            if not service:
                raise Exception("No working ChromeDriver found")
            
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set page load timeout
        driver.set_page_load_timeout(30)
        
        print("🔄 Loading page and waiting for JavaScript content...")
        driver.get(url)
        
        # Wait for page to load and JavaScript to execute
        time.sleep(5)
        
        # Wait for common job posting elements to appear
        wait = WebDriverWait(driver, 15)
        
        # Try multiple strategies to wait for content to load
        job_content_selectors = [
            '[data-automation-id="jobDescription"]',  # Microsoft careers specific
            '.job-description',
            '.job-details',
            '.position-description',
            '[class*="description"]',
            '[id*="description"]',
            'main',
            'article',
            '.content'
        ]
        
        content_element = None
        for selector in job_content_selectors:
            try:
                print(f"🔍 Waiting for element: {selector}")
                content_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                print(f"✅ Found content with selector: {selector}")
                break
            except TimeoutException:
                continue
        
        if not content_element:
            print("⚠️  No specific job content found, using full page content")
        
        # Extract page title
        title = driver.title
        print(f"📄 Page title: {title}")
        
        # Get page source after JavaScript execution
        page_source = driver.page_source
        
        # Parse with BeautifulSoup for better text extraction
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Try to find job-specific content
        job_content = ""
        
        # Microsoft careers specific selectors
        if "microsoft.com" in url:
            print("🔍 Using Microsoft-specific content extraction")
            job_sections = soup.find_all(['div', 'section'], attrs={
                'data-automation-id': True,
                'class': lambda x: x and any(keyword in str(x).lower() for keyword in ['job', 'description', 'requirement', 'responsibility'])
            })
            
            if job_sections:
                for section in job_sections:
                    text = section.get_text(separator=' ', strip=True)
                    if len(text) > 50:  # Only include substantial content
                        job_content += f"\n{text}\n"
        
        # Fallback: extract all text content
        if not job_content.strip():
            print("🔄 Using general content extraction")
            job_content = soup.get_text(separator=' ', strip=True)
        
        # Add title information
        if title and not title.lower().startswith('page'):
            clean_title = title.split(' - ')[0].split(' | ')[0].strip()
            job_content = f"JOB TITLE: {clean_title}\n\nJOB DESCRIPTION:\n{job_content}"
        
        # Clean up the text
        lines = (line.strip() for line in job_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_content = ' '.join(chunk for chunk in chunks if chunk)
        
        # Remove excessive whitespace
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # Validate content length
        if len(clean_content) < 100:
            raise Exception(f"Extracted content is too short ({len(clean_content)} chars). The page may not have loaded properly or content may be dynamically loaded.")
        
        print(f"✅ Successfully extracted {len(clean_content)} characters using Selenium")
        return clean_content
        
    except TimeoutException:
        raise Exception("Page load timeout. The website may be slow or blocking automated access.")
    except WebDriverException as e:
        raise Exception(f"WebDriver error: {str(e)}")
    except Exception as e:
        raise Exception(f"Selenium scraping failed: {str(e)}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


def fetch_job_description_from_url(url):
    """Fetch and extract job description content from a web URL"""
    print(f"🌐 DEBUG: Starting fetch_job_description_from_url for: {url}")
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format")
        
        # Check if this is a JavaScript-heavy site that needs Selenium
        js_heavy_domains = [
            'microsoft.com',
            'careers.microsoft.com',
            'jobs.careers.microsoft.com',
            'workday.com',
            'lever.co',
            'greenhouse.io',
            'careerpuck.com',
            'app.careerpuck.com',
            'angular',
            'react',
            'vue'  # Sites that mention SPA frameworks
        ]
        
        # Special handling: Don't use Selenium for sites with known Cloudflare protection
        cloudflare_protected_domains = [
            'servicenow.com',
            'careers.servicenow.com'
        ]
        
        needs_selenium = any(domain in parsed_url.netloc.lower() for domain in js_heavy_domains)
        is_cloudflare_protected = any(domain in parsed_url.netloc.lower() for domain in cloudflare_protected_domains)
        
        # Use Selenium directly for known JavaScript-heavy sites (but not for Cloudflare-protected ones)
        if needs_selenium and SELENIUM_AVAILABLE and not is_cloudflare_protected:
            print(f"🌐 Detected JavaScript-heavy site {parsed_url.netloc}, using Selenium...")
            return fetch_job_description_with_selenium(url)
        
        # For now, try standard scraping first, then fall back to Selenium if needed
        print(f"🌐 Attempting enhanced scraping for: {parsed_url.netloc} (JS-heavy: {needs_selenium})")
        
        # Standard scraping approach for regular sites
        print(f"🌐 Using standard HTTP scraping for: {parsed_url.netloc}")
        
        # Set up headers to mimic a real browser more convincingly
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Cache-Control': 'max-age=0'
        }
        
        # Fetch the webpage with retry logic
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                break
            except requests.exceptions.HTTPError as e:
                if response.status_code == 403:
                    if attempt == max_retries - 1:
                            # Only try Selenium if not Cloudflare protected
                        if SELENIUM_AVAILABLE and not any(domain in parsed_url.netloc.lower() for domain in ['servicenow.com', 'careers.servicenow.com']):
                            print("🔄 Standard scraping blocked, trying Selenium fallback...")
                            return fetch_job_description_with_selenium(url)
                        raise Exception(f"Access denied (403 Forbidden). The website '{parsed_url.netloc}' is blocking automated requests. Please try copying the job description content directly instead of using the URL.")
                    # Try with a different user agent on retry
                    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
                    continue
                elif response.status_code == 404:
                    raise Exception(f"Job posting not found (404). The URL may be incorrect or the job may have been removed.")
                elif response.status_code >= 500:
                    raise Exception(f"Server error ({response.status_code}). The website may be temporarily unavailable.")
                else:
                    raise Exception(f"HTTP {response.status_code}: {str(e)}")
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    # Only try Selenium if not Cloudflare protected
                    if SELENIUM_AVAILABLE and not any(domain in parsed_url.netloc.lower() for domain in ['servicenow.com', 'careers.servicenow.com']):
                        print("🔄 Network error, trying Selenium fallback...")
                        return fetch_job_description_with_selenium(url)
                    raise e
                continue
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements but preserve job title areas
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        # Extract job title from multiple sources with enhanced Microsoft support
        title_text = ""
        job_details = {}
        
        # 1. Try HTML title tag
        title_tag = soup.find('title')
        if title_tag:
            title_content = title_tag.get_text(strip=True)
            # Clean up title (remove "at Company" suffix)
            if ' at ' in title_content:
                title_content = title_content.split(' at ')[0]
            if ' - ' in title_content:
                title_content = title_content.split(' - ')[0]
            title_text += title_content + " | "
        
        # 2. Try meta property og:title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            title_text += og_title['content'].strip() + " | "
        
        # 3. Microsoft-specific meta tags
        if 'microsoft.com' in url:
            description_meta = soup.find('meta', attrs={'name': 'description'})
            if description_meta and description_meta.get('content'):
                meta_content = description_meta['content']
                print(f"🔍 Found Microsoft description meta: {meta_content[:100]}...")
                job_details['description'] = meta_content
        
        # 4. Try JSON-LD structured data (common in job postings)
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'JobPosting':
                    job_details['structured_data'] = data
                    if 'title' in data:
                        title_text += data['title'] + " | "
                    print("🔍 Found JobPosting structured data")
            except:
                continue
        
        # 5. Try h1, h2, h3 tags with job title patterns
        for tag in ['h1', 'h2', 'h3']:
            headers = soup.find_all(tag)
            for header in headers[:3]:  # Check first 3 of each type
                text = header.get_text(strip=True)
                if any(keyword in text.lower() for keyword in ['director', 'manager', 'engineer', 'analyst', 'specialist', 'lead', 'senior', 'coordinator', 'associate']):
                    title_text += text + " | "
        
        # Remove remaining header elements that might contain navigation but not titles
        for header in soup.find_all("header"):
            # Check if header contains title-like content
            if not any(title_keyword in header.get_text().lower() for title_keyword in ['director', 'manager', 'engineer', 'analyst', 'specialist', 'lead', 'senior', 'junior']):
                header.decompose()
        
        # Extract text content
        text = soup.get_text()
        
        # Prepend title information to ensure it's at the beginning
        if title_text.strip():
            # Clean up title text and add clear labeling
            clean_title = title_text.rstrip(" | ").replace(" | ", " ")
            text = f"JOB TITLE: {clean_title}\n\nJOB DESCRIPTION:\n{text}"
        
        # Clean up the text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Remove Unicode characters that can break JSON parsing
        import unicodedata
        text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char in '\n\r\t')
        
        # Remove private use area characters (like icon fonts)
        text = re.sub(r'[\uE000-\uF8FF]', '', text)  # Private Use Area
        text = re.sub(r'[\U000F0000-\U000FFFFD]', '', text)  # Supplementary Private Use Area A
        text = re.sub(r'[\U00100000-\U0010FFFD]', '', text)  # Supplementary Private Use Area B
        
        # Try to identify job description specific content
        # Look for common job posting patterns
        jd_patterns = [
            r'job\s+description',
            r'responsibilities',
            r'requirements',
            r'qualifications',
            r'about\s+the\s+role',
            r'position\s+summary',
            r'we\s+are\s+looking\s+for',
            r'join\s+our\s+team'
        ]
        
        # If the text is very long, try to extract relevant sections
        if len(text) > 8000:  # Reduced from 5000 to be more aggressive
            text_lower = text.lower()
            
            # Find the start of job description content
            start_pos = 0
            for pattern in jd_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    start_pos = max(0, match.start() - 200)  # Include some context before
                    break
            
            # Extract a reasonable chunk around the job description
            if start_pos > 0:
                text = text[start_pos:start_pos + 6000]  # Increased from 4000 but still manageable
            else:
                # If no pattern found, take first 6000 chars after removing common noise
                text = text[:6000]
        
        # Final cleanup
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Enhanced content validation and fallback
        # Check for corrupted content (Unicode replacement characters) and JavaScript-heavy content
        js_keywords = ['function', 'var', 'const', 'let', 'document.', 'window.', 'console.log', 'addEventListener', 'querySelector']
        js_keyword_count = sum(text.count(keyword) for keyword in js_keywords)
        
        corruption_indicators = [
            '�' in text,  # Unicode replacement character
            '\ufffd' in text,  # Unicode replacement character
            len([c for c in text[:500] if ord(c) < 32 and c not in '\n\r\t']) > 20,  # Too many control characters
            len(text) > 500 and len([c for c in text if c.isalpha()]) / len(text) < 0.3,  # Too few readable chars
            js_keyword_count > 10 and len(text) > 1000  # Primarily JavaScript content
        ]
        
        is_corrupted = any(corruption_indicators)
        
        # Debug logging for corruption detection
        print(f"🔍 Corruption detection: text_length={len(text)}, js_keywords={js_keyword_count}, is_corrupted={is_corrupted}")
        if is_corrupted:
            print(f"📊 Corruption indicators: {[i for i, x in enumerate(corruption_indicators) if x]}")
        
        if len(text) < 100 or is_corrupted:
            if is_corrupted:
                error_msg = f"Extracted content appears corrupted (Unicode replacement chars detected). Length: {len(text)} chars."
            else:
                error_msg = f"Extracted content is too short ({len(text)} chars) to be a job description."
            
            # If we detected this is a JS-heavy site, try JavaScript fallbacks
            if needs_selenium:
                if REQUESTS_HTML_AVAILABLE:
                    print(f"⚠️  {error_msg} Trying requests-html fallback...")
                    try:
                        return fetch_job_description_with_requests_html(url)
                    except Exception as rh_error:
                        print(f"🚫 requests-html fallback failed: {rh_error}")
                        
                        # Try Selenium as last resort
                        if SELENIUM_AVAILABLE:
                            print(f"🔄 Trying Selenium as final fallback...")
                            try:
                                return fetch_job_description_with_selenium(url)
                            except Exception as selenium_error:
                                print(f"🚫 Selenium fallback also failed: {selenium_error}")
                        
                elif SELENIUM_AVAILABLE:
                    print(f"⚠️  {error_msg} Trying Selenium fallback...")
                    try:
                        return fetch_job_description_with_selenium(url)
                    except Exception as selenium_error:
                        print(f"🚫 Selenium fallback also failed: {selenium_error}")
            
            # If we have any job details from structured data, use those
            if job_details:
                fallback_content = f"JOB POSTING METADATA:\n"
                if 'description' in job_details:
                    fallback_content += f"\nDescription: {job_details['description']}\n"
                if 'structured_data' in job_details:
                    sd = job_details['structured_data']
                    if 'title' in sd:
                        fallback_content += f"\nJob Title: {sd['title']}\n"
                    if 'description' in sd:
                        fallback_content += f"\nJob Description: {sd['description']}\n"
                    if 'hiringOrganization' in sd:
                        fallback_content += f"\nCompany: {sd.get('hiringOrganization', {}).get('name', 'N/A')}\n"
                
                if len(fallback_content) > 150:
                    print(f"✅ Using metadata fallback content ({len(fallback_content)} chars)")
                    return fallback_content
            
            # Special handling for ServiceNow careers - provide informative fallback
            if 'servicenow.com' in url:
                print(f"🔍 ServiceNow careers site detected - providing informative fallback")
                fallback_content = f"""
                JOB POSTING - ServiceNow Careers Site
                
                URL: {url}
                Issue: ServiceNow careers pages are protected by Cloudflare anti-bot security that blocks automated access.
                
                EXTRACTED INFORMATION:
                - Company: ServiceNow
                - Job ID: {url.split('/')[-2] if '/' in url else 'Unknown'}
                - Position: {url.split('/')[-1].replace('-', ' ').title() if '/' in url else 'Unknown'}
                
                RECOMMENDATION: 
                To get the full job description, please:
                1. Open the ServiceNow careers page in your browser
                2. Copy the complete job description text 
                3. Paste it into the text field instead of using the URL
                
                This will bypass the anti-bot protection and ensure you get the complete job requirements and description for accurate CV analysis.
                
                Note: ServiceNow recently implemented Cloudflare protection to prevent automated scraping of their job postings.
                """
                return fallback_content
            
            # Special handling for Microsoft careers - provide informative fallback
            if 'microsoft.com' in url:
                print(f"🔍 Microsoft careers site detected - providing informative fallback")
                fallback_content = f"""
                JOB POSTING - Microsoft Careers Site
                
                URL: {url}
                Issue: This Microsoft careers page uses advanced JavaScript that requires a browser to load properly.
                
                EXTRACTED INFORMATION:
                - Company: Microsoft Corporation
                - URL Pattern indicates this is job ID: {url.split('/')[-1] if '/' in url else 'Unknown'}
                
                RECOMMENDATION: 
                To get the full job description, please:
                1. Copy the job description text directly from the Microsoft careers page
                2. Paste it into the text field instead of using the URL
                
                This will ensure you get the complete job requirements and description for accurate CV analysis.
                
                Note: Microsoft's careers site uses Single Page Application (SPA) technology that loads content dynamically,
                making it challenging for automated scrapers to extract content reliably.
                """
                return fallback_content
            
            raise ValueError(error_msg + " No suitable fallback content available.")
        
        return text
        
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise Exception(f"Error processing content: {str(e)}")


@app.route('/status')
def status():
    """Status endpoint for service health checks"""
    return jsonify({
        'success': True,
        'agent': 'jd_parser',
        'version': jd_agent.version,
        'status': 'online',
        'capabilities': ['url_parsing', 'text_parsing', 'llm_processing']
    })


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    print("🚀 Starting JD Parser Agent Testing Interface...")
    print("📍 Access at: http://localhost:5003")
    print("🔧 Agent Version:", jd_agent.version)
    
    app.run(debug=True, host='0.0.0.0', port=5003)