#!/usr/bin/env python3

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import uuid
import requests
from datetime import datetime, timedelta
import json

from models import db, User, CV, JobDescription, Comparison, AnalyticsEvent
from analytics import AnalyticsTracker, AnalyticsQueries

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cv_analyzer.db'  # Change to PostgreSQL for production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
CORS(app)
jwt = JWTManager(app)
db.init_app(app)

# Agent service URLs (adjust ports as needed)
AGENT_URLS = {
    'cv_parser': 'http://localhost:5005',
    'jd_parser': 'http://localhost:5007',
    'gap_analyst': 'http://localhost:5008'
}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def apply_highlighting_instructions(content_with_addresses: str, highlighting_instructions: list) -> str:
    """
    Apply highlighting instructions to content with invisible address markup.
    
    Args:
        content_with_addresses: Original content with address markup (e.g., <!--cv_section_5-->text<!--/cv_section_5-->)
        highlighting_instructions: List of dicts with 'address', 'class', and 'reason'
        
    Returns:
        HTML content with highlighting applied, preserving original formatting
    """
    import re
    import html
    
    if not highlighting_instructions:
        # If no highlighting instructions, just remove the address markup and return content
        clean_content = re.sub(r'<!--[^>]+-->', '', content_with_addresses)
        # Escape HTML entities but preserve structure
        escaped_content = html.escape(clean_content)
        return f'<pre class="cv-content">{escaped_content}</pre>'
    
    result_content = content_with_addresses
    
    # Apply each highlighting instruction
    for instruction in highlighting_instructions:
        address = instruction.get('address', '')
        css_class = instruction.get('class', '')
        reason = instruction.get('reason', '')
        
        if not address or not css_class:
            continue
            
        # Find the content between the address markers
        pattern = f'<!--{address}-->(.*?)<!--/{address}-->'
        
        def replace_with_highlight(match):
            original_text = match.group(1)
            # DON'T escape HTML - preserve original formatting
            return f'<span class="{css_class}" title="{html.escape(reason)}">{original_text}</span>'
        
        result_content = re.sub(pattern, replace_with_highlight, result_content, flags=re.DOTALL)
    
    # Remove any remaining address markup
    result_content = re.sub(r'<!--[^>]+-->', '', result_content)
    
    print(f"🎨 Applied {len(highlighting_instructions)} highlighting instructions")
    
    # Use <pre> to preserve formatting properly and add custom CSS class
    return f'<pre class="cv-content highlighted-content">{result_content}</pre>'

# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Track registration
        AnalyticsTracker.track_user_auth('register', user.id, success=True)
        
        # Create JWT token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        AnalyticsTracker.track_user_auth('register', success=False)
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            AnalyticsTracker.track_user_auth('login', success=False)
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is disabled'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Track login
        AnalyticsTracker.track_user_auth('login', user.id, success=True)
        
        # Create JWT token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# CV MANAGEMENT ROUTES
# =============================================================================

@app.route('/api/cvs', methods=['GET'])
@jwt_required()
def get_cvs():
    """Get all CVs for current user"""
    try:
        user_id = get_jwt_identity()
        cvs = CV.query.filter_by(user_id=user_id).order_by(CV.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'cvs': [cv.to_dict() for cv in cvs]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cvs/upload', methods=['POST'])
@jwt_required()
def upload_cv():
    """Upload and parse CV"""
    try:
        user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Track upload
        AnalyticsTracker.track_upload('cv', file_size=os.path.getsize(file_path), user_id=user_id)
        
        # Parse CV using CV Parser Agent
        try:
            # Extract text from file first
            cv_text = ""
            if file.content_type == 'application/pdf':
                # Extract text from PDF using PyPDF2
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        cv_text = ""
                        for page in pdf_reader.pages:
                            cv_text += page.extract_text() + "\n"
                        cv_text = cv_text.strip()
                        if not cv_text:
                            cv_text = f"PDF file uploaded but text extraction failed: {filename}"
                except ImportError:
                    # Fallback if PyPDF2 not available
                    cv_text = f"PDF file uploaded (install PyPDF2 for text extraction): {filename}"
                except Exception as e:
                    cv_text = f"PDF file uploaded (extraction error: {str(e)}): {filename}"
            else:
                # For text files, read directly
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    cv_text = f.read()
            
            # Send text to CV Parser as JSON
            cv_data = {'cv_text': cv_text}
            response = requests.post(f"{AGENT_URLS['cv_parser']}/parse", json=cv_data)
                
            if response.status_code == 200:
                cv_response = response.json()
                if cv_response.get('success') and cv_response.get('result'):
                    parsed_data = cv_response['result']
                else:
                    parsed_data = None
                AnalyticsTracker.track_agent_call('cv_parser', success=True, user_id=user_id)
            else:
                parsed_data = None
                AnalyticsTracker.track_agent_call('cv_parser', success=False, user_id=user_id)
                
        except Exception as e:
            print(f"CV Parser error: {e}")
            parsed_data = None
            AnalyticsTracker.track_agent_call('cv_parser', success=False, user_id=user_id)
        
        # Save CV record
        cv = CV(
            user_id=user_id,
            filename=unique_filename,
            original_filename=filename,
            file_size=os.path.getsize(file_path),
            content_type=file.content_type,
            parsed_data=parsed_data
        )
        
        db.session.add(cv)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'CV uploaded and parsed successfully',
            'cv': cv.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cvs/<cv_id>', methods=['DELETE'])
@jwt_required()
def delete_cv(cv_id):
    """Delete CV"""
    try:
        user_id = get_jwt_identity()
        cv = CV.query.filter_by(id=cv_id, user_id=user_id).first()
        
        if not cv:
            return jsonify({'error': 'CV not found'}), 404
        
        # Delete file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], cv.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Track deletion
        AnalyticsTracker.track_event('delete', 'cv_delete', cv_id, user_id=user_id)
        
        db.session.delete(cv)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'CV deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# JOB DESCRIPTION ROUTES
# =============================================================================

@app.route('/api/job-descriptions', methods=['GET'])
@jwt_required()
def get_job_descriptions():
    """Get all job descriptions for current user"""
    try:
        user_id = get_jwt_identity()
        jds = JobDescription.query.filter_by(user_id=user_id).order_by(JobDescription.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'job_descriptions': [jd.to_dict() for jd in jds]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/job-descriptions', methods=['POST'])
@jwt_required()
def create_job_description():
    """Create job description from text or URL"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        jd_text = data.get('text', '').strip()
        jd_url = data.get('url', '').strip()
        title = data.get('title', '').strip()
        company = data.get('company', '').strip()
        
        if not jd_text and not jd_url:
            return jsonify({'error': 'Either text or URL is required'}), 400
        
        # Parse JD using JD Parser Agent
        try:
            if jd_url:
                print(f"🌐 Sending JD URL to parser: {jd_url}")
                response = requests.post(f"{AGENT_URLS['jd_parser']}/parse", json={'jd_url': jd_url})
            else:
                print(f"📝 Sending JD text to parser: {jd_text[:100]}...")
                response = requests.post(f"{AGENT_URLS['jd_parser']}/parse", json={'jd_text': jd_text})
                
            print(f"🔍 JD Parser response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                parsed_data = result.get('result')
                print(f"🔍 JD parsed_data: {parsed_data is not None}")
                raw_text = parsed_data.get('raw_text', jd_text) if parsed_data else jd_text
                AnalyticsTracker.track_agent_call('jd_parser', success=True, user_id=user_id)
            else:
                print(f"❌ JD Parser failed with status {response.status_code}: {response.text}")
                parsed_data = None
                raw_text = jd_text
                AnalyticsTracker.track_agent_call('jd_parser', success=False, user_id=user_id)
                
        except Exception as e:
            print(f"❌ JD Parser error: {e}")
            import traceback
            print(f"📄 Traceback: {traceback.format_exc()}")
            parsed_data = None
            raw_text = jd_text
            AnalyticsTracker.track_agent_call('jd_parser', success=False, user_id=user_id)
        
        # Extract title and company from parsed data if not provided
        if parsed_data and not title:
            title = parsed_data.get('job_title', 'Untitled Job')
        if parsed_data and not company:
            company = parsed_data.get('company_name', '')
        
        # Track JD submission
        AnalyticsTracker.track_event('submit', 'jd_submission', 'url' if jd_url else 'text', user_id=user_id)
        
        # Save JD record
        jd = JobDescription(
            user_id=user_id,
            title=title or 'Untitled Job',
            company=company,
            source_url=jd_url,
            raw_text=raw_text,
            parsed_data=parsed_data
        )
        
        db.session.add(jd)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Job description created successfully',
            'job_description': jd.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/job-descriptions/<jd_id>', methods=['DELETE'])
@jwt_required()
def delete_job_description(jd_id):
    """Delete job description"""
    try:
        user_id = get_jwt_identity()
        jd = JobDescription.query.filter_by(id=jd_id, user_id=user_id).first()
        
        if not jd:
            return jsonify({'error': 'Job description not found'}), 404
        
        # Track deletion
        AnalyticsTracker.track_event('delete', 'jd_delete', jd_id, user_id=user_id)
        
        db.session.delete(jd)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Job description deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# COMPARISON ROUTES
# =============================================================================

@app.route('/api/comparisons', methods=['GET'])
@jwt_required()
def get_comparisons():
    """Get all comparisons for current user"""
    try:
        user_id = get_jwt_identity()
        
        comparisons = db.session.query(Comparison).join(CV).join(JobDescription).filter(
            Comparison.user_id == user_id
        ).order_by(Comparison.created_at.desc()).all()
        
        # Include CV and JD data
        results = []
        for comp in comparisons:
            comp_dict = comp.to_dict()
            comp_dict['cv'] = comp.cv.to_dict() if comp.cv else None
            comp_dict['job_description'] = comp.job_description.to_dict() if comp.job_description else None
            results.append(comp_dict)
        
        return jsonify({
            'success': True,
            'comparisons': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/comparisons', methods=['POST'])
@jwt_required()
def create_comparison():
    """Create CV-JD comparison"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        cv_id = data.get('cv_id')
        jd_id = data.get('job_description_id')
        
        if not cv_id or not jd_id:
            return jsonify({'error': 'CV ID and Job Description ID are required'}), 400
        
        # Verify CV and JD belong to user
        cv = CV.query.filter_by(id=cv_id, user_id=user_id).first()
        jd = JobDescription.query.filter_by(id=jd_id, user_id=user_id).first()
        
        if not cv or not jd:
            return jsonify({'error': 'CV or Job Description not found'}), 404
            
        # Ensure data is properly loaded from database
        db.session.refresh(cv)
        db.session.refresh(jd)
        
        # Validate that CV and JD have parsed data
        if not cv.parsed_data or not jd.parsed_data:
            return jsonify({
                'error': 'CV or Job Description analysis not ready. Please wait a moment and try again.',
                'details': {
                    'cv_ready': cv.parsed_data is not None,
                    'jd_ready': jd.parsed_data is not None
                }
            }), 400
        
        # Create comparison record
        comparison = Comparison(
            user_id=user_id,
            cv_id=cv_id,
            job_description_id=jd_id,
            status='processing'
        )
        
        db.session.add(comparison)
        db.session.commit()
        
        # Run Gap Analysis
        try:
            # Minimal redaction only when content exceeds 10,000 characters
            def redact_cv_content(parsed_data):
                """Minimal redaction of CV content only if over 10,000 characters"""
                if not parsed_data or not parsed_data.get('raw_text'):
                    return parsed_data
                
                raw_text = parsed_data['raw_text']
                
                # Only redact if over 6,000 characters (conservative limit for Claude output)
                if len(raw_text) <= 6000:
                    return parsed_data
                
                print(f"🔍 CV raw_text length: {len(raw_text)} chars - applying minimal redaction for Gap Analyst (>6k limit)")
                
                # Minimal redaction: remove education and name only
                redacted_text = raw_text
                
                # Remove full name if present
                if parsed_data.get('full_name'):
                    full_name = parsed_data['full_name']
                    redacted_text = redacted_text.replace(full_name, "[NAME REDACTED]")
                
                # Remove education sections by looking for common education keywords
                import re
                # Remove education sections while preserving structure
                education_patterns = [
                    r'EDUCATION.*?(?=\n[A-Z]{2,}|\n\n[A-Z]|$)',
                    r'Education.*?(?=\n[A-Z]{2,}|\n\n[A-Z]|$)',
                    r'ACADEMIC.*?(?=\n[A-Z]{2,}|\n\n[A-Z]|$)',
                    r'Academic.*?(?=\n[A-Z]{2,}|\n\n[A-Z]|$)',
                ]
                
                for pattern in education_patterns:
                    redacted_text = re.sub(pattern, '[EDUCATION SECTION REDACTED]', redacted_text, flags=re.DOTALL | re.IGNORECASE)
                
                # Copy parsed_data and replace raw_text with redacted version
                redacted_data = parsed_data.copy()
                redacted_data['raw_text'] = redacted_text
                
                print(f"🔍 Redacted CV from {len(raw_text)} to {len(redacted_text)} chars")
                return redacted_data
            
            def redact_jd_content(parsed_data):
                """Minimal redaction of JD content only if over 10,000 characters"""
                if not parsed_data or not parsed_data.get('raw_text'):
                    return parsed_data
                
                raw_text = parsed_data['raw_text']
                
                # Only redact if over 6,000 characters (conservative limit for Claude output)
                if len(raw_text) <= 6000:
                    return parsed_data
                
                print(f"🔍 JD raw_text length: {len(raw_text)} chars - applying minimal redaction for Gap Analyst (>6k limit)")
                
                # Minimal redaction: remove company-specific information only
                redacted_text = raw_text
                
                # Remove company name if present
                if parsed_data.get('company_name') and parsed_data['company_name'] != 'Unknown':
                    company_name = parsed_data['company_name']
                    redacted_text = redacted_text.replace(company_name, "[COMPANY NAME REDACTED]")
                
                # Remove common company-specific sections while preserving job requirements
                import re
                company_patterns = [
                    r'About.*?Company.*?(?=\n[A-Z]{2,}|\n\n[A-Z]|Requirements|Qualifications|$)',
                    r'Company.*?Overview.*?(?=\n[A-Z]{2,}|\n\n[A-Z]|Requirements|Qualifications|$)',
                    r'Our.*?Mission.*?(?=\n[A-Z]{2,}|\n\n[A-Z]|Requirements|Qualifications|$)',
                    r'Benefits.*?Package.*?(?=\n[A-Z]{2,}|\n\n[A-Z]|$)',
                    r'Perks.*?(?=\n[A-Z]{2,}|\n\n[A-Z]|$)',
                ]
                
                for pattern in company_patterns:
                    redacted_text = re.sub(pattern, '[COMPANY INFO REDACTED]', redacted_text, flags=re.DOTALL | re.IGNORECASE)
                
                # Copy parsed_data and replace raw_text with redacted version
                redacted_data = parsed_data.copy()
                redacted_data['raw_text'] = redacted_text
                
                print(f"🔍 Redacted JD from {len(raw_text)} to {len(redacted_text)} chars")
                return redacted_data
            
            gap_data = {
                'cv_data': redact_cv_content(cv.parsed_data),
                'jd_data': redact_jd_content(jd.parsed_data)
            }
            
            cv_len = len(gap_data['cv_data'].get('raw_text', '')) if gap_data['cv_data'] else 0
            jd_len = len(gap_data['jd_data'].get('raw_text', '')) if gap_data['jd_data'] else 0
            print(f"🔍 Sending gap_data to Gap Analyst - CV: {cv_len} chars, JD: {jd_len} chars")
            
            response = requests.post(f"{AGENT_URLS['gap_analyst']}/analyze_gap", json=gap_data, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract data from Gap Analyst response structure
                if result.get('success') and result.get('result'):
                    gap_result = result['result']
                    match_score_data = gap_result.get('match_score', {})
                    
                    # Get highlighting instructions and apply them to create full highlighted content
                    cv_highlighting = gap_result.get('cv_highlighted', [])
                    jd_highlighting = gap_result.get('jd_highlighted', [])
                    
                    print(f"🔍 Received {len(cv_highlighting)} CV highlighting instructions")
                    print(f"🔍 Received {len(jd_highlighting)} JD highlighting instructions")
                    
                    # Apply highlighting instructions to original content with addresses
                    cv_highlighted_content = apply_highlighting_instructions(cv.parsed_data.get('raw_text', ''), cv_highlighting)
                    jd_highlighted_content = apply_highlighting_instructions(jd.parsed_data.get('raw_text', ''), jd_highlighting)
                    
                    print(f"🔍 Generated CV highlighted content: {len(cv_highlighted_content)} chars")
                    print(f"🔍 Generated JD highlighted content: {len(jd_highlighted_content)} chars")
                    
                    # Update comparison with results
                    comparison.gap_analysis = gap_result
                    comparison.match_score = match_score_data.get('overall_score', 0)
                    comparison.highlighted_content = {
                        'cv_highlighted': cv_highlighted_content,
                        'jd_highlighted': jd_highlighted_content
                    }
                else:
                    comparison.gap_analysis = result
                    comparison.match_score = 0
                    
                comparison.status = 'completed'
                comparison.completed_at = datetime.utcnow()
                
                AnalyticsTracker.track_agent_call('gap_analyst', success=True, user_id=user_id)
                
            else:
                comparison.status = 'failed'
                AnalyticsTracker.track_agent_call('gap_analyst', success=False, user_id=user_id)
                
        except Exception as e:
            print(f"Gap Analyst error: {e}")
            comparison.status = 'failed'
            AnalyticsTracker.track_agent_call('gap_analyst', success=False, user_id=user_id)
        
        db.session.commit()
        
        # Track comparison
        AnalyticsTracker.track_comparison(cv_id, jd_id, comparison.match_score, user_id)
        
        comparison_dict = comparison.to_dict()
        print(f"🔍 Final comparison data being sent to frontend:")
        print(f"🔍 Match score: {comparison_dict.get('match_score')}")
        print(f"🔍 Has gap_analysis: {comparison_dict.get('gap_analysis') is not None}")
        print(f"🔍 Has highlighted_content: {comparison_dict.get('highlighted_content') is not None}")
        
        return jsonify({
            'success': True,
            'message': 'Comparison created successfully',
            'comparison': comparison_dict
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/comparisons/<comparison_id>', methods=['GET'])
@jwt_required()
def get_comparison(comparison_id):
    """Get specific comparison details"""
    try:
        user_id = get_jwt_identity()
        comparison = Comparison.query.filter_by(id=comparison_id, user_id=user_id).first()
        
        if not comparison:
            return jsonify({'error': 'Comparison not found'}), 404
        
        # Include CV and JD data
        result = comparison.to_dict()
        result['cv'] = comparison.cv.to_dict() if comparison.cv else None
        result['job_description'] = comparison.job_description.to_dict() if comparison.job_description else None
        
        return jsonify({
            'success': True,
            'comparison': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# ANALYTICS ROUTES
# =============================================================================

@app.route('/api/analytics/track', methods=['POST'])
def track_analytics():
    """Track user interaction event"""
    try:
        data = request.get_json()
        
        # Get user ID if authenticated
        user_id = None
        try:
            user_id = get_jwt_identity() if request.headers.get('Authorization') else None
        except:
            pass  # Not authenticated, that's okay for analytics
        
        AnalyticsTracker.track_event(
            event_type=data.get('event_type'),
            event_action=data.get('event_action'),
            event_label=data.get('event_label'),
            page_url=data.get('page_url'),
            page_title=data.get('page_title'),
            element_id=data.get('element_id'),
            metadata=data.get('metadata'),
            user_id=user_id
        )
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# ADMIN ROUTES
# =============================================================================

@app.route('/api/admin/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    """Get admin dashboard data"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get dashboard statistics
        from datetime import date, timedelta
        
        # Basic counts
        total_users = User.query.count()
        total_cvs = CV.query.count()
        total_jds = JobDescription.query.count()
        total_comparisons = Comparison.query.count()
        
        # Recent activity
        recent_users = User.query.filter(
            User.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Most active users
        active_users = AnalyticsQueries.get_user_activity_summary(days=30)
        
        # Event frequency
        daily_events = AnalyticsQueries.get_event_frequency(days=14)
        
        # Popular actions
        popular_actions = AnalyticsQueries.get_popular_actions()
        
        return jsonify({
            'success': True,
            'dashboard': {
                'overview': {
                    'total_users': total_users,
                    'total_cvs': total_cvs,
                    'total_job_descriptions': total_jds,
                    'total_comparisons': total_comparisons,
                    'recent_users': recent_users
                },
                'active_users': active_users,
                'daily_events': daily_events,
                'popular_actions': popular_actions
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def admin_get_users():
    """Get all users for admin"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        users = User.query.order_by(User.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'users': [user.to_dict() for user in users]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# APPLICATION SETUP
# =============================================================================

def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(email='admin@cvanalyzer.com').first()
        if not admin:
            admin = User(
                email='admin@cvanalyzer.com',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
            print("✅ Created admin user: admin@cvanalyzer.com / admin123")

if __name__ == '__main__':
    print("🚀 Starting CV Analyzer Production Backend...")
    print("📊 Analytics tracking enabled")
    print("🔐 JWT authentication enabled")
    print("🗄️  Database: SQLite (change to PostgreSQL for production)")
    
    # Initialize database
    create_tables()
    
    app.run(debug=True, host='0.0.0.0', port=8000)