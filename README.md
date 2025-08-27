# Agentic AI CV Analysis

A modular AI agent system for analyzing CVs against job descriptions, built with specialized agents for different tasks.

## Project Vision

This application will analyze and compare CVs to job descriptions, highlighting gaps in experience and skills through a multi-agent AI architecture.

## Architecture Overview

The system is built using a modular agentic approach where each AI agent focuses on a specific task:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CV Parser     │    │   JD Parser     │    │  Content        │
│     Agent       │    │     Agent       │    │  Matcher Agent  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐    ┌─────────────────┐
                    │   Highlight     │    │   Analysis      │
                    │     Agent       │    │     Agent       │
                    └─────────────────┘    └─────────────────┘
```

## Planned Agents

1. **CV Parser Agent**: Extracts structured data from CV documents
2. **Job Description Parser Agent**: Analyzes and structures job requirements
3. **Content Matching Agent**: Compares CV content against job requirements
4. **Highlight Agent**: Identifies gaps and matches for visualization
5. **Analysis Agent**: Generates insights and recommendations

## Project Structure

```
agents/          # Individual AI agents
core/           # Shared utilities and base classes
tests/          # Unit and integration tests
docs/           # Documentation
examples/       # Example usage and sample data
configs/        # Configuration files
```

## Development Approach

Building step by step:
1. Start with individual specialized agents
2. Create agent orchestration system
3. Build testing framework
4. Integrate into full application
5. Add UI for visualization

## Getting Started

Coming soon...