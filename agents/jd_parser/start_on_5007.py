#!/usr/bin/env python3

# Import the JD Parser test interface and start on port 5007
from test_interface import app

if __name__ == '__main__':
    print("🚀 Starting JD Parser Agent on port 5007...")
    app.run(debug=False, host='0.0.0.0', port=5007)