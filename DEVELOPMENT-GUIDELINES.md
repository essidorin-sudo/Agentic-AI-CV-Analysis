# Agentic AI CV Analysis - Modular Development Guidelines

## CORE RULES - ALWAYS FOLLOW

ALWAYS: when you create a code component - there should be a detailed README file in the same folder. It should be named as "name of the component"+"README" and should be placed in the folder with component. For example "CVParserAgent-README.md" it should describe in plain and simple english the logic and code in the component (for example cv_parser/agent.py) and illustrate the place of this component in the architecture and its functions. Use flowcharts and diagrams where appropriate. Don't write code in the README files, just plain english and diagrams. ALWAYS: update README files when the code functionality changes.

1. **NEVER create files > 200 lines** - Split into smaller modules (Python files should be even smaller), markdown and readme files can be of any length
2. **NEVER mix concerns** - One file, one purpose (e.g., don't mix LLM calls with web interface logic)
3. **ALWAYS update README** - Document every new feature/agent/module
4. **ALWAYS maintain agent boundaries** - Use the defined public APIs between agents
5. **ALWAYS follow security protocols** - Validate inputs, authenticate agents, protect sensitive data

## Project Structure for Agentic AI CV Analysis

```
agentic-ai-cv-analysis/
├── README.md                     # Quick start & overview
├── ARCHITECTURE.md              # System design (5 core agents)
├── DEVELOPMENT-GUIDELINES.md    # This file - guidelines
├── MEMORY.md                   # Decisions & lessons learned
├── docs/
│   ├── agents/                 # Agent specifications
│   │   ├── cv-parser.md
│   │   ├── jd-parser.md
│   │   ├── content-matcher.md
│   │   ├── gap-analyst.md
│   │   └── report-generator.md
│   └── workflows/              # End-to-end workflows
├── agents/
│   ├── cv_parser/              # CV Parser Agent
│   │   ├── README.md
│   │   ├── agent.py           # Main agent logic
│   │   ├── parsers/           # File format parsers
│   │   ├── templates/         # Web interface
│   │   └── test_interface.py  # Testing interface
│   ├── jd_parser/             # Job Description Parser Agent
│   │   ├── README.md
│   │   ├── agent.py
│   │   ├── scrapers/          # Web scrapers
│   │   ├── templates/
│   │   └── test_interface.py
│   ├── content_matcher/       # Content Matching Agent
│   │   ├── README.md
│   │   ├── agent.py
│   │   ├── matchers/          # Matching algorithms
│   │   ├── templates/
│   │   └── test_interface.py
│   ├── gap_analyst/           # Gap Analysis Agent
│   │   ├── README.md
│   │   ├── agent.py
│   │   ├── analyzers/         # Analysis logic
│   │   ├── templates/
│   │   └── test_interface.py
│   └── report_generator/      # Report Generation Agent
│       ├── README.md
│       ├── agent.py
│       ├── generators/        # Report formats
│       ├── templates/
│       └── test_interface.py
├── shared/
│   ├── llm_clients/           # LLM integrations
│   │   ├── README.md
│   │   ├── anthropic_client.py
│   │   └── openai_client.py
│   ├── data_models/           # Shared data structures
│   │   ├── README.md
│   │   ├── cv_models.py
│   │   └── jd_models.py
│   ├── security/              # Security utilities
│   │   ├── README.md
│   │   ├── file_validator.py
│   │   ├── input_sanitizer.py
│   │   └── auth_manager.py
│   └── utils/                 # Shared utilities
│       ├── README.md
│       ├── file_utils.py
│       └── text_utils.py
└── tests/
    ├── unit/                  # Agent unit tests
    ├── integration/           # Cross-agent tests
    └── e2e/                   # End-to-end workflows
```

## Agent Architecture

```
┌─────────────────────────────────────────────────┐
│                 WEB INTERFACES                   │
│         (Flask Apps & Testing GUIs)             │
├─────────────────────────────────────────────────┤
│                 AGENT LAYER                      │
│  CV Parser │ JD Parser │ Matcher │ Analyst │ Gen │
├─────────────────────────────────────────────────┤
│                SERVICE LAYER                     │
│        LLM Clients & Processing Logic            │
├─────────────────────────────────────────────────┤
│                SECURITY LAYER                    │
│      Input Validation & Authentication           │
├─────────────────────────────────────────────────┤
│                DATA LAYER                        │
│          File System & Temporary Storage         │
└─────────────────────────────────────────────────┘
```

## Agent Communication & Dependencies

```
                    ┌──────────────┐
                    │    Report    │
                    │  Generator   │
                    └──────┬───────┘
                           │ Consumes
                    ┌──────▼───────┐
        ┌──────────►│     Gap      │◄──────────┐
        │           │   Analyst    │           │
        │           └──────┬───────┘           │
        │                  │                   │
        │                  │ Analyzes          │ Provides
        │                  ▼                   │ Analysis
┌───────┴──────┐   ┌──────────────┐   ┌───────┴──────┐
│   Content    │◄──│   CV/JD      │──►│    Human     │
│   Matcher    │   │    Data      │   │  Interface   │
└──────┬───────┘   └──────┬───────┘   └──────────────┘
       │                  │
       │ Orchestrates     │ Parsed Data
       ▼                  ▼
┌──────────────┐   ┌──────────────┐
│  CV Parser   │   │  JD Parser   │
│    Agent     │   │    Agent     │
└──────────────┘   └──────────────┘
     Processes           Processes
   CV Documents      Job Descriptions
```

## LLM Integration Best Practices

### Prompt Engineering Guidelines

```python
# Standard prompt structure template
class PromptTemplate:
    def __init__(self, template_name: str, version: str):
        self.template_name = template_name
        self.version = version
        self.template = self.load_template()
        
    def load_template(self) -> str:
        # Load versioned prompts from templates/prompts/
        return f"prompts/{self.template_name}_v{self.version}.txt"

# Prompt versioning strategy
PROMPT_VERSIONS = {
    "cv_parsing": "1.2.3",
    "jd_analysis": "2.1.0", 
    "gap_analysis": "1.4.1",
    "content_matching": "1.0.2"
}
```

### Token Management

```python
class TokenManager:
    def __init__(self, max_tokens_per_request: int = 4000):
        self.max_tokens_per_request = max_tokens_per_request
        self.token_budget = {}
        
    def estimate_tokens(self, text: str) -> int:
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def optimize_prompt(self, prompt: str, max_tokens: int) -> str:
        if self.estimate_tokens(prompt) <= max_tokens:
            return prompt
        # Implement smart truncation/compression
        return self.compress_prompt(prompt, max_tokens)
    
    def track_usage(self, agent_id: str, tokens_used: int, cost: float):
        if agent_id not in self.token_budget:
            self.token_budget[agent_id] = {"tokens": 0, "cost": 0.0}
        self.token_budget[agent_id]["tokens"] += tokens_used
        self.token_budget[agent_id]["cost"] += cost
```

### Model Selection Criteria

```python
# Model selection based on task complexity and requirements
MODEL_SELECTION = {
    "cv_parsing": {
        "primary": "claude-3-5-sonnet-20241022",  # High accuracy needed
        "fallback": "claude-3-haiku-20240307",    # Cost-effective backup
        "max_tokens": 4000,
        "temperature": 0.1
    },
    "jd_analysis": {
        "primary": "claude-3-5-sonnet-20241022",
        "fallback": "claude-3-haiku-20240307", 
        "max_tokens": 3000,
        "temperature": 0.2
    },
    "gap_analysis": {
        "primary": "claude-3-5-sonnet-20241022",  # Complex reasoning required
        "fallback": "claude-3-sonnet-20240229",
        "max_tokens": 4000,
        "temperature": 0.3
    },
    "report_generation": {
        "primary": "claude-3-haiku-20240307",     # Speed over complexity
        "fallback": "claude-3-sonnet-20240229",
        "max_tokens": 2000,
        "temperature": 0.4
    }
}
```

### LLM Failure Recovery

```python
class LLMClient:
    def __init__(self, retry_attempts: int = 3, timeout: int = 60):
        self.retry_attempts = retry_attempts
        self.timeout = timeout
        self.circuit_breaker = CircuitBreaker()
    
    async def call_with_retry(self, prompt: str, model_config: dict) -> str:
        for attempt in range(self.retry_attempts):
            try:
                if self.circuit_breaker.is_open():
                    raise CircuitBreakerOpenException("LLM service unavailable")
                
                response = await self.make_llm_call(prompt, model_config)
                self.circuit_breaker.record_success()
                return response
                
            except (TimeoutError, ConnectionError) as e:
                self.circuit_breaker.record_failure()
                if attempt == self.retry_attempts - 1:
                    # Try fallback model
                    return await self.try_fallback_model(prompt, model_config)
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise LLMProcessingException("All retry attempts failed")
    
    async def try_fallback_model(self, prompt: str, config: dict) -> str:
        fallback_config = config.copy()
        fallback_config["model"] = config.get("fallback_model")
        return await self.make_llm_call(prompt, fallback_config)
```

## Error Recovery & Resilience

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def is_open(self) -> bool:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return False
            return True
        return False
    
    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
```

### Graceful Degradation

```python
class AgentDegradationStrategy:
    def __init__(self):
        self.degraded_responses = {
            "cv_parser": self.cv_parser_fallback,
            "jd_parser": self.jd_parser_fallback,
            "gap_analyst": self.gap_analyst_fallback
        }
    
    def cv_parser_fallback(self, file_content: bytes) -> dict:
        # Basic text extraction without LLM processing
        text = self.extract_plain_text(file_content)
        return {
            "success": True,
            "degraded": True,
            "data": {
                "raw_text": text,
                "message": "Limited parsing available - LLM service unavailable"
            }
        }
    
    def gap_analyst_fallback(self, cv_data: dict, jd_data: dict) -> dict:
        # Simple keyword matching without intelligent analysis
        return {
            "success": True,
            "degraded": True,
            "basic_match_score": self.calculate_basic_match(cv_data, jd_data),
            "message": "Basic analysis only - Full AI analysis unavailable"
        }
```

### Agent Recovery Mechanisms

```python
class AgentRecoveryManager:
    def __init__(self):
        self.agent_states = {}
        self.recovery_strategies = {
            "memory_leak": self.restart_agent,
            "connection_timeout": self.reset_connections,
            "file_corruption": self.clear_cache_and_restart
        }
    
    async def monitor_agent_health(self, agent_id: str):
        while True:
            try:
                health = await self.check_agent_health(agent_id)
                if not health.is_healthy:
                    await self.initiate_recovery(agent_id, health.issues)
            except Exception as e:
                logging.error(f"Health check failed for {agent_id}: {e}")
            await asyncio.sleep(30)  # Check every 30 seconds
    
    async def initiate_recovery(self, agent_id: str, issues: List[str]):
        for issue in issues:
            if issue in self.recovery_strategies:
                try:
                    await self.recovery_strategies[issue](agent_id)
                    logging.info(f"Recovery successful for {agent_id}: {issue}")
                except Exception as e:
                    logging.error(f"Recovery failed for {agent_id}: {e}")
    
    async def restart_agent(self, agent_id: str):
        # Graceful shutdown and restart
        await self.save_agent_state(agent_id)
        await self.shutdown_agent(agent_id)
        await self.start_agent(agent_id)
        await self.restore_agent_state(agent_id)
```

## Security Considerations

### File Upload Security

```python
class FileValidator:
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def validate_file(self, file_content: bytes, filename: str) -> dict:
        validation_result = {
            "is_valid": True,
            "issues": [],
            "file_info": {}
        }
        
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            validation_result["is_valid"] = False
            validation_result["issues"].append(f"Unsupported file type: {file_ext}")
        
        # Check file size
        if len(file_content) > self.MAX_FILE_SIZE:
            validation_result["is_valid"] = False
            validation_result["issues"].append("File size exceeds 10MB limit")
        
        # Check for malicious content
        if self.scan_for_malicious_content(file_content):
            validation_result["is_valid"] = False
            validation_result["issues"].append("Potentially malicious content detected")
        
        # Verify file integrity
        if not self.verify_file_integrity(file_content, file_ext):
            validation_result["is_valid"] = False
            validation_result["issues"].append("File appears to be corrupted")
        
        return validation_result
    
    def scan_for_malicious_content(self, content: bytes) -> bool:
        # Check for embedded scripts, macros, or suspicious patterns
        suspicious_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'<?php',
            b'exec(',
            b'eval(',
            b'ActiveX'
        ]
        
        content_lower = content.lower()
        return any(pattern in content_lower for pattern in suspicious_patterns)
    
    def verify_file_integrity(self, content: bytes, file_ext: str) -> bool:
        # Verify file headers match extension
        file_signatures = {
            '.pdf': [b'%PDF'],
            '.docx': [b'PK\x03\x04'],  # ZIP-based format
            '.doc': [b'\xd0\xcf\x11\xe0'],  # OLE format
            '.txt': []  # No specific signature required
        }
        
        if file_ext in file_signatures and file_signatures[file_ext]:
            return any(content.startswith(sig) for sig in file_signatures[file_ext])
        return True
```

### Input Sanitization

```python
class InputSanitizer:
    def sanitize_text_input(self, text: str) -> str:
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
        sanitized = text
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Limit length to prevent memory exhaustion
        max_length = 50000  # 50KB of text
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "... [truncated]"
        
        return sanitized.strip()
    
    def sanitize_filename(self, filename: str) -> str:
        # Remove path traversal attempts
        safe_name = os.path.basename(filename)
        
        # Remove special characters
        safe_chars = re.sub(r'[^\w\-_\.]', '_', safe_name)
        
        # Ensure reasonable length
        if len(safe_chars) > 100:
            name, ext = os.path.splitext(safe_chars)
            safe_chars = name[:95] + ext
        
        return safe_chars
    
    def validate_url(self, url: str) -> bool:
        # Basic URL validation for JD scraping
        if not url.startswith(('http://', 'https://')):
            return False
        
        try:
            parsed = urllib.parse.urlparse(url)
            # Block localhost and private IPs
            if parsed.hostname in ['localhost', '127.0.0.1']:
                return False
            
            # Check against allowed domains (implement whitelist)
            allowed_domains = [
                'linkedin.com', 'indeed.com', 'glassdoor.com',
                'monster.com', 'careerbuilder.com'
            ]
            
            domain = parsed.hostname.lower()
            return any(domain.endswith(allowed) for allowed in allowed_domains)
        except:
            return False
```

### Agent Authentication

```python
class AgentAuthManager:
    def __init__(self):
        self.agent_tokens = {}
        self.token_expiry = {}
        self.session_timeout = 3600  # 1 hour
    
    def generate_agent_token(self, agent_id: str, agent_version: str) -> str:
        # Generate secure token for agent-to-agent communication
        token_data = {
            "agent_id": agent_id,
            "version": agent_version,
            "timestamp": time.time(),
            "nonce": secrets.token_hex(16)
        }
        
        # Create HMAC signature
        secret_key = os.getenv('AGENT_SECRET_KEY', 'default-dev-key')
        token_string = json.dumps(token_data, sort_keys=True)
        signature = hmac.new(
            secret_key.encode(),
            token_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        token = base64.b64encode(
            json.dumps({**token_data, "signature": signature}).encode()
        ).decode()
        
        # Store token with expiry
        self.agent_tokens[agent_id] = token
        self.token_expiry[agent_id] = time.time() + self.session_timeout
        
        return token
    
    def validate_agent_token(self, token: str) -> dict:
        try:
            # Decode and verify token
            token_data = json.loads(base64.b64decode(token).decode())
            agent_id = token_data.get('agent_id')
            
            # Check expiry
            if time.time() > token_data.get('timestamp', 0) + self.session_timeout:
                return {"valid": False, "reason": "Token expired"}
            
            # Verify signature
            signature = token_data.pop('signature')
            secret_key = os.getenv('AGENT_SECRET_KEY', 'default-dev-key')
            expected_signature = hmac.new(
                secret_key.encode(),
                json.dumps(token_data, sort_keys=True).encode(),
                hashlib.sha256
            ).hexdigest()
            
            if signature != expected_signature:
                return {"valid": False, "reason": "Invalid signature"}
            
            return {"valid": True, "agent_id": agent_id}
            
        except Exception as e:
            return {"valid": False, "reason": f"Token validation error: {str(e)}"}
```

## Agent Creation Checklist

### For EVERY New Agent:

```
Agent: [NAME]
├── □ Create agent folder structure
├── □ Write README.md with API specification
├── □ Define Python data classes/models
├── □ Create agent.py with public methods
├── □ Implement security validations
├── □ Add LLM integration with fallbacks
├── □ Write test specifications
├── □ Implement core processing functions
├── □ Add web interface (test_interface.py)
├── □ Configure monitoring and logging
├── □ Update main README
└── □ Update MEMORY.md with decisions
```

## Agent README Template

```markdown
# [Agent Name] Agent

## Purpose
[Single sentence describing agent responsibility]

## Public API

| Method | Input | Output | Purpose |
|--------|-------|--------|---------|
| process_cv | file_content, filename | CVData | Parse CV content |
| get_status | - | dict | Check agent health |

## Security Considerations
- Input validation: [describe validation rules]
- Authentication: [describe auth requirements]
- File handling: [describe security measures]

## LLM Integration
- Primary model: [model name and version]
- Fallback strategy: [fallback approach]
- Token limits: [max tokens per request]
- Prompt version: [current prompt version]

## Dependencies

### Internal
- shared/llm_clients (for LLM processing)
- shared/data_models (for structured data)
- shared/security (for validation and auth)

### External
- flask (web interface)
- anthropic (LLM API)
- [Other packages from requirements.txt]

## File Structure
\```
agent-name/
├── README.md           # This documentation
├── agent.py           # Main agent class
├── [name]_service.py  # Business logic
├── parsers/           # Specialized parsers
├── templates/         # Web interface templates
└── test_interface.py  # Testing web interface
\```

## Configuration
[Environment variables and configuration options]

## Error Handling
[Failure modes and recovery strategies]

## Performance Considerations
[LLM token usage, processing time, memory usage]

## Testing
[How to test this agent in isolation and integration]
```

## File Size Monitoring

```
┌─────────────────────────────────────────────┐
│           File Size Thresholds              │
├─────────────────────────────────────────────┤
│ Python Files:                               │
│   ⚠️  Warning at:  150 lines               │
│   🛑 Must split at: 200 lines              │
│                                             │
│ Agent Classes:                              │
│   ⚠️  Warning at:  100 lines               │
│   🛑 Must split at: 150 lines              │
│                                             │
│ Flask Routes:                               │
│   ⚠️  Warning at:  200 lines               │
│   🛑 Must split at: 300 lines              │
└─────────────────────────────────────────────┘
```

## Agent-Specific Guidelines

### CV Parser Agent

```
Structure:
├── CVParserAgent
│   ├── PDF parsing (PyPDF2, pdfplumber)
│   ├── DOCX parsing (python-docx)
│   └── Text extraction & formatting
├── ParsingService
│   ├── File validation & security
│   ├── Content extraction
│   └── Data structuring
└── CVDataModels
    ├── PersonalInfo class
    ├── WorkExperience class
    └── Education class

Max Complexity:
- Parsing functions: 30 lines each
- LLM prompt functions: 50 lines each
- No more than 5 methods per class

Security Requirements:
- File type validation (PDF, DOCX, TXT only)
- Malware scanning for uploaded files
- Content sanitization before LLM processing
```

### JD Parser Agent

```
Structure:
├── JDParserAgent
│   ├── URL scraping (requests, BeautifulSoup)
│   ├── Text processing
│   └── Content structuring
├── ScrapingService
│   ├── Website detection
│   ├── Content extraction
│   └── Text cleaning
└── JDDataModels
    ├── JobDetails class
    ├── Requirements class
    └── Company class

Key Rules:
- Always respect robots.txt
- Implement rate limiting for scraping
- Cache scraped content for efficiency
- URL validation and whitelist enforcement

Security Requirements:
- Validate URLs against whitelist
- Block localhost/private IP access
- Sanitize scraped content
- Implement request rate limiting
```

### Content Matcher Agent

```
Structure:
├── ContentMatcherAgent
│   ├── Agent orchestration
│   ├── Data validation
│   └── Response coordination
├── MatchingService
│   ├── CV-JD alignment
│   ├── Skills matching
│   └── Experience correlation
└── MatchingTypes
    ├── MatchResult class
    ├── MatchScore interface
    └── MatchSession type

Critical Performance:
- Agent response time < 30 seconds
- LLM token optimization
- Error handling and retries
- Comprehensive logging

Security Requirements:
- Agent authentication tokens
- Input validation for all data
- Session management and timeouts
- Encrypted agent communication
```

### Gap Analyst Agent

```
Structure:
├── GapAnalystAgent
│   ├── Intelligent highlighting
│   ├── Score calculation
│   └── Recommendation generation
├── AnalysisService
│   ├── Skills gap analysis
│   ├── Experience assessment
│   └── Improvement suggestions
└── AnalysisTypes
    ├── GapAnalysisResult class
    ├── MatchScore class
    └── Highlight types

Intelligent Rules:
- Skills: Individual term highlighting
- Experience: Section-level highlighting
- Address-based targeting system
- Content-aware granularity

Security Requirements:
- Sanitize analysis inputs
- Validate highlighting addresses
- Protect against injection attacks
- Secure recommendation generation
```

### Report Generator Agent

```
Structure:
├── ReportGeneratorAgent
│   ├── Report compilation
│   ├── Format generation
│   └── Export handling
├── GenerationService
│   ├── Template processing
│   ├── Data formatting
│   └── File creation
└── ReportTypes
    ├── Report interface
    ├── ReportFormat enum
    └── ExportOptions type

Export Formats:
- PDF reports (comprehensive analysis)
- JSON (structured data)
- HTML (interactive reports)
- CSV (tabular summaries)

Security Requirements:
- Template injection prevention
- File path validation
- Content sanitization
- Safe file generation
```

## Memory File Structure

```markdown
# MEMORY.md

## Architecture Decisions
| Date | Decision | Reasoning | Outcome |
|------|----------|-----------|---------|
| Day 1 | Flask for web interfaces | Simple, lightweight | Fast development |
| Day 2 | Anthropic Claude API | High-quality analysis | Excellent results |

## Security Lessons
### File Upload Security
- Lesson: Need comprehensive validation
- Solution: Multi-layer security checks

### Agent Authentication  
- Lesson: Token-based auth prevents spoofing
- Solution: HMAC-signed JWT tokens

## Agent Lessons
### CV Parser Agent
- Lesson: PDF parsing inconsistent
- Solution: Multiple parser fallbacks

### JD Parser Agent
- Lesson: Website blocking scrapers
- Solution: User-Agent rotation, delays

### Content Matcher Agent
- Lesson: Agent coordination complex
- Solution: Centralized orchestration

### Gap Analyst Agent
- Lesson: Generic highlighting poor
- Solution: Intelligent content-aware highlighting

## Performance Optimizations
- LLM prompt caching
- Agent response streaming
- File processing chunking
- Circuit breaker patterns

## Known Issues
- Large PDF files slow to process
- Some job sites block scraping
- LLM token limits with long documents
- Security validation adds processing time
```

## Agent Communication Patterns

```
User Request Flow:
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   User   │────▶│   CV     │────▶│ Content  │────▶│   Gap    │
│Interface │     │ Parser   │     │ Matcher  │     │ Analyst  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                 │                 │                │
     │                 ▼                 ▼                ▼
     │          [Parsed CV]         [Match Data]    [Analysis]
     │                 │                 │                │
     └─────────────────┴─────────────────┴────────────────┘
                              │
                              ▼
                        [Secure Storage]

Authenticated Data Flow:
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   JD     │────▶│ Content  │────▶│   Gap    │────▶│  Report  │
│ Parser   │     │ Matcher  │     │ Analyst  │     │Generator │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
    │ [Auth]         │ [Auth]         │ [Auth]         │ [Auth]
    └────────────────┴────────────────┴────────────────┘
                              │
                              ▼
                        [Token Validation]
```

## Quality Checks Before Commit

```
Pre-Commit Checklist:
├── □ All files < 200 lines
├── □ Agent READMEs updated
├── □ No circular dependencies
├── □ Tests cover new code
├── □ Security validations implemented
├── □ LLM prompts optimized
├── □ Error handling with fallbacks
├── □ Input sanitization in place
├── □ Authentication mechanisms working
├── □ Web interfaces tested
├── □ MEMORY.md updated
└── □ Main README current
```

## Common Pitfalls to Avoid

```
❌ DON'T:
- Mix LLM calls with web interface logic
- Create monolithic agent files
- Import from deep paths (use agent APIs)
- Skip input validation and sanitization
- Hardcode API keys or secrets
- Ignore LLM failure scenarios
- Process files without security checks
- Allow unauthenticated agent communication
- Use synchronous LLM calls in web routes
- Store sensitive data in logs

✅ DO:
- Keep agents focused on single responsibility
- Use proper Python type hints
- Validate all inputs and file uploads
- Implement comprehensive error handling
- Use environment variables for configuration
- Add security layers at all entry points
- Cache LLM responses when appropriate
- Implement proper agent authentication
- Add circuit breakers for external dependencies
- Document unusual security decisions
```

## Agent Health Indicators

```
Healthy Agent:
├── ✅ Clear single responsibility
├── ✅ Well-defined public API
├── ✅ No circular dependencies
├── ✅ All files < 200 lines
├── ✅ README up to date
├── ✅ Tests passing
├── ✅ Security validations working
├── ✅ Web interface functional
├── ✅ LLM integration with fallbacks
└── ✅ Proper error handling

Unhealthy Agent:
├── ❌ Multiple responsibilities
├── ❌ Exposes internal methods
├── ❌ Circular dependencies
├── ❌ Large files (> 200 lines)
├── ❌ Outdated documentation
├── ❌ Failing tests
├── ❌ Security vulnerabilities
├── ❌ Broken web interface
├── ❌ LLM errors not handled
└── ❌ No input validation
```

## Success Metrics for Agents

```
CV Parser Agent Success:
□ Handles PDF, DOCX, TXT formats securely
□ Extracts structured data accurately  
□ Processing time < 10 seconds
□ Rejects malicious files correctly
□ Error handling for corrupted files

JD Parser Agent Success:
□ Scrapes major job sites successfully
□ Handles both URL and text input safely
□ Respects rate limiting and robots.txt
□ Validates URLs against whitelist
□ Parses requirements accurately

Content Matcher Agent Success:
□ Orchestrates agent communication securely
□ Provides unified web interface
□ Handles concurrent requests
□ Validates agent authentication
□ Maintains session state securely

Gap Analyst Agent Success:
□ Intelligent highlighting working
□ Accurate scoring algorithms
□ Meaningful recommendations
□ Fast analysis processing
□ Input validation and sanitization

Report Generator Agent Success:
□ Multiple export formats work
□ Professional report layouts
□ Accurate data representation
□ Fast report generation
□ Template injection prevention
```

## Configuration Management

### Environment Variables

```bash
# LLM Configuration
ANTHROPIC_API_KEY=your_api_key_here
OPENAI_API_KEY=your_api_key_here

# Security Configuration
AGENT_SECRET_KEY=your_secret_key_here
FILE_UPLOAD_MAX_SIZE=10485760  # 10MB in bytes
ALLOWED_DOMAINS=linkedin.com,indeed.com,glassdoor.com

# Agent Ports
CV_PARSER_PORT=5004
JD_PARSER_PORT=5007
CONTENT_MATCHER_PORT=5006
GAP_ANALYST_PORT=5008
REPORT_GENERATOR_PORT=5009

# Processing Limits
MAX_FILE_SIZE_MB=10
LLM_TIMEOUT_SECONDS=60
MAX_CONCURRENT_REQUESTS=5
CIRCUIT_BREAKER_THRESHOLD=5
```

## Monitoring and Logging

### Logging Standards

```python
import logging
import structlog

# Enhanced logging with security context
def setup_logger(agent_name: str):
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger(agent_name)

# Usage in agents with security context
logger = setup_logger(__name__)
logger.info("Agent started", 
           agent=agent_name, 
           port=port, 
           security_level="high")
logger.error("Processing failed", 
            error=str(error),
            file_hash=hashlib.sha256(file_content).hexdigest()[:8])
```

---

*This document provides comprehensive development guidelines for the Agentic AI CV Analysis system with enhanced security, LLM integration best practices, and robust error handling. Follow these guidelines to ensure consistent, maintainable, secure, and scalable agent development.*