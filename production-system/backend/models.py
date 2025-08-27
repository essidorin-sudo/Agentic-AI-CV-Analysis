#!/usr/bin/env python3

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
import uuid

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    """User account model"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    cvs = db.relationship('CV', backref='user', lazy=True, cascade='all, delete-orphan')
    job_descriptions = db.relationship('JobDescription', backref='user', lazy=True, cascade='all, delete-orphan')
    comparisons = db.relationship('Comparison', backref='user', lazy=True, cascade='all, delete-orphan')
    analytics_events = db.relationship('AnalyticsEvent', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class CV(db.Model):
    """CV/Resume model"""
    __tablename__ = 'cvs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    content_type = db.Column(db.String(100))
    parsed_data = db.Column(db.JSON)  # Parsed CV content from CV Parser Agent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    comparisons = db.relationship('Comparison', backref='cv', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'content_type': self.content_type,
            'parsed_data': self.parsed_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class JobDescription(db.Model):
    """Job Description model"""
    __tablename__ = 'job_descriptions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255))
    source_url = db.Column(db.Text)  # URL if scraped from web
    raw_text = db.Column(db.Text, nullable=False)
    parsed_data = db.Column(db.JSON)  # Parsed JD content from JD Parser Agent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    comparisons = db.relationship('Comparison', backref='job_description', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'source_url': self.source_url,
            'raw_text': self.raw_text,
            'parsed_data': self.parsed_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Comparison(db.Model):
    """CV-JD Comparison model"""
    __tablename__ = 'comparisons'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    cv_id = db.Column(db.String(36), db.ForeignKey('cvs.id'), nullable=False)
    job_description_id = db.Column(db.String(36), db.ForeignKey('job_descriptions.id'), nullable=False)
    
    # Gap Analysis Results
    gap_analysis = db.Column(db.JSON)  # Full gap analysis from Gap Analyst Agent
    match_score = db.Column(db.Float)  # Overall match score (0-100)
    highlighted_content = db.Column(db.JSON)  # Color-coded highlighting data
    
    # Status tracking
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'cv_id': self.cv_id,
            'job_description_id': self.job_description_id,
            'gap_analysis': self.gap_analysis,
            'match_score': self.match_score,
            'highlighted_content': self.highlighted_content,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class AnalyticsEvent(db.Model):
    """Analytics tracking model for user interactions"""
    __tablename__ = 'analytics_events'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)  # Null for anonymous events
    session_id = db.Column(db.String(36), nullable=False)  # Track user sessions
    
    # Event details
    event_type = db.Column(db.String(100), nullable=False)  # 'click', 'upload', 'comparison', etc.
    event_action = db.Column(db.String(100), nullable=False)  # 'button_click', 'file_upload', 'run_analysis'
    event_label = db.Column(db.String(200))  # Additional context
    
    # Page/location tracking
    page_url = db.Column(db.String(500))
    page_title = db.Column(db.String(200))
    element_id = db.Column(db.String(100))  # HTML element ID that was interacted with
    
    # Additional data
    event_metadata = db.Column(db.JSON)  # Store additional event data
    
    # Timing
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Browser/device info
    user_agent = db.Column(db.String(500))
    ip_address = db.Column(db.String(45))  # IPv6 support
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'event_type': self.event_type,
            'event_action': self.event_action,
            'event_label': self.event_label,
            'page_url': self.page_url,
            'page_title': self.page_title,
            'element_id': self.element_id,
            'metadata': self.event_metadata,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'user_agent': self.user_agent,
            'ip_address': self.ip_address
        }

class SystemUsage(db.Model):
    """System usage statistics"""
    __tablename__ = 'system_usage'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = db.Column(db.Date, nullable=False, index=True)
    
    # Daily metrics
    total_users = db.Column(db.Integer, default=0)
    active_users = db.Column(db.Integer, default=0)
    new_registrations = db.Column(db.Integer, default=0)
    total_cv_uploads = db.Column(db.Integer, default=0)
    total_jd_submissions = db.Column(db.Integer, default=0)
    total_comparisons = db.Column(db.Integer, default=0)
    
    # Agent usage
    cv_parser_calls = db.Column(db.Integer, default=0)
    jd_parser_calls = db.Column(db.Integer, default=0)
    gap_analyst_calls = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'total_users': self.total_users,
            'active_users': self.active_users,
            'new_registrations': self.new_registrations,
            'total_cv_uploads': self.total_cv_uploads,
            'total_jd_submissions': self.total_jd_submissions,
            'total_comparisons': self.total_comparisons,
            'cv_parser_calls': self.cv_parser_calls,
            'jd_parser_calls': self.jd_parser_calls,
            'gap_analyst_calls': self.gap_analyst_calls,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }