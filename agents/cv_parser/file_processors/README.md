# File Processors Module

## Purpose
Handles file format processing and text extraction for CV documents. Manages PDF, DOCX, and text files while providing address markup for intelligent highlighting systems.

## Components

### document_processor.py
Core file processing engine that validates file formats, extracts text content, and handles different document types safely.

**Key Features:**
- Multi-format support (PDF, DOCX, TXT)
- File format validation and integrity checks
- Error handling for corrupted or invalid files
- Memory-efficient processing for large documents
- Fallback text extraction methods

### text_markup.py
Adds invisible address markup to CV text content for the highlighting system. Creates semantic addresses that map to specific CV sections and content areas.

**Key Features:**
- Intelligent section detection (experience, education, skills)
- Line-by-line address markup generation
- Pattern-based content classification
- Address mapping for highlighting system
- Preservation of original text formatting

## Data Flow

```
1. File Upload → Format Validation → Security Checks
2. Binary Content → Text Extraction → Content Cleaning  
3. Extracted Text → Address Markup → Marked Content
4. Processed Text → Return to Parsing Service
```

## Address Markup System

The text markup creates semantic addresses for intelligent highlighting:

```
CV Content Types → Address Patterns:
├── Section Headers → cv_section_{line_number}
├── Company/Position → cv_position_{line_number}  
├── Bullet Points → cv_item_{line_number}
└── Regular Lines → cv_line_{line_number}
```

## Security Considerations
- File size limits and validation
- Format verification against file signatures
- Content sanitization before processing
- Memory usage monitoring for large files

## Error Handling
- Corrupted file recovery attempts
- Format mismatch detection and reporting
- Memory overflow prevention
- Graceful degradation for unsupported content

## Performance
- Streaming processing for large files
- Memory-efficient text extraction
- Caching of processed content
- Parallel processing capabilities where safe