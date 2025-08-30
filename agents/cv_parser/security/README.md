# Security Module

## Purpose
Provides comprehensive input validation, file security checks, and content sanitization for the CV parser agent. Implements multi-layered security to protect against malicious content and ensure safe processing.

## Components

### input_validator.py
Comprehensive security validation for all inputs to the CV parser system including file uploads, text content, and user parameters.

**Key Security Features:**
- File type and size validation
- Malicious content detection and scanning
- File signature verification against spoofing
- Content sanitization and dangerous character removal
- Memory protection against large content attacks
- Input length limits and boundary checks

## Security Layers

```
Security Validation Flow:
1. File Upload → Format & Size Check → Signature Verification
2. Content Scan → Malware Detection → Dangerous Pattern Check
3. Text Input → Length Limits → Character Sanitization
4. Parameter Validation → Type Checking → Range Validation
```

## Threat Protection

### File Upload Security
- **Format Validation**: Only PDF, DOCX, TXT allowed
- **Size Limits**: 10MB maximum file size
- **Signature Verification**: Header bytes match extension
- **Malware Scanning**: Pattern-based malicious content detection

### Content Security
- **Script Injection**: Removes JavaScript, VBScript, PHP code
- **Code Execution**: Blocks eval(), exec(), ActiveX patterns
- **Buffer Overflow**: Content length limits and memory protection
- **Path Traversal**: Filename sanitization and path validation

### Input Sanitization
- **Text Processing**: Dangerous character removal and escaping
- **Length Limits**: Maximum content size enforcement
- **Encoding Safety**: UTF-8 validation and fallback handling
- **Parameter Validation**: Type and range checking for all inputs

## Configuration

### Security Limits
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_TEXT_LENGTH = 50000          # 50KB
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}
```

### Dangerous Patterns
- Script tags and JavaScript execution
- Server-side code (PHP, ASP, JSP)
- System commands and shell execution
- ActiveX components and macros
- SQL injection patterns

## Error Handling
- Security violations logged with context
- Graceful rejection of malicious content
- Detailed validation failure reporting
- Safe fallback for edge cases

## Performance Impact
- Minimal overhead for legitimate files
- Fast pattern matching for threat detection
- Memory-efficient content scanning
- Optimized file signature verification