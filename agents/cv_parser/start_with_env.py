#!/usr/bin/env python3
"""
Start CV parser with .env file loaded
"""
import os
from pathlib import Path

# Load .env file
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

# Import and run the main interface
from test_interface import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)