# CV Parser Agent

## Purpose
Extracts structured information from CV/resume files (PDF, DOCX, TXT) using AI-powered parsing to create standardized candidate profiles for gap analysis.

## Public API

| Method | Input | Output | Purpose |
|--------|-------|--------|---------|
| `parse_cv_file(file_content, filename)` | bytes, string | ParsedCV | Parse uploaded CV file |
| `parse_cv(cv_text, metadata)` | string, dict | ParsedCV | Parse CV text content |
| `to_dict(result)` | ParsedCV | dict | Convert to dictionary |
| `to_json(result, indent)` | ParsedCV, int | string | Convert to JSON string |
| `update_prompt(new_prompt)` | string | None | Update parsing prompt |
| `get_prompt()` | None | string | Get current prompt |
| `save_as_default_prompt(prompt)` | string | bool | Save prompt as default |

## Architecture Overview

```
CV Parser Agent
├── agent.py                    # Main agent orchestration & API
├── cv_parsing_service.py       # Core business logic & data processing
├── llm_integration/            # LLM client management
│   ├── anthropic_client.py     # Anthropic API integration
│   └── prompt_manager.py       # Prompt loading & management
├── file_processors/            # File format handling
│   ├── document_processor.py   # PDF/DOCX/TXT processing
│   └── text_markup.py         # Address markup for highlighting
└── security/                   # Security validation
    └── input_validator.py      # File & input validation
```

## Data Flow

```
1. File Upload → Security Validation → File Processing
2. Text Extraction → LLM Processing → Structured Data
3. Data Validation → Address Markup → ParsedCV Object
4. JSON Serialization → API Response
```

## Security Considerations
- **File Validation**: PDF/DOCX/TXT format verification and size limits
- **Content Security**: Anti-malware scanning and content sanitization  
- **Input Validation**: Text length limits and dangerous character removal
- **API Security**: Environment variable configuration and secure defaults

## LLM Integration
- **Primary Model**: claude-3-5-sonnet-20241022 (high accuracy parsing)
- **Fallback Strategy**: Basic pattern matching when LLM unavailable
- **Token Limits**: 4000-8000 tokens per request depending on operation
- **Prompt Version**: Loaded from default_prompt.txt with anti-hallucination protocols

## Dependencies

### Internal Modules
- `cv_parsing_service` - Core business logic
- `llm_integration.anthropic_client` - LLM processing
- `file_processors.document_processor` - File handling
- `security.input_validator` - Security validation

### External Packages
- `flask` - Web interface framework
- `requests` - HTTP client for Anthropic API
- `python-dotenv` - Environment variable loading
- `dataclasses` - Structured data models

## Configuration

### Environment Variables
```bash
ANTHROPIC_API_KEY=your_api_key_here  # Required for AI parsing
```

### File Limits
- **Max File Size**: 10MB
- **Supported Formats**: PDF, DOCX, TXT
- **Processing Timeout**: 60 seconds

## Error Handling

### Failure Modes
1. **LLM API Failures**: Rate limiting, timeouts, authentication
2. **File Processing**: Corrupted files, unsupported formats
3. **JSON Parsing**: Malformed LLM responses
4. **Memory Issues**: Large file processing

### Recovery Strategies
1. **Retry Logic**: 3 attempts with exponential backoff
2. **Fallback Models**: Basic pattern matching for text extraction
3. **JSON Repair**: Attempt to fix malformed JSON responses
4. **Graceful Degradation**: Return partial results with error notes

## Performance Considerations
- **LLM Token Usage**: ~500-2000 tokens per CV depending on length
- **Processing Time**: 5-30 seconds depending on file size and complexity
- **Memory Usage**: ~50-100MB per request during processing
- **Concurrent Requests**: Limited by Anthropic API rate limits

## Testing

### Unit Testing
```bash
cd /Users/eugenes/Desktop/Agentic-AI-CV-Analysis/agents/cv_parser
python test_direct.py  # Direct agent testing
```

### Web Interface Testing
```bash
python test_interface.py  # Start web interface on port 5004
```

### Integration Testing
- Upload test CV files via web interface
- Verify JSON output structure matches ParsedCV schema
- Test error handling with corrupted/invalid files
- Validate security measures with malicious content

## API Compatibility
All public methods maintain exact compatibility with existing integrations:
- **Gap Analysis Agent**: Consumes ParsedCV objects via HTTP API
- **Web Interface**: Uses Flask endpoints for file upload and parsing
- **Test Systems**: All existing test scripts continue to work unchanged

## Version History
- **v2.0.0**: Modular refactoring for guideline compliance
- **v1.0.0**: Original monolithic implementation (working baseline)