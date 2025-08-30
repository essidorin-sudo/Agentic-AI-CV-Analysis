#!/usr/bin/env python3
"""
LLM integration for JD Parser Agent.
Handles communication with various LLM providers for job description parsing.
"""

import os
from typing import Dict, Any

# Try importing core utilities
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
    from core.utils import create_llm_client, GracefulDegradation
    print("✅ Using core LLM utilities")
except ImportError:
    create_llm_client = None
    GracefulDegradation = None
    print("⚠️  Core LLM utilities not available")

# Import local API clients
try:
    from .api_clients import JDAnthropicAPIClient, JDOpenAIAPIClient, JDJSONResponseParser
except ImportError:
    from api_clients import JDAnthropicAPIClient, JDOpenAIAPIClient, JDJSONResponseParser


class JDParserLLMClient:
    """LLM client specifically for JD parsing operations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_provider = config.get('llm_provider', 'anthropic')
        self.model_name = config.get('model_name', 'claude-3-5-sonnet-20241022')
        
        # Initialize clients
        self._init_llm_clients()
    
    def _init_llm_clients(self):
        """Initialize LLM clients based on configuration."""
        
        # Try to use core utilities if available
        if create_llm_client:
            try:
                self.standard_client = create_llm_client(self.model_name)
                print("✅ Using standardized LLM client")
                return
            except Exception as e:
                print(f"⚠️  Could not create standardized client: {e}")
        
        # Initialize direct API clients
        self._init_api_clients()
    
    def _init_api_clients(self):
        """Initialize direct API clients."""
        
        # Anthropic client
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_api_key:
            self.anthropic_client = JDAnthropicAPIClient(
                anthropic_api_key, self.model_name, self.config
            )
            print("✅ Anthropic API client initialized")
        else:
            self.anthropic_client = None
        
        # OpenAI client
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            try:
                import openai
                client = openai.OpenAI(api_key=openai_api_key)
                self.openai_client = JDOpenAIAPIClient(client, self.model_name, self.config)
                print("✅ OpenAI API client initialized")
            except Exception as e:
                print(f"⚠️  OpenAI client failed: {e}")
                self.openai_client = None
        else:
            self.openai_client = None
    
    def parse_jd_with_llm(self, jd_text: str, parsing_prompt: str) -> Dict[str, Any]:
        """Parse JD using configured LLM provider."""
        
        # Try standardized client first
        if hasattr(self, 'standard_client'):
            try:
                response = self.standard_client.generate_response(
                    prompt=f"{parsing_prompt}\n\n{jd_text}",
                    max_tokens=self.config.get('max_tokens', 4000),
                    temperature=self.config.get('temperature', 0.1)
                )
                
                if response.success:
                    return JDJSONResponseParser.parse_json_response(response.content)
                else:
                    print(f"⚠️  Standardized client failed: {response.error_message}")
            except Exception as e:
                print(f"⚠️  Standardized client error: {e}")
        
        # Try direct API calls
        try:
            if self.llm_provider == 'anthropic' and self.anthropic_client:
                content = self.anthropic_client.call_api(jd_text, parsing_prompt)
                return JDJSONResponseParser.parse_json_response(content)
            elif self.llm_provider == 'openai' and self.openai_client:
                content = self.openai_client.call_api(jd_text, parsing_prompt)
                return JDJSONResponseParser.parse_json_response(content)
        except Exception as e:
            print(f"❌ API call error: {e}")
        
        # Use graceful degradation if available
        if GracefulDegradation:
            print("⚠️  Using fallback parsing - LLM unavailable")
            return GracefulDegradation.fallback_jd_parsing(jd_text)
        else:
            raise ValueError("No LLM provider available and no fallback configured")