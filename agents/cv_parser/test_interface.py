#!/usr/bin/env python3
"""
CV Parser Agent - Testing Interface

Simple web interface for testing the CV Parser Agent with different
CV/resume documents and comparing results between different configurations.
"""


import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from agent import CVParserAgent
import traceback
import io
import tempfile

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global agent instance
cv_agent = CVParserAgent()

# Sample CVs for testing
SAMPLE_CVS = {
    "tech_senior": """John Smith
john.smith@email.com
(555) 123-4567
San Francisco, CA

PROFESSIONAL SUMMARY
Senior Software Engineer with 8+ years of experience in full-stack development. Proven track record of delivering scalable web applications and leading cross-functional teams.

TECHNICAL SKILLS
• Programming Languages: Python, JavaScript, TypeScript, Java
• Frontend: React, Vue.js, HTML5, CSS3, Bootstrap
• Backend: Node.js, Express, Django, Flask
• Databases: PostgreSQL, MongoDB, Redis
• Cloud Platforms: AWS (EC2, S3, Lambda), Azure, GCP
• DevOps: Docker, Kubernetes, Jenkins, Git

WORK EXPERIENCE

Senior Software Engineer - Google (2020-2024)
• Led development of cloud infrastructure components serving 1M+ users
• Managed team of 5 engineers, conducting code reviews and mentoring
• Implemented microservices architecture reducing system latency by 40%
• Collaborated with product managers and designers on feature planning

Software Engineer - Apple (2018-2020)
• Developed iOS applications using Swift and Objective-C
• Collaborated with design teams to implement user-friendly interfaces
• Optimized app performance resulting in 25% faster load times
• Participated in Agile development processes and sprint planning

Junior Developer - StartupCorp (2016-2018)
• Built responsive web applications using React and Node.js
• Integrated third-party APIs and payment systems
• Wrote comprehensive unit and integration tests
• Contributed to open-source projects and documentation

EDUCATION
Master of Science in Computer Science - Stanford University (2018)
Bachelor of Science in Computer Science - UC Berkeley (2016)
GPA: 3.8/4.0

CERTIFICATIONS
• AWS Certified Solutions Architect - Professional (2023)
• Google Cloud Professional Developer (2022)
• Certified Kubernetes Administrator (2021)

PROJECTS
E-commerce Platform
• Built full-stack e-commerce solution using React, Node.js, and MongoDB
• Implemented secure payment processing and user authentication
• Technologies: React, Node.js, MongoDB, Stripe API
• URL: github.com/johnsmith/ecommerce-platform

AI-Powered Chat Application
• Developed real-time chat application with AI-powered responses
• Integrated OpenAI GPT API for intelligent conversation features
• Technologies: Python, Flask, WebSocket, OpenAI API
• URL: github.com/johnsmith/ai-chat

LANGUAGES
• English (Native)
• Spanish (Conversational)
• Mandarin (Basic)

ACHIEVEMENTS
• Winner of Google Developer Challenge 2023
• Published 3 technical articles on Medium with 10k+ views
• Speaker at React Conference 2022

VOLUNTEER WORK
• Code for America - Volunteer Developer (2019-2021)
• Teaching Assistant for CS101 at Stanford University (2017-2018)""",

    "finance_analyst": """Sarah Johnson
sarah.johnson@email.com
(555) 987-6543
New York, NY
LinkedIn: linkedin.com/in/sarahjohnson

PROFESSIONAL SUMMARY
Detail-oriented Financial Analyst with 5+ years of experience in corporate finance, financial modeling, and strategic planning. Strong analytical skills with expertise in variance analysis and executive reporting.

CORE COMPETENCIES
• Financial Modeling & Analysis
• Variance Analysis & Reporting
• Strategic Planning & Forecasting
• Risk Assessment & Management
• Data Analysis & Visualization
• Stakeholder Communication

TECHNICAL SKILLS
• Software: Excel (Advanced), SQL, Tableau, Power BI, SAP, Oracle
• Programming: Python, R (basic)
• Financial Tools: Bloomberg Terminal, FactSet, Capital IQ

PROFESSIONAL EXPERIENCE

Senior Financial Analyst - Goldman Sachs (2021-2024)
• Developed comprehensive financial models for M&A transactions worth $500M+
• Performed variance analysis identifying cost savings opportunities of $2M annually
• Prepared executive presentations for C-suite leadership
• Led cross-functional teams in budget planning and forecasting processes
• Managed relationships with external auditors and regulatory compliance

Financial Analyst - JPMorgan Chase (2019-2021)
• Created automated financial reporting dashboards reducing manual work by 60%
• Conducted industry research and competitive analysis for investment decisions
• Supported deal execution for corporate lending transactions
• Analyzed credit risk for portfolio of $100M+ commercial loans
• Collaborated with sales teams on client pitch materials

Junior Analyst - Deutsche Bank (2018-2019)
• Assisted in financial due diligence for private equity transactions
• Maintained financial databases and performed data quality checks
• Supported senior analysts in creating client reports and presentations
• Participated in client meetings and conference calls

EDUCATION
Master of Business Administration (MBA) - Wharton School, University of Pennsylvania (2018)
Concentration: Finance and Strategic Management
GPA: 3.7/4.0

Bachelor of Science in Economics - University of Chicago (2016)
Magna Cum Laude, GPA: 3.8/4.0

CERTIFICATIONS
• CFA Level II Candidate (Exam scheduled June 2024)
• Financial Risk Manager (FRM) - GARP (2022)
• Bloomberg Market Concepts (BMC) Certification (2021)

ACHIEVEMENTS
• Wharton Finance Club President (2017-2018)
• Dean's List for 6 consecutive semesters
• Winner of University of Chicago Case Competition 2016

PUBLICATIONS
• "Alternative Investment Strategies in Volatile Markets" - Journal of Applied Finance (2023)
• "ESG Integration in Portfolio Management" - Finance Today Magazine (2022)

LANGUAGES
• English (Native)
• French (Fluent)
• German (Conversational)

VOLUNTEER EXPERIENCE
• Financial Literacy Volunteer - Junior Achievement (2020-Present)
• Mentor for Women in Finance Organization (2019-Present)""",

    "marketing_manager": """Michael Chen
michael.chen@email.com
(555) 456-7890
Los Angeles, CA
Portfolio: michaelchen.com

PROFESSIONAL SUMMARY
Creative Marketing Manager with 6+ years of experience driving digital marketing initiatives and leading high-performing teams. Proven track record of increasing brand awareness and generating qualified leads through data-driven campaigns.

CORE SKILLS
• Digital Marketing Strategy
• Social Media Management
• Content Marketing & SEO
• Marketing Automation
• Team Leadership & Development
• Campaign Performance Analysis

TECHNICAL PROFICIENCIES
• Marketing Platforms: HubSpot, Marketo, Salesforce, Mailchimp
• Analytics: Google Analytics, Adobe Analytics, Mixpanel
• Social Media: Facebook Ads Manager, LinkedIn Campaign Manager, Twitter Ads
• Design Tools: Adobe Creative Suite, Canva, Figma
• Other: HTML/CSS, Google Tag Manager, Zapier

WORK EXPERIENCE

Digital Marketing Manager - Tesla (2021-2024)
• Led digital marketing team of 8 specialists across paid media, content, and social
• Developed and executed comprehensive digital marketing strategies for Model 3 launch
• Increased website conversion rate by 45% through A/B testing and optimization
• Managed $2M annual marketing budget with 150% ROI improvement
• Collaborated with product and sales teams to align marketing initiatives

Marketing Manager - SpaceX (2019-2021)
• Created integrated marketing campaigns for Starlink internet service launch
• Managed social media presence across platforms with 500k+ followers
• Developed content marketing strategy increasing organic traffic by 200%
• Led rebranding initiative resulting in 30% increase in brand recognition
• Coordinated with PR team on major announcement communications

Marketing Specialist - Uber (2018-2019)
• Executed performance marketing campaigns across Google Ads and Facebook
• Created marketing automation workflows increasing lead nurturing efficiency by 60%
• Analyzed campaign performance and provided weekly reporting to management
• Supported trade show and event marketing initiatives
• Assisted in developing customer retention strategies

EDUCATION
Master of Business Administration (MBA) - UCLA Anderson School of Management (2018)
Concentration: Marketing and Entrepreneurship

Bachelor of Arts in Communications - University of Southern California (2016)
Minor in Digital Media

CERTIFICATIONS
• Google Ads Certified (Search, Display, Video)
• HubSpot Content Marketing Certification
• Facebook Blueprint Certified
• Google Analytics Individual Qualification (IQ)

PROJECTS
Brand Redesign Campaign - Tesla Model Y
• Led complete brand redesign for Model Y launch campaign
• Coordinated across creative, digital, and traditional media channels
• Delivered 40% increase in pre-order conversions
• Budget: $5M, Timeline: 6 months

Influencer Marketing Program - SpaceX
• Developed influencer partnership program for Starlink
• Managed relationships with 50+ tech and space influencers
• Generated 10M+ impressions and 2M+ video views
• ROI: 300% above industry benchmark

LANGUAGES
• English (Native)
• Mandarin (Fluent)
• Spanish (Intermediate)

AWARDS & RECOGNITION
• Marketing Excellence Award - Tesla (2023)
• Rising Star in Marketing - USC Alumni Association (2022)
• Best Integrated Campaign - Digital Marketing Awards (2021)

VOLUNTEER WORK
• Marketing Consultant - Local Non-Profit Animal Shelter (2020-Present)
• Guest Lecturer - UCLA Extension Marketing Program (2022-Present)"""
}


@app.route('/')
def index():
    """Main testing interface"""
    return render_template('test_interface.html', sample_cvs=SAMPLE_CVS)


@app.route('/get_current_prompt', methods=['GET'])
def get_current_prompt():
    """Get the current parsing prompt"""
    try:
        return jsonify({
            'success': True,
            'prompt': cv_agent.get_prompt(),
            'prompt_id': 'default',
            'prompt_name': 'Default CV Parsing Prompt'
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
        cv_agent.update_prompt(new_prompt)
        
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
        success = cv_agent.save_as_default_prompt(prompt)
        
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
    """Parse CV with a specific prompt"""
    try:
        data = request.get_json()
        cv_text = data.get('cv_text', '').strip()
        custom_prompt = data.get('prompt', '').strip()
        
        if not cv_text:
            return jsonify({'error': 'No CV text provided'}), 400
        
        # Save original prompt
        original_prompt = cv_agent.get_prompt()
        
        try:
            # Temporarily use custom prompt if provided
            if custom_prompt:
                cv_agent.update_prompt(custom_prompt)
            
            # Parse the CV
            result = cv_agent.parse_cv(cv_text)
            
            # Convert to dictionary for JSON response
            result_dict = cv_agent.to_dict(result)
            
            response_data = {
                'success': True,
                'result': result_dict,
                'agent_info': {
                    'version': cv_agent.version,
                    'agent_id': cv_agent.agent_id
                },
                'prompt_used': custom_prompt if custom_prompt else original_prompt
            }
            
            return jsonify(response_data)
            
        finally:
            # Always restore original prompt
            if custom_prompt:
                cv_agent.update_prompt(original_prompt)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/parse', methods=['POST'])
def parse_cv():
    """Parse a CV and return structured results"""
    try:
        data = request.get_json()
        cv_text = data.get('cv_text', '').strip()
        
        if not cv_text:
            return jsonify({'error': 'No CV text provided'}), 400
        
        print(f"🔧 DEBUG: Processing CV text of length {len(cv_text)}")
        print(f"🔧 DEBUG: Using model: {cv_agent.model_name}")
        
        # Parse the CV
        result = cv_agent.parse_cv(cv_text)
        
        print(f"🔧 DEBUG: Parse result type: {type(result)}")
        print(f"🔧 DEBUG: Parse result full_name: {result.full_name}")
        
        # Convert to dictionary for JSON response
        result_dict = cv_agent.to_dict(result)
        
        response_data = {
            'success': True,
            'result': result_dict,
            'agent_info': {
                'version': cv_agent.version,
                'agent_id': cv_agent.agent_id
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/parse_file', methods=['POST'])
def parse_cv_file():
    """Parse a CV file (PDF, DOC, DOCX) directly with Claude"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file content as bytes
        file_content = file.read()
        
        # Send file directly to Claude for processing
        result = cv_agent.parse_cv_file(file_content, file.filename)
        
        # Convert to dictionary for JSON response
        result_dict = cv_agent.to_dict(result)
        
        response_data = {
            'success': True,
            'result': result_dict,
            'agent_info': {
                'version': cv_agent.version,
                'agent_id': cv_agent.agent_id
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500




@app.route('/compare', methods=['POST'])
def compare_results():
    """Compare parsing results between different CV texts"""
    try:
        data = request.get_json()
        cv_texts = data.get('cv_texts', [])
        
        if len(cv_texts) < 2:
            return jsonify({'error': 'Need at least 2 CVs to compare'}), 400
        
        results = []
        for i, cv_text in enumerate(cv_texts[:5]):  # Limit to 5 comparisons
            if cv_text.strip():
                result = cv_agent.parse_cv(cv_text.strip())
                results.append({
                    'index': i,
                    'parsed_result': cv_agent.to_dict(result)
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
        'total_cvs': len(results),
        'avg_confidence': 0.0,
        'skills_comparison': {},
        'experience_comparison': {},
        'education_comparison': {}
    }
    
    if not results:
        return summary
    
    # Calculate averages
    total_confidence = sum(r['parsed_result']['confidence_score'] for r in results)
    summary['avg_confidence'] = total_confidence / len(results)
    
    # Compare skills across CVs
    all_skills = []
    for result in results:
        all_skills.extend(result['parsed_result']['key_skills'])
    
    summary['skills_comparison'] = {
        'common_skills': _find_common_items(results, 'key_skills'),
        'total_unique_skills': len(set(all_skills)),
        'avg_skills_per_cv': len(all_skills) / len(results) if results else 0
    }
    
    # Compare experience levels
    experience_years = []
    for result in results:
        work_exp = result['parsed_result']['work_experience']
        experience_years.append(len(work_exp))
    
    summary['experience_comparison'] = {
        'avg_positions': sum(experience_years) / len(experience_years) if experience_years else 0,
        'total_positions': sum(experience_years)
    }
    
    # Compare education levels
    education_counts = []
    for result in results:
        education = result['parsed_result']['education']
        education_counts.append(len(education))
    
    summary['education_comparison'] = {
        'avg_degrees': sum(education_counts) / len(education_counts) if education_counts else 0,
        'total_degrees': sum(education_counts)
    }
    
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


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    print("🚀 Starting CV Parser Agent Testing Interface...")
    print("📍 Access at: http://localhost:5004")
    print("🔧 Agent Version:", cv_agent.version)
    
    app.run(debug=True, host='0.0.0.0', port=5004)