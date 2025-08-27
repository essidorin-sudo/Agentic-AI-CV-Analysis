#!/usr/bin/env python3
"""
Content Matcher Agent - CV and JD Analysis Orchestrator

This agent orchestrates the interaction between JD Parser and CV Parser agents,
providing side-by-side content analysis and comparison capabilities.
"""

import json
import requests
import os
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"🔧 Loaded environment from {env_path}")
except ImportError:
    print("📝 python-dotenv not installed, using system environment variables")


@dataclass
class MatchResult:
    """Result of content matching analysis"""
    cv_data: Dict
    jd_data: Dict
    cv_success: bool
    jd_success: bool
    cv_error: Optional[str] = None
    jd_error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class ContentMatcherAgent:
    """
    Content Matcher Agent - Orchestrates CV and JD analysis
    
    This agent coordinates between the JD Parser and CV Parser agents to provide
    unified analysis and comparison capabilities.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.version = "1.0.0"
        self.agent_id = f"content_matcher_{datetime.now().strftime('%Y%m%d')}"
        
        # Agent endpoints
        self.jd_parser_url = self.config.get('jd_parser_url', 'http://localhost:5003')
        self.cv_parser_url = self.config.get('cv_parser_url', 'http://localhost:5004')
        
        print(f"🤖 Content Matcher Agent v{self.version} initialized")
        print(f"📍 JD Parser: {self.jd_parser_url}")
        print(f"📍 CV Parser: {self.cv_parser_url}")
    
    def process_job_description(self, jd_text: str = None, jd_url: str = None) -> Tuple[bool, Dict, Optional[str]]:
        """
        Send job description to JD Parser agent
        
        Args:
            jd_text: Job description text
            jd_url: Job description URL
            
        Returns:
            Tuple of (success, data, error_message)
        """
        
        try:
            print(f"📋 Sending JD to parser agent...")
            
            # Prepare request data
            request_data = {}
            if jd_url:
                request_data['jd_url'] = jd_url
            elif jd_text:
                request_data['jd_text'] = jd_text
            else:
                return False, {}, "No job description provided"
            
            # Send to JD Parser
            response = requests.post(
                f"{self.jd_parser_url}/parse",
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ JD parsing successful")
                    return True, data['result'], None
                else:
                    error_msg = data.get('error', 'Unknown error')
                    print(f"❌ JD parsing failed: {error_msg}")
                    return False, {}, error_msg
            else:
                error_msg = f"JD Parser responded with status {response.status_code}"
                print(f"❌ {error_msg}")
                return False, {}, error_msg
                
        except requests.exceptions.ConnectionError:
            error_msg = f"Could not connect to JD Parser at {self.jd_parser_url}"
            print(f"❌ {error_msg}")
            return False, {}, error_msg
        except requests.exceptions.Timeout:
            error_msg = "JD Parser request timed out"
            print(f"❌ {error_msg}")
            return False, {}, error_msg
        except Exception as e:
            error_msg = f"JD parsing error: {str(e)}"
            print(f"❌ {error_msg}")
            return False, {}, error_msg
    
    def process_cv_text(self, cv_text: str) -> Tuple[bool, Dict, Optional[str]]:
        """
        Send CV text to CV Parser agent
        
        Args:
            cv_text: CV content as text
            
        Returns:
            Tuple of (success, data, error_message)
        """
        
        try:
            print(f"📄 Sending CV text to parser agent...")
            
            response = requests.post(
                f"{self.cv_parser_url}/parse",
                json={'cv_text': cv_text},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ CV parsing successful")
                    return True, data['result'], None
                else:
                    error_msg = data.get('error', 'Unknown error')
                    print(f"❌ CV parsing failed: {error_msg}")
                    return False, {}, error_msg
            else:
                error_msg = f"CV Parser responded with status {response.status_code}"
                print(f"❌ {error_msg}")
                return False, {}, error_msg
                
        except requests.exceptions.ConnectionError:
            error_msg = f"Could not connect to CV Parser at {self.cv_parser_url}"
            print(f"❌ {error_msg}")
            return False, {}, error_msg
        except requests.exceptions.Timeout:
            error_msg = "CV Parser request timed out"
            print(f"❌ {error_msg}")
            return False, {}, error_msg
        except Exception as e:
            error_msg = f"CV parsing error: {str(e)}"
            print(f"❌ {error_msg}")
            return False, {}, error_msg
    
    def process_cv_file(self, file_content: bytes, filename: str) -> Tuple[bool, Dict, Optional[str]]:
        """
        Send CV file to CV Parser agent
        
        Args:
            file_content: CV file content as bytes
            filename: Original filename
            
        Returns:
            Tuple of (success, data, error_message)
        """
        
        try:
            print(f"📎 Sending CV file ({filename}) to parser agent...")
            
            # Prepare multipart form data
            files = {'file': (filename, file_content)}
            
            response = requests.post(
                f"{self.cv_parser_url}/parse_file",
                files=files,
                timeout=60  # Longer timeout for file processing
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ CV file parsing successful")
                    return True, data['result'], None
                else:
                    error_msg = data.get('error', 'Unknown error')
                    print(f"❌ CV file parsing failed: {error_msg}")
                    return False, {}, error_msg
            else:
                error_msg = f"CV Parser responded with status {response.status_code}"
                print(f"❌ {error_msg}")
                return False, {}, error_msg
                
        except requests.exceptions.ConnectionError:
            error_msg = f"Could not connect to CV Parser at {self.cv_parser_url}"
            print(f"❌ {error_msg}")
            return False, {}, error_msg
        except requests.exceptions.Timeout:
            error_msg = "CV Parser file processing timed out"
            print(f"❌ {error_msg}")
            return False, {}, error_msg
        except Exception as e:
            error_msg = f"CV file parsing error: {str(e)}"
            print(f"❌ {error_msg}")
            return False, {}, error_msg
    
    def analyze_match(self, cv_data: Dict, jd_data: Dict) -> MatchResult:
        """
        Create a match result combining CV and JD data
        
        Args:
            cv_data: Parsed CV data
            jd_data: Parsed JD data
            
        Returns:
            MatchResult object
        """
        
        return MatchResult(
            cv_data=cv_data,
            jd_data=jd_data,
            cv_success=True,
            jd_success=True
        )
    
    def check_agents_status(self) -> Dict[str, bool]:
        """
        Check if both JD and CV parser agents are running
        
        Returns:
            Dict with agent status
        """
        
        status = {
            'jd_parser': False,
            'cv_parser': False
        }
        
        # Check JD Parser
        try:
            response = requests.get(f"{self.jd_parser_url}/", timeout=5)
            status['jd_parser'] = response.status_code == 200
        except:
            pass
        
        # Check CV Parser
        try:
            response = requests.get(f"{self.cv_parser_url}/", timeout=5)
            status['cv_parser'] = response.status_code == 200
        except:
            pass
        
        return status


# Test the agent when run directly
if __name__ == "__main__":
    print("🤖 Content Matcher Agent v1.0.0 - CV and JD Analysis Orchestrator")
    print("=" * 60)
    
    agent = ContentMatcherAgent()
    
    # Check agent status
    status = agent.check_agents_status()
    print(f"\n📊 Agent Status:")
    print(f"   JD Parser: {'✅ Online' if status['jd_parser'] else '❌ Offline'}")
    print(f"   CV Parser: {'✅ Online' if status['cv_parser'] else '❌ Offline'}")
    
    if all(status.values()):
        print("\n🎉 All agents are ready for content matching!")
    else:
        print("\n⚠️  Some agents are offline. Make sure both JD and CV parsers are running.")