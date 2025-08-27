# AI Agents

This directory contains specialized AI agents, each focusing on a specific task in the CV analysis pipeline.

## Agent Overview

### 1. CV Parser Agent (`cv_parser/`)
**Purpose**: Extract and structure information from CV documents
- Parse PDF/Word/Text CVs
- Extract skills, experience, education, certifications
- Normalize and structure data
- Handle various CV formats

### 2. Job Description Parser Agent (`jd_parser/`)
**Purpose**: Analyze and structure job requirements
- Parse job descriptions from various sources
- Categorize requirements (must-have vs nice-to-have)
- Extract skills, experience levels, responsibilities
- Separate job requirements from company info

### 3. Content Matcher Agent (`content_matcher/`)
**Purpose**: Compare CV content against job requirements
- Match skills between CV and JD
- Compare experience levels
- Assess qualification alignment
- Generate match scores and relevance ratings

### 4. Gap Analyzer Agent (`gap_analyzer/`)
**Purpose**: Identify missing skills and experience gaps
- Highlight missing requirements
- Categorize gap severity (critical vs minor)
- Suggest skill development priorities
- Identify transferable skills

### 5. Recommendation Engine Agent (`recommendation_engine/`)
**Purpose**: Generate insights and actionable recommendations
- Provide improvement suggestions
- Recommend skill development paths
- Generate application strategies
- Create personalized feedback

## Agent Communication

Agents communicate through standardized interfaces:
- **Input**: Structured data objects
- **Output**: JSON responses with results and metadata
- **Error Handling**: Consistent error reporting
- **Logging**: Detailed execution logs

## Development Principles

- **Single Responsibility**: Each agent has one clear purpose
- **Modularity**: Agents work independently
- **Testability**: Easy to unit test individual agents
- **Scalability**: Can be deployed as microservices
- **Configurability**: Behavior controlled through config files