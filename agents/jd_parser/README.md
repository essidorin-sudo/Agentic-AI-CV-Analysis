# JD Parser Agent

Specialized AI agent for parsing and structuring job descriptions into meaningful, analyzable sections.

## Features

- **Intelligent Content Analysis**: Automatically categorizes job description content into structured sections
- **Skills Extraction**: Identifies both required and preferred skills from context
- **Requirements Classification**: Separates must-have vs nice-to-have qualifications
- **Confidence Scoring**: Provides quality metrics for parsing results
- **Isolated Testing**: Standalone testing interface for prompt iteration

## Agent Capabilities

### Content Categorization
- Job title and basic information extraction
- Key responsibilities identification
- Required vs preferred qualifications separation
- Skills extraction (technical and soft skills)
- Work environment details
- Company information filtering

### Output Structure
```python
ParsedJobDescription:
    job_title: str
    company_name: str
    location: str
    job_summary: List[str]
    required_skills: List[str]
    preferred_skills: List[str]
    required_experience: List[str]
    required_education: List[str]
    required_qualifications: List[str]
    preferred_qualifications: List[str]
    key_responsibilities: List[str]
    work_environment: List[str]
    company_info: List[str]
    team_info: List[str]
    benefits: List[str]
    confidence_score: float
    parsing_notes: List[str]
```

## Quick Start

### 1. Install Dependencies
```bash
cd agents/jd_parser
pip install -r requirements.txt
```

### 2. Test the Agent (Command Line)
```bash
python agent.py
```

### 3. Launch Testing Interface
```bash
python test_interface.py
```
Then open http://localhost:5000 in your browser.

### 4. Use Programmatically
```python
from agent import JDParserAgent

agent = JDParserAgent()
result = agent.parse_job_description("Your job description text here...")
print(agent.to_json(result))
```

## Testing Interface Features

### 🎯 Interactive Testing
- **Sample Job Descriptions**: Pre-loaded examples for quick testing
- **Real-time Parsing**: Instant results with structured output
- **Confidence Metrics**: Visual indicators of parsing quality
- **Multiple Views**: Overview, skills, requirements, and raw JSON

### 🔧 Development Tools
- **Prompt Iteration**: Easy testing of different parsing approaches
- **Results Comparison**: Compare outputs between different JD formats
- **Error Handling**: Detailed error messages and debugging info
- **Export Options**: JSON export for further analysis

## Configuration

The agent can be configured with custom patterns and keywords:

```python
config = {
    'custom_skills': ['Domain-specific skill', 'Industry knowledge'],
    'company_indicators': ['custom company pattern'],
    'confidence_threshold': 0.7
}

agent = JDParserAgent(config=config)
```

## Architecture

### Parsing Pipeline
1. **Text Preprocessing**: Clean and normalize input text
2. **Line Analysis**: Categorize each line based on content patterns
3. **Skills Extraction**: Identify technical and soft skills
4. **Structure Assembly**: Organize into standardized format
5. **Quality Assessment**: Calculate confidence metrics

### Pattern Recognition
- **Regex-based Classification**: Pattern matching for content types
- **Keyword Analysis**: Context-aware skill detection
- **Heuristic Rules**: Logic for requirement vs preference classification
- **Confidence Scoring**: Multi-factor quality assessment

## Integration

This agent is designed to work independently or as part of the larger CV analysis pipeline:

```python
# Standalone usage
parsed_jd = jd_agent.parse_job_description(job_text)

# Pipeline integration (future)
# content_matches = content_matcher.match(cv_data, parsed_jd)
# gaps = gap_analyzer.analyze(content_matches)
```

## Development

### Adding New Patterns
Edit the `_init_patterns()` method in `agent.py` to add new recognition patterns:

```python
self.custom_patterns = [
    r"your custom pattern",
    r"another pattern"
]
```

### Extending Output Structure
Modify the `ParsedJobDescription` dataclass to add new fields:

```python
@dataclass
class ParsedJobDescription:
    # ... existing fields ...
    new_field: List[str]
```

### Testing Changes
Use the web interface to test changes immediately:
1. Modify the agent code
2. Restart the test server
3. Test with various job descriptions
4. Compare results and iterate

## Future Enhancements

- [ ] AI/LLM integration for better context understanding
- [ ] Industry-specific parsing optimization
- [ ] Multi-language support
- [ ] Integration with job board APIs
- [ ] Advanced confidence scoring algorithms
- [ ] Custom prompt templates
- [ ] Batch processing capabilities