#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_cors import CORS
from agent import CVParserAgent
import traceback

app = Flask(__name__)
CORS(app)

# Initialize the agent
agent = CVParserAgent()

@app.route('/parse', methods=['POST'])
def parse():
    try:
        data = request.get_json()
        
        # Handle both text and file inputs
        if 'cv_text' in data:
            result = agent.parse_cv(data['cv_text'])
            return jsonify({
                'success': True,
                'result': agent.to_dict(result),
                'agent_info': {
                    'version': agent.version,
                    'agent_id': agent.agent_id
                }
            })
        else:
            return jsonify({'success': False, 'error': 'No CV text provided'}), 400
            
    except Exception as e:
        print(f"Error in CV parser: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'version': agent.version})

if __name__ == '__main__':
    print("🤖 Starting CV Parser Service on port 5005...")
    app.run(host='0.0.0.0', port=5005, debug=True)