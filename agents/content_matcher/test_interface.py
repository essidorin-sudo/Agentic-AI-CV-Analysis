#!/usr/bin/env python3
"""
Content Matcher Agent - Testing Interface

Web interface for testing the Content Matcher Agent with CV upload and JD input,
displaying results side by side with status indicators.
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from flask import Flask, render_template, request, jsonify
import json
from agent import ContentMatcherAgent
import traceback

app = Flask(__name__)

# Global agent instance
matcher_agent = ContentMatcherAgent()

@app.route('/')
def index():
    """Main testing interface"""
    return render_template('test_interface.html')

@app.route('/status')
def get_status():
    """Get status of all agents"""
    try:
        status = matcher_agent.check_agents_status()
        return jsonify({
            'success': True,
            'agents': status,
            'all_online': all(status.values())
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/process_jd', methods=['POST'])
def process_job_description():
    """Process job description using JD Parser agent"""
    try:
        data = request.get_json()
        jd_text = data.get('jd_text', '').strip()
        jd_url = data.get('jd_url', '').strip()
        
        if not jd_text and not jd_url:
            return jsonify({'error': 'No job description provided'}), 400
        
        # Process with JD Parser agent
        success, result, error = matcher_agent.process_job_description(
            jd_text=jd_text if jd_text else None,
            jd_url=jd_url if jd_url else None
        )
        
        if success:
            return jsonify({
                'success': True,
                'result': result,
                'agent_info': {
                    'version': matcher_agent.version,
                    'agent_id': matcher_agent.agent_id
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': error
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/process_cv_text', methods=['POST'])
def process_cv_text():
    """Process CV text using CV Parser agent"""
    try:
        data = request.get_json()
        cv_text = data.get('cv_text', '').strip()
        
        if not cv_text:
            return jsonify({'error': 'No CV text provided'}), 400
        
        # Process with CV Parser agent
        success, result, error = matcher_agent.process_cv_text(cv_text)
        
        if success:
            return jsonify({
                'success': True,
                'result': result,
                'agent_info': {
                    'version': matcher_agent.version,
                    'agent_id': matcher_agent.agent_id
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': error
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/process_cv_file', methods=['POST'])
def process_cv_file():
    """Process CV file using CV Parser agent"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file content
        file_content = file.read()
        filename = file.filename
        
        # Process with CV Parser agent
        success, result, error = matcher_agent.process_cv_file(file_content, filename)
        
        if success:
            return jsonify({
                'success': True,
                'result': result,
                'agent_info': {
                    'version': matcher_agent.version,
                    'agent_id': matcher_agent.agent_id
                },
                'file_info': {
                    'filename': filename,
                    'size': len(file_content)
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': error
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/analyze_match', methods=['POST'])
def analyze_match():
    """Analyze match between CV and JD data"""
    try:
        data = request.get_json()
        cv_data = data.get('cv_data', {})
        jd_data = data.get('jd_data', {})
        
        if not cv_data or not jd_data:
            return jsonify({'error': 'Both CV and JD data required'}), 400
        
        # Create match analysis
        match_result = matcher_agent.analyze_match(cv_data, jd_data)
        
        return jsonify({
            'success': True,
            'match_result': {
                'cv_data': match_result.cv_data,
                'jd_data': match_result.jd_data,
                'cv_success': match_result.cv_success,
                'jd_success': match_result.jd_success,
                'timestamp': match_result.timestamp
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    print("🚀 Starting Content Matcher Agent Testing Interface...")
    print("📍 Access at: http://localhost:5005")
    print("🔧 Agent Version:", matcher_agent.version)
    
    # Check agent status on startup
    status = matcher_agent.check_agents_status()
    print(f"\n📊 Dependent Agent Status:")
    print(f"   JD Parser (port 5003): {'✅ Online' if status['jd_parser'] else '❌ Offline'}")
    print(f"   CV Parser (port 5004): {'✅ Online' if status['cv_parser'] else '❌ Offline'}")
    
    if not all(status.values()):
        print("\n⚠️  Warning: Some dependent agents are offline!")
        print("   Make sure both JD Parser and CV Parser agents are running")
    
    app.run(debug=True, host='0.0.0.0', port=5005)