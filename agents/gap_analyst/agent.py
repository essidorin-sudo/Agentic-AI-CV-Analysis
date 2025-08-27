#!/usr/bin/env python3
"""
Gap Analyst Agent - CV and JD Gap Analysis with LLM-based Matching

This agent performs intelligent gap analysis between CV and JD data,
providing color-coded matching results and comprehensive scoring.
"""

import json
import requests
import os
from typing import Dict, List, Optional, Tuple
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
class MatchScore:
    """Scoring information for CV-JD matching"""
    overall_score: float  # 0-100
    skills_score: float
    experience_score: float
    education_score: float
    qualifications_score: float
    recommendations: List[str]
    strengths: List[str]
    gaps: List[str]


@dataclass 
class GapAnalysisResult:
    """Result of gap analysis between CV and JD"""
    cv_data: Dict
    jd_data: Dict
    cv_highlighted: str  # HTML string with color-coded highlighting
    jd_highlighted: str  # HTML string with color-coded highlighting
    match_score: MatchScore
    analysis_notes: List[str]
    timestamp: str
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class GapAnalystAgent:
    """
    Gap Analyst Agent - LLM-based CV and JD Matching Analysis
    
    This agent performs sophisticated gap analysis using LLM to identify
    matches, partial matches, and gaps between CV and JD requirements.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.version = "1.0.0"
        self.agent_id = f"gap_analyst_{datetime.now().strftime('%Y%m%d')}"
        
        # LLM configuration
        self.llm_provider = self.config.get('llm_provider', 'anthropic')
        self.model_name = self.config.get('model_name', 'claude-3-5-sonnet-20241022')
        self.temperature = self.config.get('temperature', 0.2)  # Lower temperature for analysis
        
        # Initialize LLM clients
        self._init_llm_clients()
        
        # Prompt persistence
        self.prompt_file = Path(__file__).parent / 'default_prompt.txt'
        
        # Core gap analysis prompt
        self.analysis_prompt = self._load_default_prompt()
        
        # Content Matcher endpoint
        self.content_matcher_url = self.config.get('content_matcher_url', 'http://localhost:5005')
        
        print(f"🤖 Gap Analyst Agent v{self.version} initialized")
        print(f"🧠 Using {self.llm_provider} model: {self.model_name}")
    
    def _load_default_prompt(self) -> str:
        """Load saved default prompt or return built-in default"""
        try:
            if self.prompt_file.exists():
                with open(self.prompt_file, 'r', encoding='utf-8') as f:
                    saved_prompt = f.read().strip()
                    if saved_prompt:
                        print(f"📄 Loaded saved default prompt from {self.prompt_file}")
                        return saved_prompt
        except Exception as e:
            print(f"⚠️  Could not load saved prompt: {e}")
        
        # Return built-in default prompt
        print("📝 Using built-in default prompt")
        return self._get_gap_analysis_prompt()
    
    def _init_llm_clients(self):
        """Initialize LLM clients based on configuration"""
        
        # Anthropic client
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_api_key:
            self.anthropic_api_key = anthropic_api_key
            self.anthropic_client = "direct_api"
            print("✅ Anthropic API key configured for direct calls")
        else:
            self.anthropic_api_key = None
            self.anthropic_client = None
    
    def _get_gap_analysis_prompt(self) -> str:
        """Get the core gap analysis prompt template"""
        
        return """You are an expert CV-JD Gap Analysis Agent. Analyze the CV and Job Description to create INTELLIGENT address-based highlighting instructions and comprehensive scoring.

INTELLIGENT HIGHLIGHTING APPROACH - CRITICAL REQUIREMENTS:

1. CONTENT-AWARE GRANULARITY:
   - SKILLS/TECHNOLOGIES: Look for line-level addresses containing specific skills, but note in reason which SPECIFIC terms to highlight (e.g., "Python", "AWS", "Docker")
   - EXPERIENCE/QUALIFICATIONS: Target whole sections/positions that need narrative improvement or reframing
   
2. ADDRESS VALIDATION:
   - ONLY reference addresses that actually exist in the provided markup
   - Available CV addresses: cv_section_X, cv_position_X, cv_item_X, cv_line_X
   - Available JD addresses: jd_section_X, jd_requirement_X, jd_skill_X, jd_qualification_X, jd_line_X
   - DO NOT invent addresses like cv_skill_python or jd_requirement_aws - they don't exist
   
3. INTELLIGENT REASONING:
   - For skills: Specify exactly which skill terms within the line need highlighting
   - For experience: Explain what narrative improvements are needed for the whole section
   - Make clear whether you're targeting individual words or complete sections

TASK: 
1. Analyze matches between CV and JD content
2. Return highlighting instructions by address reference with intelligent content targeting
3. Provide comprehensive scoring and recommendations

SCORING GUIDELINES (return scores as percentages 0.0-100.0):
- Overall Score: Weighted average of all categories (typically 20-90%)
- Skills Score: % of required skills that candidate has (0%=none, 50%=half, 100%=all+more)
- Experience Score: Match quality (0%=no match, 50%=some relevant, 80%=good match, 100%=exceeds)
- Education Score: Education requirement match (0%=missing, 80%=meets minimum, 100%=exceeds)
- Qualifications Score: Additional qualifications match (0%=none, 50%=some, 100%=all+bonus)

HIGHLIGHTING CLASSES:
- "highlight-match": Exact matches between CV and JD (GREEN)
- "highlight-potential": Partial/transferable matches (ORANGE) 
- "highlight-gap": Missing required skills/experience from CV (RED)

INTELLIGENT HIGHLIGHTING APPROACH:
1. SKILLS/SYSTEMS/TECHNOLOGIES: Highlight specific words or phrases when:
   - Specific technical skills are mentioned (Python, AWS, React, ServiceNow, etc.)
   - Certifications or credentials are referenced
   - Tools, frameworks, or platforms are discussed
   - Use precise addressing for individual skill terms

2. EXPERIENCES/QUALIFICATIONS: Highlight whole sentences or sections when:
   - Job descriptions need more specific details or quantification
   - Achievements lack concrete metrics or impact statements  
   - Responsibilities could be better contextualized to match JD requirements
   - Educational background could be better positioned for the role
   - Use broader addressing for complete statements that need improvement

CV Data: {cv_data}

JD Data: {jd_data}

Return ONLY this JSON structure:
{{
    "cv_highlighting": [
        {{"address": "cv_skill_python", "class": "highlight-match", "reason": "Python skill directly matches JD requirement"}},
        {{"address": "cv_experience_section_2", "class": "highlight-potential", "reason": "This experience description could be enhanced with specific metrics and technologies used to better match platform architect requirements"}},
        {{"address": "cv_skill_leadership", "class": "highlight-match", "reason": "Leadership experience aligns with senior role expectations"}}
    ],
    "jd_highlighting": [
        {{"address": "jd_requirement_servicenow", "class": "highlight-gap", "reason": "ServiceNow certification requirement not found in CV"}},
        {{"address": "jd_requirement_experience", "class": "highlight-potential", "reason": "5+ years experience requirement - candidate's experience should be repositioned to emphasize platform and architecture work"}},
        {{"address": "jd_skill_aws", "class": "highlight-gap", "reason": "AWS cloud experience specifically required but not mentioned in CV"}}
    ],
    "match_score": {{
        "overall_score": 75.0,
        "skills_score": 65.0,
        "experience_score": 80.0,
        "education_score": 100.0,
        "qualifications_score": 70.0,
        "recommendations": ["Emphasize any cloud computing or infrastructure work in your current role descriptions", "Highlight containerization or deployment experience, even if not explicitly Docker"],
        "strengths": ["Strong Python and React skills", "Solid software engineering experience", "Relevant CS education"],
        "gaps": ["Missing AWS cloud experience", "No Docker/containerization knowledge"]
    }},
    "analysis_notes": ["Strong technical foundation with relevant programming languages", "Good experience level but missing some cloud technologies"]
}}

CRITICAL REQUIREMENTS:
- cv_highlighting and jd_highlighting arrays must contain address references found in the provided text
- Only reference addresses that actually exist in the markup (cv_section_X, cv_position_X, cv_item_X, cv_line_X for CV; jd_section_X, jd_requirement_X, jd_skill_X, jd_qualification_X, jd_line_X for JD)
- Each highlighting instruction must include: address, class, and reason
- Focus on the most relevant matches/gaps - don't highlight every single address
- Provide comprehensive scoring and actionable recommendations

RECOMMENDATIONS FOCUS:
- Focus on CV OPTIMIZATION, not gaining new experience or certifications
- Suggest how to better present existing experience and skills
- Recommend highlighting transferable skills or relevant work already done
- DO NOT suggest "Learn AWS" or "Gain 5 years experience" - focus on CV improvements only

CRITICAL: You MUST return valid JSON in the exact format specified. Never return plain text explanations."""

    def analyze_cv_jd_gap(self, cv_data: Dict, jd_data: Dict) -> GapAnalysisResult:
        """
        Perform comprehensive gap analysis between CV and JD data
        
        Args:
            cv_data: Structured CV data from CV Parser
            jd_data: Structured JD data from JD Parser
            
        Returns:
            GapAnalysisResult with highlighting and scores
        """
        
        print(f"🔍 Starting gap analysis...")
        print(f"📄 CV: {cv_data.get('full_name', 'Unknown')} vs JD: {jd_data.get('job_title', 'Unknown')}")
        print(f"🔍 JD Company: {jd_data.get('company_name', 'Unknown')}")
        print(f"🔍 JD Skills: {jd_data.get('required_skills', [][:3])}...")  # First 3 skills
        
        try:
            # Clean and validate data before analysis
            clean_cv_data = self._clean_data(cv_data)
            clean_jd_data = self._clean_data(jd_data)
            
            # Format the prompt with actual data
            full_prompt = self.analysis_prompt.format(
                cv_data=json.dumps(clean_cv_data, indent=2),
                jd_data=json.dumps(clean_jd_data, indent=2)
            )
            
            # Call the LLM for analysis
            if self.llm_provider == 'anthropic' and self.anthropic_api_key:
                analysis_data = self._call_anthropic(full_prompt)
            else:
                print("⚠️  No LLM client available, using fallback analysis")
                analysis_data = self._fallback_analysis(cv_data, jd_data)
            
            # Validate and normalize scores to 0-100 range
            def validate_score(score, name):
                if score > 100.0:
                    print(f"⚠️  {name} score {score} too high, capping at 100")
                    return 100.0
                elif score < 0.0:
                    print(f"⚠️  {name} score {score} too low, setting to 0")
                    return 0.0
                return score
            
            raw_scores = analysis_data['match_score']
            print(f"🔍 Raw LLM scores: Overall={raw_scores['overall_score']}, Skills={raw_scores['skills_score']}")
            validated_scores = {
                'overall_score': validate_score(raw_scores['overall_score'], 'Overall'),
                'skills_score': validate_score(raw_scores['skills_score'], 'Skills'),
                'experience_score': validate_score(raw_scores['experience_score'], 'Experience'),
                'education_score': validate_score(raw_scores['education_score'], 'Education'),
                'qualifications_score': validate_score(raw_scores['qualifications_score'], 'Qualifications')
            }
            print(f"🔍 Validated scores: Overall={validated_scores['overall_score']}, Skills={validated_scores['skills_score']}")
            
            # Create match score object
            match_score = MatchScore(
                overall_score=validated_scores['overall_score'],
                skills_score=validated_scores['skills_score'],
                experience_score=validated_scores['experience_score'],
                education_score=validated_scores['education_score'],
                qualifications_score=validated_scores['qualifications_score'],
                recommendations=analysis_data['match_score']['recommendations'],
                strengths=analysis_data['match_score']['strengths'],
                gaps=analysis_data['match_score']['gaps']
            )
            
            # Create result with address-based highlighting
            result = GapAnalysisResult(
                cv_data=cv_data,
                jd_data=jd_data,
                cv_highlighted=analysis_data.get('cv_highlighting', []),  # Now contains highlighting instructions
                jd_highlighted=analysis_data.get('jd_highlighting', []),  # Now contains highlighting instructions
                match_score=match_score,
                analysis_notes=analysis_data.get('analysis_notes', []),
                timestamp=datetime.now().isoformat()
            )
            
            print(f"✅ Gap analysis completed. Overall score: {match_score.overall_score:.1f}%")
            return result
            
        except Exception as e:
            print(f"❌ Error during gap analysis: {str(e)}")
            # Return fallback result
            return self._create_fallback_result(cv_data, jd_data, str(e))
    
    def _call_anthropic(self, prompt: str) -> Dict:
        """Call Anthropic API for gap analysis"""
        
        import requests
        import time
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-5-sonnet-20241022",  # Force Sonnet for full content handling
            "max_tokens": 8192,  # Maximum tokens for full content
            "temperature": self.temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        # Retry logic
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=180
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result["content"][0]["text"].strip()
                    print(f"🔍 Claude analysis response: {response_text[:200]}...")
                    break
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("retry-after", base_delay * (2 ** attempt)))
                    print(f"⏱️  Rate limited. Waiting {retry_after} seconds")
                    if attempt < max_retries - 1:
                        time.sleep(retry_after)
                        continue
                    else:
                        raise Exception("Rate limited - please wait before trying again")
                elif response.status_code == 529:
                    # Server overloaded - retry with exponential backoff
                    retry_delay = base_delay * (2 ** attempt)
                    print(f"🔄 Server overloaded. Retrying in {retry_delay} seconds (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise Exception("Server overloaded - please try again later")
                else:
                    print(f"❌ Anthropic API error: {response.status_code}")
                    print(f"📄 Error response: {response.text}")
                    raise Exception(f"API error ({response.status_code}): {response.text[:200]}")
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2 ** attempt))
                    continue
                else:
                    raise Exception("Request timed out")
        
        # Parse JSON response
        response_text = self._clean_json_response(response_text)
        
        try:
            parsed_json = json.loads(response_text)
            print(f"✅ JSON parsed successfully")
            return parsed_json
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"📄 Raw response: {response_text[:1000]}...")
            # Return fallback data instead of crashing
            print(f"🔄 Using fallback analysis due to JSON parse error")
            return {
                "cv_highlighting": [],
                "jd_highlighting": [],
                "match_score": {
                    "overall_score": 50.0,
                    "skills_score": 50.0,
                    "experience_score": 50.0,
                    "education_score": 50.0,
                    "qualifications_score": 50.0,
                    "recommendations": ["Unable to generate recommendations due to parsing error"],
                    "strengths": ["Unable to analyze strengths due to parsing error"],
                    "gaps": ["Unable to analyze gaps due to parsing error"]
                },
                "analysis_notes": ["Analysis failed due to JSON parsing error"]
            }
    
    def _clean_json_response(self, response_text: str) -> str:
        """Clean up JSON response from LLM"""
        
        # Remove markdown formatting
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        elif response_text.startswith('```'):
            response_text = response_text[3:]
        
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Ensure it starts and ends with braces
        if not response_text.startswith('{'):
            start_idx = response_text.find('{')
            if start_idx != -1:
                response_text = response_text[start_idx:]
        
        if not response_text.endswith('}'):
            end_idx = response_text.rfind('}')
            if end_idx != -1:
                response_text = response_text[:end_idx + 1]
        
        return response_text
    
    def _fallback_analysis(self, cv_data: Dict, jd_data: Dict) -> Dict:
        """Fallback analysis when LLM is not available"""
        
        return {
            "cv_highlighting": [],
            "jd_highlighting": [],
            "match_score": {
                "overall_score": 50.0,
                "skills_score": 50.0,
                "experience_score": 50.0,
                "education_score": 50.0,
                "qualifications_score": 50.0,
                "recommendations": ["Enable LLM analysis for detailed recommendations"],
                "strengths": ["Fallback mode - limited analysis available"],
                "gaps": ["Configure ANTHROPIC_API_KEY for complete analysis"]
            },
            "analysis_notes": ["Fallback analysis mode - limited functionality"]
        }
    
    def _clean_data(self, data: Dict) -> Dict:
        """Clean data to remove Unicode replacement characters and other problematic content"""
        if not isinstance(data, dict):
            return data
            
        cleaned_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Remove Unicode replacement characters and other problematic characters
                clean_value = value.replace('�', '').replace('\ufffd', '')
                # Remove excessive whitespace
                clean_value = ' '.join(clean_value.split())
                cleaned_data[key] = clean_value
            elif isinstance(value, list):
                cleaned_list = []
                for item in value:
                    if isinstance(item, str):
                        clean_item = item.replace('�', '').replace('\ufffd', '')
                        clean_item = ' '.join(clean_item.split())
                        if clean_item.strip():  # Only add non-empty strings
                            cleaned_list.append(clean_item)
                    elif isinstance(item, dict):
                        cleaned_list.append(self._clean_data(item))
                    else:
                        cleaned_list.append(item)
                cleaned_data[key] = cleaned_list
            elif isinstance(value, dict):
                cleaned_data[key] = self._clean_data(value)
            else:
                cleaned_data[key] = value
        
        return cleaned_data
    
    def _create_fallback_result(self, cv_data: Dict, jd_data: Dict, error: str) -> GapAnalysisResult:
        """Create fallback result for error cases"""
        
        match_score = MatchScore(
            overall_score=0.0,
            skills_score=0.0,
            experience_score=0.0,
            education_score=0.0,
            qualifications_score=0.0,
            recommendations=[f"Analysis failed: {error}"],
            strengths=[],
            gaps=["Could not complete gap analysis"]
        )
        
        return GapAnalysisResult(
            cv_data=cv_data,
            jd_data=jd_data,
            cv_highlighted=[],
            jd_highlighted=[],
            match_score=match_score,
            analysis_notes=[f"Analysis error: {error}"],
            timestamp=datetime.now().isoformat()
        )
    
    def update_prompt(self, new_prompt: str):
        """Update the analysis prompt for testing different approaches"""
        self.analysis_prompt = new_prompt
        print(f"🔄 Gap analysis prompt updated. Length: {len(new_prompt)} characters")
    
    def get_prompt(self) -> str:
        """Get the current analysis prompt"""
        return self.analysis_prompt
    
    def save_as_default_prompt(self, prompt: str) -> bool:
        """Save a prompt as the new default"""
        try:
            self.prompt_file.parent.mkdir(exist_ok=True)
            
            with open(self.prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            self.analysis_prompt = prompt
            
            print(f"✅ Saved new default prompt to {self.prompt_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save default prompt: {e}")
            return False


# Test the agent when run directly
if __name__ == "__main__":
    print("🤖 Gap Analyst Agent v1.0.0 - CV and JD Gap Analysis")
    print("=" * 55)
    
    # Sample test data
    sample_cv = {
        "full_name": "John Doe",
        "key_skills": ["Python", "JavaScript", "React", "SQL"],
        "work_experience": [{"position": "Software Engineer", "company": "Tech Corp"}]
    }
    
    sample_jd = {
        "job_title": "Senior Software Engineer", 
        "required_skills": ["Python", "React", "AWS", "Docker"],
        "preferred_skills": ["Kubernetes", "GraphQL"]
    }
    
    agent = GapAnalystAgent()
    result = agent.analyze_cv_jd_gap(sample_cv, sample_jd)
    
    print(f"\n📊 Gap Analysis Results:")
    print(f"Overall Score: {result.match_score.overall_score:.1f}%")
    print(f"Skills Score: {result.match_score.skills_score:.1f}%")
    print(f"Strengths: {result.match_score.strengths}")
    print(f"Gaps: {result.match_score.gaps}")