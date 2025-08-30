#!/usr/bin/env python3
"""
JD Parser Agent LLM Core Module

Core LLM integration methods for the JD Parser Agent.
Extracted from main agent to comply with 200-line development guidelines.
"""

import json
import requests
from typing import Dict, Any, Optional
import time


class JDLLMCoreMixin:
    """Core LLM integration methods for JD Parser Agent"""
    
    def _call_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Direct HTTP call to Anthropic API"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = f"API call failed: {response.status_code}"
                if response.text:
                    print(f"❌ Anthropic API error: {response.status_code} - {response.text}")
                    error_msg += f" - {response.text}"
                print(f"❌ Anthropic API call failed: {error_msg}")
                raise Exception(error_msg)
            
            response_data = response.json()
            
            if "content" not in response_data or not response_data["content"]:
                raise Exception("Invalid response format from Anthropic API")
            
            content = response_data["content"][0]["text"]
            cleaned_content = self._clean_json_response(content)
            
            try:
                return json.loads(cleaned_content)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed: {str(e)}")
                return self._attempt_json_repair(cleaned_content)
        
        except requests.exceptions.Timeout:
            raise Exception("Anthropic API timeout - request took too long")
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"Connection failed: {str(e)}")
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")
    
    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API using official client"""
        if not self.openai_client:
            raise Exception("OpenAI client not configured")
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content
            cleaned_content = self._clean_json_response(content)
            
            try:
                return json.loads(cleaned_content)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed: {str(e)}")
                return self._attempt_json_repair(cleaned_content)
        
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response from markdown and whitespace"""
        # Remove markdown code blocks
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        
        # Clean whitespace
        response = response.strip()
        
        return response
    
    def _attempt_json_repair(self, malformed_json: str) -> Dict[str, Any]:
        """Attempt to repair malformed JSON response"""
        print("🔧 Attempting JSON repair...")
        
        # Try common fixes
        fixes = [
            lambda s: s + '}',  # Add missing closing brace
            lambda s: s + '"}',  # Add missing closing quote and brace
            lambda s: s.replace('""', '"'),  # Fix double quotes
            lambda s: s.replace('\n', ' ').replace('\r', ''),  # Remove newlines
        ]
        
        for fix in fixes:
            try:
                fixed = fix(malformed_json)
                return json.loads(fixed)
            except:
                continue
        
        # If repair fails, return fallback structure
        print("⚠️ JSON repair failed, using fallback structure")
        return {
            "job_title": "Parsing Error - Check JSON Format",
            "company_name": "Unknown",
            "location": "Unknown", 
            "job_summary": [],
            "required_skills": [],
            "preferred_skills": [],
            "required_experience": [],
            "required_education": [],
            "required_qualifications": [],
            "preferred_qualifications": [],
            "key_responsibilities": [],
            "work_environment": [],
            "company_info": [],
            "team_info": [],
            "benefits": [],
            "confidence_score": 0.1,
            "parsing_notes": [
                "JSON parsing failed - malformed response from LLM",
                f"Original response length: {len(malformed_json)} characters",
                "Using fallback parsing structure"
            ]
        }
    
    def _fallback_parsing(self, job_text: str) -> Dict[str, Any]:
        """Fallback parsing when LLM is unavailable"""
        print("🔄 Using fallback parsing (DEMO MODE)")
        
        # Simple regex-based extraction for demo
        lines = job_text.split('\n')
        
        job_title = "Unknown Position"
        company_name = "Unknown Company"
        
        # Try to extract basic info
        if len(lines) > 0 and lines[0].strip():
            job_title = lines[0].strip()
        if len(lines) > 1 and lines[1].strip():
            company_name = lines[1].strip()
        
        return {
            "job_title": job_title,
            "company_name": company_name,
            "location": "Not specified",
            "job_summary": ["Basic fallback parsing - LLM unavailable"],
            "required_skills": ["See original job description"],
            "preferred_skills": [],
            "required_experience": [],
            "required_education": [],
            "required_qualifications": [],
            "preferred_qualifications": [],
            "key_responsibilities": ["See original job description"],
            "work_environment": [],
            "company_info": [],
            "team_info": [],
            "benefits": [],
            "confidence_score": 0.2,
            "parsing_notes": [
                "DEMO MODE: LLM parsing unavailable",
                "Basic fallback extraction used",
                "For full parsing, ensure API keys are configured"
            ]
        }