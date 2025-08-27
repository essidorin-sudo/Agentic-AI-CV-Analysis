#!/usr/bin/env python3
"""
Gap Analyst Agent - Testing Interface

Flask web interface for testing the Gap Analyst Agent with Content Matcher integration.
Includes prompt engineering, color-coded gap analysis, and comprehensive scoring.
"""

import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from pathlib import Path
from agent import GapAnalystAgent

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"🔧 Loaded environment from {env_path}")
except ImportError:
    print("📝 python-dotenv not installed, using system environment variables")

app = Flask(__name__)

# Initialize the Gap Analyst Agent
agent = GapAnalystAgent()

# Agent endpoints
CONTENT_MATCHER_URL = "http://localhost:5005"
CV_PARSER_URL = "http://localhost:5004"
JD_PARSER_URL = "http://localhost:5007"

@app.route('/')
def index():
    """Simple, streamlined interface page"""
    return render_template('simple_interface.html')

@app.route('/complex')
def complex_interface():
    """Complex testing interface page"""
    return render_template('test_interface.html')

@app.route('/status')
def status():
    """Check agent status and dependencies"""
    try:
        # Check all agent statuses
        cv_parser_online = False
        jd_parser_online = False
        content_matcher_online = False
        
        try:
            response = requests.get(f"{CV_PARSER_URL}/status", timeout=3)
            if response.status_code == 200:
                cv_parser_online = True
        except:
            pass
            
        try:
            response = requests.get(f"{JD_PARSER_URL}/status", timeout=3)
            if response.status_code == 200:
                jd_parser_online = True
        except:
            pass
            
        try:
            response = requests.get(f"{CONTENT_MATCHER_URL}/status", timeout=3)
            if response.status_code == 200:
                content_matcher_online = True
        except:
            pass
        
        return jsonify({
            'success': True,
            'agent_version': agent.version,
            'model': agent.model_name,
            'agents': {
                'cv_parser': cv_parser_online,
                'jd_parser': jd_parser_online,
                'content_matcher': content_matcher_online,
                'gap_analyst': True
            },
            'anthropic_configured': bool(agent.anthropic_api_key)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download_from_matcher')
def download_from_matcher():
    """Download results from Content Matcher Agent"""
    try:
        # This endpoint would fetch the latest processed data from Content Matcher
        # For now, we'll return a mock response showing the expected structure
        
        response = requests.get(f"{CONTENT_MATCHER_URL}/get_latest_results", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'cv_data': data.get('cv_data', {}),
                'jd_data': data.get('jd_data', {}),
                'timestamp': data.get('timestamp', '')
            })
        else:
            # Return mock data if Content Matcher is not available
            return jsonify({
                'success': True,
                'cv_data': {
                    'full_name': 'Test User',
                    'key_skills': ['Python', 'JavaScript', 'React'],
                    'work_experience': [
                        {
                            'position': 'Software Engineer',
                            'company': 'Tech Corp',
                            'duration': '2020-2024',
                            'responsibilities': ['Developed web applications', 'Led team projects']
                        }
                    ],
                    'education': [
                        {
                            'degree': 'Bachelor of Science',
                            'field': 'Computer Science',
                            'institution': 'University of Technology',
                            'graduation': '2020'
                        }
                    ]
                },
                'jd_data': {
                    'job_title': 'Senior Software Engineer',
                    'company_name': 'Innovation Labs',
                    'required_skills': ['Python', 'React', 'AWS', 'Docker'],
                    'preferred_skills': ['Kubernetes', 'GraphQL'],
                    'required_experience': ['5+ years software development experience'],
                    'required_education': ['Bachelor\'s degree in Computer Science or related field']
                },
                'timestamp': '2024-01-01T12:00:00',
                'source': 'mock_data'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/analyze_gap', methods=['POST'])
def analyze_gap():
    """Perform gap analysis between CV and JD data"""
    try:
        data = request.get_json()
        cv_data = data.get('cv_data', {})
        jd_data = data.get('jd_data', {})
        
        if not cv_data or not jd_data:
            return jsonify({'success': False, 'error': 'Both CV and JD data are required'})
        
        # Perform gap analysis
        result = agent.analyze_cv_jd_gap(cv_data, jd_data)
        
        # Convert result to dictionary for JSON response
        response_data = {
            'success': True,
            'result': {
                'cv_data': result.cv_data,
                'jd_data': result.jd_data,
                'cv_highlighted': result.cv_highlighted,
                'jd_highlighted': result.jd_highlighted,
                'match_score': {
                    'overall_score': result.match_score.overall_score,
                    'skills_score': result.match_score.skills_score,
                    'experience_score': result.match_score.experience_score,
                    'education_score': result.match_score.education_score,
                    'qualifications_score': result.match_score.qualifications_score,
                    'recommendations': result.match_score.recommendations,
                    'strengths': result.match_score.strengths,
                    'gaps': result.match_score.gaps
                },
                'analysis_notes': result.analysis_notes,
                'timestamp': result.timestamp
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Gap analysis error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_prompt')
def get_prompt():
    """Get the current gap analysis prompt"""
    try:
        return jsonify({
            'success': True,
            'prompt': agent.get_prompt()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/update_prompt', methods=['POST'])
def update_prompt():
    """Update the gap analysis prompt"""
    try:
        data = request.get_json()
        new_prompt = data.get('prompt', '')
        
        if not new_prompt:
            return jsonify({'success': False, 'error': 'Prompt cannot be empty'})
        
        agent.update_prompt(new_prompt)
        
        return jsonify({
            'success': True,
            'message': 'Prompt updated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/save_default_prompt', methods=['POST'])
def save_default_prompt():
    """Save the current prompt as default"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt cannot be empty'})
        
        success = agent.save_as_default_prompt(prompt)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Prompt saved as default successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save prompt as default'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/test_analysis')
def test_analysis():
    """Test gap analysis with sample data"""
    try:
        # Sample CV data
        sample_cv = {
            "full_name": "John Doe",
            "key_skills": ["Python", "JavaScript", "React", "SQL", "Git"],
            "work_experience": [
                {
                    "position": "Software Engineer",
                    "company": "Tech Solutions Inc",
                    "duration": "2021-2024",
                    "responsibilities": [
                        "Developed web applications using React and Node.js",
                        "Collaborated with cross-functional teams",
                        "Implemented REST APIs"
                    ]
                },
                {
                    "position": "Junior Developer",
                    "company": "StartupCorp",
                    "duration": "2020-2021",
                    "responsibilities": [
                        "Built responsive web interfaces",
                        "Worked with SQL databases"
                    ]
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "institution": "State University",
                    "graduation": "2020"
                }
            ]
        }
        
        # Sample JD data
        sample_jd = {
            "job_title": "Senior Software Engineer",
            "company_name": "Innovation Labs",
            "required_skills": ["Python", "React", "AWS", "Docker"],
            "preferred_skills": ["Kubernetes", "GraphQL", "TypeScript"],
            "required_experience": ["5+ years software development experience", "Experience with cloud platforms"],
            "required_education": ["Bachelor's degree in Computer Science or related field"],
            "key_responsibilities": [
                "Lead development of scalable web applications",
                "Mentor junior developers",
                "Design system architecture"
            ]
        }
        
        # Perform analysis
        result = agent.analyze_cv_jd_gap(sample_cv, sample_jd)
        
        return jsonify({
            'success': True,
            'cv_data': sample_cv,
            'jd_data': sample_jd,
            'analysis_result': {
                'overall_score': result.match_score.overall_score,
                'skills_score': result.match_score.skills_score,
                'experience_score': result.match_score.experience_score,
                'education_score': result.match_score.education_score,
                'qualifications_score': result.match_score.qualifications_score,
                'strengths': result.match_score.strengths,
                'gaps': result.match_score.gaps,
                'recommendations': result.match_score.recommendations
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/process_cv_and_jd', methods=['POST'])
def process_cv_and_jd():
    """Process CV file and JD through the complete pipeline"""
    try:
        import time
        
        # Step 1: Get inputs
        cv_file = request.files.get('cv_file')
        jd_url = request.form.get('jd_url', '').strip()
        jd_text = request.form.get('jd_text', '').strip()
        
        if not cv_file:
            return jsonify({'success': False, 'error': 'CV file is required'})
        
        if not jd_url and not jd_text:
            return jsonify({'success': False, 'error': 'Job description URL or text is required'})
        
        workflow_steps = []
        
        # Step 2: Process CV through CV Parser
        workflow_steps.append({'step': 'cv_parsing', 'status': 'in_progress', 'message': 'Sending CV to CV Parser Agent...'})
        
        cv_files = {'file': (cv_file.filename, cv_file.read(), cv_file.content_type)}
        cv_response = requests.post(f"{CV_PARSER_URL}/parse_file", files=cv_files, timeout=60)
        
        if cv_response.status_code != 200:
            workflow_steps.append({'step': 'cv_parsing', 'status': 'failed', 'message': 'CV parsing failed'})
            return jsonify({'success': False, 'error': 'CV parsing failed', 'workflow_steps': workflow_steps})
        
        cv_data = cv_response.json()
        if not cv_data.get('success'):
            workflow_steps.append({'step': 'cv_parsing', 'status': 'failed', 'message': cv_data.get('error', 'CV parsing failed')})
            return jsonify({'success': False, 'error': cv_data.get('error', 'CV parsing failed'), 'workflow_steps': workflow_steps})
        
        workflow_steps.append({'step': 'cv_parsing', 'status': 'completed', 'message': 'CV parsed successfully'})
        
        # Step 3: Process JD through JD Parser
        workflow_steps.append({'step': 'jd_parsing', 'status': 'in_progress', 'message': 'Sending JD to JD Parser Agent...'})
        
        jd_payload = {}
        if jd_url:
            jd_payload['jd_url'] = jd_url
        else:
            jd_payload['jd_text'] = jd_text
            
        jd_response = requests.post(f"{JD_PARSER_URL}/parse", 
                                   headers={'Content-Type': 'application/json'},
                                   json=jd_payload, timeout=60)
        
        if jd_response.status_code != 200:
            workflow_steps.append({'step': 'jd_parsing', 'status': 'failed', 'message': 'JD parsing failed'})
            return jsonify({'success': False, 'error': 'JD parsing failed', 'workflow_steps': workflow_steps})
        
        jd_data = jd_response.json()
        if not jd_data.get('success'):
            workflow_steps.append({'step': 'jd_parsing', 'status': 'failed', 'message': jd_data.get('error', 'JD parsing failed')})
            return jsonify({'success': False, 'error': jd_data.get('error', 'JD parsing failed'), 'workflow_steps': workflow_steps})
        
        workflow_steps.append({'step': 'jd_parsing', 'status': 'completed', 'message': 'JD parsed successfully'})
        
        # Step 4: Perform Gap Analysis
        workflow_steps.append({'step': 'gap_analysis', 'status': 'in_progress', 'message': 'Performing intelligent gap analysis...'})
        
        gap_result = agent.analyze_cv_jd_gap(cv_data['result'], jd_data['result'])
        
        workflow_steps.append({'step': 'gap_analysis', 'status': 'completed', 'message': 'Gap analysis completed'})
        workflow_steps.append({'step': 'complete', 'status': 'completed', 'message': 'Full workflow completed successfully'})
        
        # Convert result to dictionary for JSON response
        response_data = {
            'success': True,
            'workflow_steps': workflow_steps,
            'cv_data': cv_data['result'],
            'jd_data': jd_data['result'],
            'gap_analysis': {
                'cv_highlighted': gap_result.cv_highlighted,
                'jd_highlighted': gap_result.jd_highlighted,
                'match_score': {
                    'overall_score': gap_result.match_score.overall_score,
                    'skills_score': gap_result.match_score.skills_score,
                    'experience_score': gap_result.match_score.experience_score,
                    'education_score': gap_result.match_score.education_score,
                    'qualifications_score': gap_result.match_score.qualifications_score,
                    'recommendations': gap_result.match_score.recommendations,
                    'strengths': gap_result.match_score.strengths,
                    'gaps': gap_result.match_score.gaps
                },
                'analysis_notes': gap_result.analysis_notes,
                'timestamp': gap_result.timestamp
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        workflow_steps.append({'step': 'error', 'status': 'failed', 'message': f'Workflow error: {str(e)}'})
        print(f"❌ Workflow error: {str(e)}")
        return jsonify({'success': False, 'error': str(e), 'workflow_steps': workflow_steps})

if __name__ == '__main__':
    print(f"🚀 Starting Gap Analyst Agent Testing Interface...")
    print(f"🤖 Agent Version: {agent.version}")
    print(f"🧠 Model: {agent.model_name}")
    print(f"🔗 Content Matcher URL: {CONTENT_MATCHER_URL}")
    print(f"🔗 CV Parser URL: {CV_PARSER_URL}")
    print(f"🔗 JD Parser URL: {JD_PARSER_URL}")
    print(f"📊 Anthropic API: {'✅ Configured' if agent.anthropic_api_key else '❌ Not configured'}")
    print(f"🌐 Interface will be available at: http://localhost:5006")
    print("=" * 60)
    
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    # Copy .env from JD parser if it doesn't exist
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        jd_env_file = Path(__file__).parent.parent / 'jd_parser' / '.env'
        if jd_env_file.exists():
            import shutil
            shutil.copy(jd_env_file, env_file)
            print(f"📄 Copied environment file from JD Parser")
    
    app.run(debug=True, host='0.0.0.0', port=5006)