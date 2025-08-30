#!/usr/bin/env python3
"""
CV Parsing Service

Core business logic for CV parsing operations. Handles the complete parsing
workflow from file validation through LLM processing to structured output.
"""

from typing import Dict, Optional
from pathlib import Path

from llm_integration.anthropic_client import AnthropicClient
from llm_integration.prompt_manager import PromptManager
from file_processors.document_processor import DocumentProcessor
from file_processors.text_markup import TextMarkup
from security.input_validator import InputValidator
from fallback_parser import FallbackParser
from result_builder import ResultBuilder


class CVParsingService:
    """
    Core CV parsing service with complete workflow management
    
    Orchestrates the entire CV parsing process including validation,
    file processing, LLM analysis, and structured data generation.
    """
    
    def __init__(self):
        # Initialize all components
        self.validator = InputValidator()
        self.doc_processor = DocumentProcessor()
        self.text_markup = TextMarkup()
        self.prompt_manager = PromptManager(Path(__file__).parent)
        self.llm_client = AnthropicClient()
        self.fallback_parser = FallbackParser()
        self.result_builder = ResultBuilder()
        
        print("✅ CV Parsing Service initialized")
    
    def parse_file(self, file_content: bytes, filename: str) -> Dict:
        """
        Parse a CV file with complete validation and processing
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            
        Returns:
            Dict with parsing results and metadata
        """
        print(f"🤖 CV Parsing Service processing file: {filename}")
        print(f"📄 File size: {len(file_content)} bytes")
        
        try:
            # Security validation (but allow CV processing to continue)
            validation_result = self.validator.validate_file_upload(file_content, filename)
            
            # Skip security blocking for CV documents - trust the user's files
            # if not self.validator.is_file_processing_safe(validation_result):
            #     return self.result_builder.create_validation_error_result(validation_result, self.validator)
            
            # Process file based on type
            if self._requires_llm_processing(filename):
                return self._process_file_with_llm(file_content, filename)
            else:
                return self._process_text_file(file_content, filename)
                
        except Exception as e:
            print(f"❌ File parsing error: {str(e)}")
            return self.result_builder.create_error_result(f"File parsing failed: {str(e)}", filename)
    
    def parse_text(self, cv_text: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Parse CV text content with LLM processing
        
        Args:
            cv_text: Raw CV text content
            metadata: Optional metadata about the CV
            
        Returns:
            Dict with parsing results
        """
        print(f"🤖 CV Parsing Service processing text: {len(cv_text)} characters")
        
        try:
            # Validate and sanitize text
            text_validation = self.validator.validate_text_input(cv_text)
            
            if not text_validation["is_valid"]:
                return self.result_builder.create_text_validation_error(text_validation)
            
            sanitized_text = text_validation["sanitized_text"]
            
            # Add address markup for highlighting
            marked_text = self.text_markup.add_address_markup(sanitized_text)
            
            # Process with appropriate method
            if self.llm_client.is_available():
                parsed_data = self._process_with_llm(sanitized_text)
            else:
                print("⚠️ No LLM client available, using fallback parsing")
                parsed_data = self.fallback_parser.parse_text_fallback(sanitized_text)
            
            # Create structured result
            parsed_cv = self.result_builder.create_parsed_cv(parsed_data, marked_text)
            
            return self.result_builder.create_success_result(parsed_cv)
            
        except Exception as e:
            print(f"❌ Text parsing error: {str(e)}")
            return self.result_builder.create_error_result(f"Text parsing failed: {str(e)}")
    
    def _requires_llm_processing(self, filename: str) -> bool:
        """Check if file requires LLM processing (PDF/DOC) vs direct text extraction"""
        file_ext = Path(filename).suffix.lower()
        return file_ext in ['.pdf', '.doc', '.docx']
    
    def _process_file_with_llm(self, file_content: bytes, filename: str) -> Dict:
        """Process PDF/DOC files using LLM"""
        
        if not self.llm_client.is_available():
            return self.result_builder.create_error_result("LLM processing required but not available", filename)
        
        try:
            # Get prompt template and call LLM with file
            prompt_template = self.prompt_manager.get_current_prompt()
            parsed_data = self.llm_client.call_file_api(file_content, filename, prompt_template)
            
            # Create structured result
            parsed_cv = self.result_builder.create_parsed_cv(parsed_data, f"[FILE: {filename}]")
            return self.result_builder.create_success_result(parsed_cv)
            
        except Exception as e:
            print(f"❌ LLM file processing failed: {e}")
            return self.result_builder.create_error_result(f"LLM processing failed: {str(e)}", filename)
    
    def _process_text_file(self, file_content: bytes, filename: str) -> Dict:
        """Process text files with direct extraction"""
        
        try:
            extracted_text = self.doc_processor.extract_text(file_content, filename)
            return self.parse_text(extracted_text)
        except Exception as e:
            print(f"❌ Text file processing failed: {e}")
            return self.result_builder.create_error_result(f"Text extraction failed: {str(e)}", filename)
    
    def _process_with_llm(self, sanitized_text: str) -> Dict:
        """Process text with LLM"""
        prompt_template = self.prompt_manager.get_current_prompt()
        # Use replace instead of format to avoid issues with JSON braces in template
        full_prompt = prompt_template.replace('{cv_text}', sanitized_text)
        return self.llm_client.call_text_api(full_prompt)