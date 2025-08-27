#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from agent import CVParserAgent

# Test CV text
cv_text = """John Smith
Software Engineer
john@email.com
(555) 123-4567
San Francisco, CA

EXPERIENCE:
Senior Developer at TechCorp (2020-2024)
- Built web applications with React and Node.js
- Led team of 3 developers
- Implemented REST APIs

SKILLS:
- Python, JavaScript, TypeScript
- React, Node.js, Express
- PostgreSQL, MongoDB

EDUCATION:
BS Computer Science - UC Berkeley (2020)
"""

print("🔧 Testing CV Parser Agent directly...")
print(f"📄 CV text length: {len(cv_text)}")

# Create agent
agent = CVParserAgent()
print(f"🤖 Agent version: {agent.version}")
print(f"🧠 Using model: {agent.model_name}")

# Parse CV
try:
    result = agent.parse_cv(cv_text)
    print(f"✅ Parse completed!")
    print(f"📋 Name: {result.full_name}")
    print(f"📧 Email: {result.email}")
    print(f"📞 Phone: {result.phone}")
    print(f"🎯 Skills: {result.key_skills[:3]}...")
    print(f"💼 Work Experience: {len(result.work_experience)} entries")
    print(f"🎓 Education: {len(result.education)} entries")
    print(f"✨ Confidence: {result.confidence_score}")
    if result.parsing_notes:
        print(f"📝 Notes: {result.parsing_notes}")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    print(f"❌ Error type: {type(e)}")