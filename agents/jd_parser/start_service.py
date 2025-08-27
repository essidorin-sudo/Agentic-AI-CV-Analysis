#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_cors import CORS
from agent import JDParserAgent
import traceback

app = Flask(__name__)
CORS(app)

# Initialize the agent
agent = JDParserAgent()

@app.route('/parse', methods=['POST'])
def parse():
    try:
        data = request.get_json()
        
        # Handle both text and URL inputs
        if 'jd_text' in data:
            result = agent.parse_job_description(data['jd_text'])
            return jsonify({
                'success': True,
                'result': agent.to_dict(result),
                'agent_info': {
                    'version': agent.version,
                    'agent_id': agent.agent_id
                }
            })
        elif 'jd_url' in data:
            # URL parsing not implemented in simple service launcher
            return jsonify({'success': False, 'error': 'URL parsing not supported in this service launcher'}), 400
        else:
            return jsonify({'success': False, 'error': 'No JD text or URL provided'}), 400
            
    except Exception as e:
        print(f"Error in JD parser: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'version': agent.version})

if __name__ == '__main__':
    print("🤖 Starting JD Parser Service on port 5007...")
    app.run(host='0.0.0.0', port=5007, debug=True)