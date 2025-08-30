# LLM Integration Module

## Purpose
Handles all interactions with Language Model APIs (Anthropic Claude, OpenAI) for CV parsing, including authentication, request management, retry logic, and response processing.

## Components

### anthropic_client.py
Manages direct HTTP API calls to Anthropic Claude for both text and file processing. Handles authentication, rate limiting, retries, and response cleaning.

**Key Features:**
- Direct API integration without SDK dependencies
- File processing with base64 encoding for PDF/DOCX
- Retry logic with exponential backoff
- JSON response cleaning and repair
- Error handling and fallback responses

### prompt_manager.py  
Manages CV parsing prompts including loading, saving, and version control. Handles both built-in defaults and custom saved prompts.

**Key Features:**
- Default prompt loading from file system
- Custom prompt persistence
- Anti-hallucination protocol enforcement
- Prompt versioning and rollback capabilities
- Template variable substitution

## Data Flow

```
1. Agent Request → Prompt Manager → Load/Format Prompt
2. Formatted Prompt → Anthropic Client → API Request
3. API Response → Response Cleaning → JSON Parsing
4. Parsed Data → Validation → Return to Agent
```

## Security Considerations
- API key protection via environment variables
- Request timeout enforcement (60 seconds)
- Response size limits and validation
- Secure prompt template handling

## Error Recovery
- 3-attempt retry with exponential backoff
- Rate limiting detection and handling
- JSON parsing failure recovery
- Network error handling with timeouts

## Performance
- Token usage optimization
- Request caching where appropriate
- Connection pooling for multiple requests
- Memory-efficient file processing