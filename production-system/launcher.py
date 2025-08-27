#!/usr/bin/env python3
"""
CV Analyzer Production System Launcher
Starts all components of the CV analysis system with one command.
"""

import os
import sys
import time
import signal
import socket
import subprocess
import threading
from pathlib import Path
from typing import List, Dict

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class SystemLauncher:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.project_root = Path(__file__).parent.parent
        self.services = {}
        
    def log(self, message: str, color: str = Colors.OKBLUE):
        timestamp = time.strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {message}{Colors.ENDC}")
    
    def check_port(self, port: int) -> bool:
        """Check if a port is available"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            return sock.connect_ex(('localhost', port)) != 0
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        self.log("🔍 Checking system dependencies...", Colors.HEADER)
        
        # Check Python
        if sys.version_info < (3, 9):
            self.log("❌ Python 3.9+ required", Colors.FAIL)
            return False
        self.log("✅ Python version OK", Colors.OKGREEN)
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ Node.js installed", Colors.OKGREEN)
            else:
                raise Exception()
        except:
            self.log("❌ Node.js not found", Colors.FAIL)
            return False
        
        # Check required ports
        required_ports = [5005, 5007, 5008, 8000, 3000]
        for port in required_ports:
            if not self.check_port(port):
                self.log(f"❌ Port {port} is already in use", Colors.FAIL)
                return False
        self.log("✅ All required ports available", Colors.OKGREEN)
        
        # Check API key
        if not os.getenv('ANTHROPIC_API_KEY'):
            self.log("❌ ANTHROPIC_API_KEY environment variable not set", Colors.FAIL)
            return False
        self.log("✅ Anthropic API key configured", Colors.OKGREEN)
        
        return True
    
    def start_agent(self, name: str, path: str, port: int, command: List[str]) -> bool:
        """Start an AI agent"""
        self.log(f"🚀 Starting {name} on port {port}...", Colors.OKCYAN)
        
        agent_path = self.project_root / "agents" / path
        if not agent_path.exists():
            self.log(f"❌ {name} directory not found: {agent_path}", Colors.FAIL)
            return False
        
        try:
            env = os.environ.copy()
            env['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY')
            
            process = subprocess.Popen(
                command,
                cwd=agent_path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(process)
            self.services[name] = {
                'process': process,
                'port': port,
                'status': 'starting'
            }
            
            # Wait a moment and check if process started successfully
            time.sleep(2)
            if process.poll() is None:
                self.log(f"✅ {name} started successfully", Colors.OKGREEN)
                self.services[name]['status'] = 'running'
                return True
            else:
                stdout, stderr = process.communicate()
                self.log(f"❌ {name} failed to start: {stderr}", Colors.FAIL)
                return False
                
        except Exception as e:
            self.log(f"❌ Failed to start {name}: {e}", Colors.FAIL)
            return False
    
    def start_backend(self) -> bool:
        """Start the Flask backend API"""
        self.log("🚀 Starting Backend API on port 8000...", Colors.OKCYAN)
        
        backend_path = self.project_root / "production-system" / "backend"
        if not backend_path.exists():
            self.log(f"❌ Backend directory not found: {backend_path}", Colors.FAIL)
            return False
        
        try:
            env = os.environ.copy()
            env.update({
                'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
                'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
                'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production'),
                'FLASK_ENV': 'development'
            })
            
            process = subprocess.Popen(
                ['python3', 'app.py'],
                cwd=backend_path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(process)
            self.services['Backend API'] = {
                'process': process,
                'port': 8000,
                'status': 'starting'
            }
            
            # Wait for backend to start
            time.sleep(3)
            if process.poll() is None:
                self.log("✅ Backend API started successfully", Colors.OKGREEN)
                self.services['Backend API']['status'] = 'running'
                return True
            else:
                stdout, stderr = process.communicate()
                self.log(f"❌ Backend API failed to start: {stderr}", Colors.FAIL)
                return False
                
        except Exception as e:
            self.log(f"❌ Failed to start Backend API: {e}", Colors.FAIL)
            return False
    
    def start_frontend(self) -> bool:
        """Start the React frontend"""
        self.log("🚀 Starting Frontend on port 3000...", Colors.OKCYAN)
        
        frontend_path = self.project_root / "production-system" / "frontend"
        if not frontend_path.exists():
            self.log(f"❌ Frontend directory not found: {frontend_path}", Colors.FAIL)
            return False
        
        try:
            process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd=frontend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(process)
            self.services['Frontend'] = {
                'process': process,
                'port': 3000,
                'status': 'starting'
            }
            
            # Wait for frontend to start
            time.sleep(5)
            if process.poll() is None:
                self.log("✅ Frontend started successfully", Colors.OKGREEN)
                self.services['Frontend']['status'] = 'running'
                return True
            else:
                stdout, stderr = process.communicate()
                self.log(f"❌ Frontend failed to start: {stderr}", Colors.FAIL)
                return False
                
        except Exception as e:
            self.log(f"❌ Failed to start Frontend: {e}", Colors.FAIL)
            return False
    
    def monitor_services(self):
        """Monitor running services"""
        while True:
            try:
                time.sleep(10)
                for name, service in self.services.items():
                    if service['process'].poll() is not None:
                        self.log(f"❌ {name} has stopped unexpectedly", Colors.FAIL)
                        service['status'] = 'stopped'
            except KeyboardInterrupt:
                break
    
    def print_status(self):
        """Print status of all services"""
        self.log("\n" + "="*60, Colors.HEADER)
        self.log("🎯 CV Analyzer Production System Status", Colors.HEADER)
        self.log("="*60, Colors.HEADER)
        
        for name, service in self.services.items():
            status_color = Colors.OKGREEN if service['status'] == 'running' else Colors.FAIL
            self.log(f"📋 {name:20} Port {service['port']:4} - {service['status'].upper()}", status_color)
        
        self.log("\n🌐 Application URLs:", Colors.HEADER)
        self.log("   Frontend:     http://localhost:3000", Colors.OKCYAN)
        self.log("   Backend API:  http://localhost:8000", Colors.OKCYAN)
        self.log("   CV Parser:    http://localhost:5005", Colors.OKCYAN)
        self.log("   JD Parser:    http://localhost:5007", Colors.OKCYAN)
        self.log("   Gap Analyst:  http://localhost:5008", Colors.OKCYAN)
        
        self.log("\n⚡ Commands:", Colors.HEADER)
        self.log("   Press Ctrl+C to stop all services", Colors.WARNING)
        self.log("="*60 + "\n", Colors.HEADER)
    
    def cleanup(self):
        """Stop all services gracefully"""
        self.log("\n🛑 Shutting down all services...", Colors.WARNING)
        
        for name, service in self.services.items():
            if service['process'].poll() is None:
                self.log(f"🔄 Stopping {name}...", Colors.WARNING)
                service['process'].terminate()
                
                # Wait for graceful shutdown
                try:
                    service['process'].wait(timeout=5)
                    self.log(f"✅ {name} stopped gracefully", Colors.OKGREEN)
                except subprocess.TimeoutExpired:
                    self.log(f"⚠️  Force killing {name}...", Colors.WARNING)
                    service['process'].kill()
                    service['process'].wait()
        
        self.log("✅ All services stopped", Colors.OKGREEN)
    
    def run(self):
        """Main launcher logic"""
        # Print header
        self.log("🎯 CV Analyzer Production System Launcher", Colors.HEADER)
        self.log("="*50, Colors.HEADER)
        
        # Check dependencies
        if not self.check_dependencies():
            self.log("❌ Dependency check failed. Please resolve issues and try again.", Colors.FAIL)
            return 1
        
        # Start services in order
        services_to_start = [
            ("CV Parser", "cv_parser", 5005, ['python3', 'test_interface.py']),
            ("JD Parser", "jd_parser", 5007, ['python3', 'test_interface.py']),
            ("Gap Analyst", "gap_analyst", 5008, ['python3', 'test_interface.py']),
        ]
        
        # Start AI agents
        for name, path, port, command in services_to_start:
            if not self.start_agent(name, path, port, command):
                self.cleanup()
                return 1
        
        # Start backend
        if not self.start_backend():
            self.cleanup()
            return 1
        
        # Start frontend
        if not self.start_frontend():
            self.cleanup()
            return 1
        
        # Print status
        self.print_status()
        
        # Set up signal handlers
        def signal_handler(signum, frame):
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start monitoring in background
        monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
        monitor_thread.start()
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.cleanup()
            return 0

def main():
    """Entry point"""
    launcher = SystemLauncher()
    return launcher.run()

if __name__ == "__main__":
    sys.exit(main())