# Claude Code Development Reference

## MANDATORY GUIDELINES
**ALWAYS reference `/Users/eugenes/Desktop/Agentic-AI-CV-Analysis/DEVELOPMENT-GUIDELINES.md` for ALL development work on this project.**

This file serves as a permanent reminder for Claude to follow the established development guidelines for the Agentic AI CV Analysis project.

## Core Principles
1. **200-line file limit** - Never exceed this limit
2. **Modular agent architecture** - Maintain clear boundaries
3. **Security-first approach** - Validate all inputs, authenticate agents
4. **LLM integration best practices** - Use fallbacks, circuit breakers
5. **Comprehensive error handling** - Graceful degradation always

## Before ANY Code Changes
1. ✅ Read DEVELOPMENT-GUIDELINES.md
2. ✅ Check agent-specific requirements
3. ✅ Implement security validations
4. ✅ Add proper error handling
5. ✅ Update README files
6. ✅ Test thoroughly

## Agent Structure Requirements
- Each agent must have: README.md, agent.py, test_interface.py
- Security validations for all inputs
- LLM integration with fallbacks
- Circuit breaker patterns
- Authentication mechanisms

## Quality Checklist
- [ ] All files under 200 lines
- [ ] Security implemented
- [ ] Error handling present
- [ ] Tests passing
- [ ] Documentation updated

**This document ensures consistent development practices across all sessions.**