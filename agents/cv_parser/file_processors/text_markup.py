#!/usr/bin/env python3
"""
Text Markup for CV Highlighting

Adds invisible address markup to CV text content for intelligent highlighting
systems. Creates semantic addresses based on content analysis and structure.
"""

import re
from typing import List


class TextMarkup:
    """
    Adds semantic address markup to CV text for intelligent highlighting
    
    Analyzes CV text structure and adds invisible HTML-style address markers
    that enable precise highlighting of sections, positions, and content items.
    """
    
    def __init__(self):
        # Section keywords for detection
        self.section_keywords = [
            'EXPERIENCE', 'EDUCATION', 'SKILLS', 'SUMMARY', 'COMPETENCIES',
            'CERTIFICATIONS', 'PROJECTS', 'ACHIEVEMENTS', 'LANGUAGES',
            'OBJECTIVE', 'PROFILE', 'QUALIFICATIONS', 'EMPLOYMENT',
            'WORK HISTORY', 'CAREER', 'BACKGROUND'
        ]
        
        # Position/role keywords
        self.position_keywords = [
            'CEO', 'CTO', 'CFO', 'Manager', 'Director', 'Engineer', 'Analyst',
            'Lead', 'Senior', 'Junior', 'Associate', 'Coordinator', 'Specialist',
            'Developer', 'Architect', 'Consultant', 'Administrator'
        ]
        
        # Month patterns for date detection
        self.month_patterns = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
    
    def add_address_markup(self, cv_text: str) -> str:
        """
        Add invisible address markup to CV text for highlighting system
        
        Args:
            cv_text: Plain CV text content
            
        Returns:
            CV text with invisible address markup for highlighting
        """
        if not cv_text or not cv_text.strip():
            return cv_text
        
        # Split text into lines for processing
        lines = cv_text.split('\n')
        marked_lines = []
        
        print(f"🔖 Adding address markup to {len(lines)} lines of CV text")
        
        # Process each line with appropriate markup
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            
            # Skip empty lines
            if not stripped_line:
                marked_lines.append(line)
                continue
            
            # Determine line type and add appropriate markup
            line_type = self._classify_line(stripped_line, i)
            marked_line = self._add_line_markup(line, line_type, i)
            marked_lines.append(marked_line)
        
        marked_text = '\n'.join(marked_lines)
        print(f"✅ Address markup completed: {len(lines)} lines processed")
        
        return marked_text
    
    def _classify_line(self, line: str, line_number: int) -> str:
        """Classify line type for appropriate markup"""
        
        # Check for section headers (all caps or contains section keywords)
        if self._is_section_header(line):
            return 'section'
        
        # Check for company/position lines (contains dates or position titles)
        elif self._is_position_line(line):
            return 'position'
        
        # Check for bullet points or list items
        elif self._is_list_item(line):
            return 'item'
        
        # Check for contact/personal info (email, phone, etc.)
        elif self._is_contact_info(line):
            return 'contact'
        
        # Default to regular content line
        else:
            return 'line'
    
    def _is_section_header(self, line: str) -> bool:
        """Determine if line is a section header"""
        
        # Check if line is all uppercase (common for headers)
        if len(line) > 2 and line.isupper():
            return True
        
        # Check if line contains section keywords
        line_upper = line.upper()
        return any(keyword in line_upper for keyword in self.section_keywords)
    
    def _is_position_line(self, line: str) -> bool:
        """Determine if line contains position/company information"""
        
        # Check for year patterns (e.g., 2020, 2021-2023)
        if re.search(r'\b20\d{2}\b', line):
            return True
        
        # Check for month names
        if any(month in line for month in self.month_patterns):
            return True
        
        # Check for position keywords
        return any(keyword in line for keyword in self.position_keywords)
    
    def _is_list_item(self, line: str) -> bool:
        """Determine if line is a bullet point or list item"""
        
        # Check for common bullet point markers
        bullet_markers = ['•', '-', '*', '●', '○', '▪', '▫', '►', '⬥']
        if any(line.startswith(marker) for marker in bullet_markers):
            return True
        
        # Check for numbered lists
        if re.match(r'^\d+[\.\)]\s', line):
            return True
        
        # Check for indented items (common in experience sections)
        if line.startswith('  ') or line.startswith('\t'):
            return True
        
        return False
    
    def _is_contact_info(self, line: str) -> bool:
        """Determine if line contains contact information"""
        
        # Check for email addresses
        if re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', line):
            return True
        
        # Check for phone numbers
        if re.search(r'[\+]?[\s\(\-\)]?[\d\s\(\-\)]{10,}', line):
            return True
        
        # Check for URLs
        if re.search(r'https?://\S+|www\.\S+', line):
            return True
        
        # Check for LinkedIn
        if 'linkedin' in line.lower():
            return True
        
        return False
    
    def _add_line_markup(self, line: str, line_type: str, line_number: int) -> str:
        """Add appropriate markup based on line type"""
        
        markup_templates = {
            'section': '<!--cv_section_{0}-->{1}<!--/cv_section_{0}-->',
            'position': '<!--cv_position_{0}-->{1}<!--/cv_position_{0}-->',
            'item': '<!--cv_item_{0}-->{1}<!--/cv_item_{0}-->',
            'contact': '<!--cv_contact_{0}-->{1}<!--/cv_contact_{0}-->',
            'line': '<!--cv_line_{0}-->{1}<!--/cv_line_{0}-->'
        }
        
        template = markup_templates.get(line_type, markup_templates['line'])
        return template.format(line_number, line)
    
    def get_markup_statistics(self, marked_text: str) -> dict:
        """Get statistics about the markup applied"""
        
        stats = {
            'total_lines': marked_text.count('\n') + 1 if marked_text else 0,
            'sections': marked_text.count('<!--cv_section_'),
            'positions': marked_text.count('<!--cv_position_'),
            'items': marked_text.count('<!--cv_item_'),
            'contacts': marked_text.count('<!--cv_contact_'),
            'regular_lines': marked_text.count('<!--cv_line_')
        }
        
        return stats