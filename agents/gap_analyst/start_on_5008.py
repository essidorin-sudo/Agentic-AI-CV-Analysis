#!/usr/bin/env python3
"""
Gap Analyst Agent - Production Service Starter
Starts Gap Analyst on port 5008 for production system integration
"""

import os
import json
from flask import Flask, request, jsonify
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

@app.route('/status')
def status():
    """Check agent status"""
    return jsonify({
        'success': True,
        'agent_version': agent.version,
        'model': agent.model_name,
        'anthropic_configured': bool(agent.anthropic_api_key),
        'service': 'gap_analyst'
    })

@app.route('/analyze_gap', methods=['POST'])
def analyze_gap():
    """Perform gap analysis between CV and JD data"""
    try:
        data = request.get_json()
        cv_data = data.get('cv_data', {})
        jd_data = data.get('jd_data', {})
        
        print(f"🔍 Received gap analysis request")
        print(f"📋 CV data type: {type(cv_data)}, value: {cv_data}")
        print(f"📋 JD data type: {type(jd_data)}, value: {jd_data}")
        
        if cv_data is None or jd_data is None or not cv_data or not jd_data:
            print(f"❌ Invalid data - CV: {cv_data}, JD: {jd_data}")
            return jsonify({'success': False, 'error': 'Both CV and JD data are required'})
        
        print(f"🔍 Received gap analysis request")
        print(f"📄 CV: {cv_data.get('full_name', 'Unknown')}")
        print(f"📋 JD: {jd_data.get('job_title', 'Unknown')}")
        
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
        
        print(f"✅ Gap analysis completed. Overall score: {result.match_score.overall_score:.1f}%")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Gap analysis error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print(f"🚀 Starting Gap Analyst Agent Production Service...")
    print(f"🤖 Agent Version: {agent.version}")
    print(f"🧠 Model: {agent.model_name}")
    print(f"📊 Anthropic API: {'✅ Configured' if agent.anthropic_api_key else '❌ Not configured'}")
    print(f"🌐 Production service on port 5008")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5008)