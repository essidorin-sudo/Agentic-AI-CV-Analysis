#!/usr/bin/env python3

from flask import request, session
from models import db, AnalyticsEvent, SystemUsage, User
from datetime import datetime, date
import uuid
import json

class AnalyticsTracker:
    """Comprehensive analytics tracking system"""
    
    @staticmethod
    def get_session_id():
        """Get or create session ID for tracking"""
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        return session['session_id']
    
    @staticmethod
    def track_event(event_type, event_action, event_label=None, 
                   page_url=None, page_title=None, element_id=None, 
                   metadata=None, user_id=None):
        """
        Track user interaction event
        
        Args:
            event_type: Type of event ('click', 'upload', 'navigation', 'system')
            event_action: Specific action ('button_click', 'file_upload', 'page_view')
            event_label: Additional context
            page_url: Current page URL
            page_title: Current page title
            element_id: HTML element ID that was interacted with
            metadata: Additional event data as dict
            user_id: User ID if authenticated
        """
        try:
            event = AnalyticsEvent(
                user_id=user_id,
                session_id=AnalyticsTracker.get_session_id(),
                event_type=event_type,
                event_action=event_action,
                event_label=event_label,
                page_url=page_url,
                page_title=page_title,
                element_id=element_id,
                event_metadata=metadata,
                user_agent=request.headers.get('User-Agent'),
                ip_address=request.remote_addr
            )
            
            db.session.add(event)
            db.session.commit()
            
            print(f"📊 Analytics: {event_type}.{event_action} - {event_label}")
            
        except Exception as e:
            print(f"❌ Analytics tracking error: {e}")
            db.session.rollback()
    
    @staticmethod
    def track_click(element_id, event_label=None, page_url=None, user_id=None):
        """Track button/link clicks"""
        AnalyticsTracker.track_event(
            event_type='click',
            event_action='button_click',
            event_label=event_label,
            element_id=element_id,
            page_url=page_url,
            user_id=user_id
        )
    
    @staticmethod
    def track_upload(file_type, file_size=None, user_id=None):
        """Track file uploads"""
        AnalyticsTracker.track_event(
            event_type='upload',
            event_action='file_upload',
            event_label=file_type,
            metadata={'file_size': file_size},
            user_id=user_id
        )
    
    @staticmethod
    def track_comparison(cv_id, jd_id, match_score=None, user_id=None):
        """Track CV-JD comparisons"""
        AnalyticsTracker.track_event(
            event_type='analysis',
            event_action='cv_jd_comparison',
            event_label='gap_analysis',
            metadata={
                'cv_id': cv_id,
                'jd_id': jd_id,
                'match_score': match_score
            },
            user_id=user_id
        )
    
    @staticmethod
    def track_agent_call(agent_name, execution_time=None, success=True, user_id=None):
        """Track AI agent API calls"""
        AnalyticsTracker.track_event(
            event_type='system',
            event_action='agent_call',
            event_label=agent_name,
            metadata={
                'execution_time': execution_time,
                'success': success
            },
            user_id=user_id
        )
    
    @staticmethod
    def track_page_view(page_url, page_title, user_id=None):
        """Track page navigation"""
        AnalyticsTracker.track_event(
            event_type='navigation',
            event_action='page_view',
            page_url=page_url,
            page_title=page_title,
            user_id=user_id
        )
    
    @staticmethod
    def track_user_auth(action, user_id=None, success=True):
        """Track authentication events"""
        AnalyticsTracker.track_event(
            event_type='auth',
            event_action=action,  # 'login', 'logout', 'register'
            metadata={'success': success},
            user_id=user_id
        )
    
    @staticmethod
    def update_daily_usage():
        """Update daily usage statistics"""
        try:
            today = date.today()
            
            # Get or create today's usage record
            usage = SystemUsage.query.filter_by(date=today).first()
            if not usage:
                usage = SystemUsage(date=today)
                db.session.add(usage)
            
            # Count users
            usage.total_users = User.query.count()
            usage.active_users = User.query.filter(
                User.last_login >= datetime.combine(today, datetime.min.time())
            ).count()
            
            # Count new registrations today
            usage.new_registrations = User.query.filter(
                User.created_at >= datetime.combine(today, datetime.min.time())
            ).count()
            
            # Count events today
            today_start = datetime.combine(today, datetime.min.time())
            
            usage.total_cv_uploads = AnalyticsEvent.query.filter(
                AnalyticsEvent.timestamp >= today_start,
                AnalyticsEvent.event_action == 'file_upload',
                AnalyticsEvent.event_label == 'cv'
            ).count()
            
            usage.total_jd_submissions = AnalyticsEvent.query.filter(
                AnalyticsEvent.timestamp >= today_start,
                AnalyticsEvent.event_action == 'jd_submission'
            ).count()
            
            usage.total_comparisons = AnalyticsEvent.query.filter(
                AnalyticsEvent.timestamp >= today_start,
                AnalyticsEvent.event_action == 'cv_jd_comparison'
            ).count()
            
            # Count agent calls
            usage.cv_parser_calls = AnalyticsEvent.query.filter(
                AnalyticsEvent.timestamp >= today_start,
                AnalyticsEvent.event_action == 'agent_call',
                AnalyticsEvent.event_label == 'cv_parser'
            ).count()
            
            usage.jd_parser_calls = AnalyticsEvent.query.filter(
                AnalyticsEvent.timestamp >= today_start,
                AnalyticsEvent.event_action == 'agent_call',
                AnalyticsEvent.event_label == 'jd_parser'
            ).count()
            
            usage.gap_analyst_calls = AnalyticsEvent.query.filter(
                AnalyticsEvent.timestamp >= today_start,
                AnalyticsEvent.event_action == 'agent_call',
                AnalyticsEvent.event_label == 'gap_analyst'
            ).count()
            
            db.session.commit()
            print(f"📈 Updated daily usage stats for {today}")
            
        except Exception as e:
            print(f"❌ Daily usage update error: {e}")
            db.session.rollback()

class AnalyticsQueries:
    """Analytics query helpers for admin dashboard"""
    
    @staticmethod
    def get_user_activity_summary(days=30):
        """Get user activity summary for last N days"""
        from sqlalchemy import func
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Most active users
        user_activity = db.session.query(
            User.id,
            User.email,
            User.first_name,
            User.last_name,
            func.count(AnalyticsEvent.id).label('event_count')
        ).join(AnalyticsEvent).filter(
            AnalyticsEvent.timestamp >= cutoff_date
        ).group_by(User.id).order_by(
            func.count(AnalyticsEvent.id).desc()
        ).limit(10).all()
        
        return [
            {
                'user_id': row.id,
                'email': row.email,
                'name': f"{row.first_name} {row.last_name}",
                'event_count': row.event_count
            }
            for row in user_activity
        ]
    
    @staticmethod
    def get_event_frequency(event_type=None, days=7):
        """Get event frequency by day"""
        from sqlalchemy import func
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.session.query(
            func.date(AnalyticsEvent.timestamp).label('date'),
            func.count(AnalyticsEvent.id).label('count')
        ).filter(AnalyticsEvent.timestamp >= cutoff_date)
        
        if event_type:
            query = query.filter(AnalyticsEvent.event_type == event_type)
        
        results = query.group_by(
            func.date(AnalyticsEvent.timestamp)
        ).order_by('date').all()
        
        return [
            {
                'date': row.date.isoformat(),
                'count': row.count
            }
            for row in results
        ]
    
    @staticmethod
    def get_popular_actions(limit=10):
        """Get most popular user actions"""
        from sqlalchemy import func
        
        results = db.session.query(
            AnalyticsEvent.event_action,
            func.count(AnalyticsEvent.id).label('count')
        ).group_by(
            AnalyticsEvent.event_action
        ).order_by(
            func.count(AnalyticsEvent.id).desc()
        ).limit(limit).all()
        
        return [
            {
                'action': row.event_action,
                'count': row.count
            }
            for row in results
        ]