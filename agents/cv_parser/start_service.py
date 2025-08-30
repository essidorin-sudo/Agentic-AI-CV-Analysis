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

@app.route('/parse_file', methods=['POST'])
def parse_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Read file content
        file_content = file.read()
        filename = file.filename
        
        # For text files, extract text and use regular text parsing
        if filename.lower().endswith(('.txt', '.text')):
            try:
                # Decode text content
                cv_text = file_content.decode('utf-8')
                result = agent.parse_cv(cv_text)
                print(f"✅ Text file processed successfully: {filename}")
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    cv_text = file_content.decode('latin-1')
                    result = agent.parse_cv(cv_text)
                    print(f"✅ Text file processed with latin-1 encoding: {filename}")
                except Exception as e:
                    print(f"❌ Failed to decode text file: {e}")
                    return jsonify({'success': False, 'error': f'Failed to decode text file: {str(e)}'}), 400
        else:
            # For binary files (PDF, DOC, DOCX), use file parsing
            result = agent.parse_cv_file(file_content, filename)
        
        return jsonify({
            'success': True,
            'result': agent.to_dict(result),
            'agent_info': {
                'version': agent.version,
                'agent_id': agent.agent_id
            },
            'file_info': {
                'filename': filename,
                'size': len(file_content)
            }
        })
        
    except Exception as e:
        print(f"Error parsing CV file: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'version': agent.version})

if __name__ == '__main__':
    print("🤖 Starting CV Parser Service on port 5005...")
    app.run(host='0.0.0.0', port=5005, debug=True)