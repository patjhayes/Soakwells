#!/usr/bin/env python3
"""
Dashboard Launcher
Starts the Streamlit soakwell dashboard
"""

import subprocess
import sys
import os

def start_dashboard():
    """Start the Streamlit dashboard"""
    try:
        print("🌧️ Starting Soakwell Design Dashboard...")
        print("📱 The dashboard will open in your web browser at: http://localhost:8502")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 70)
        
        # Change to script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Check if we're in a virtual environment
        venv_python = os.path.join(script_dir, ".venv", "Scripts", "python.exe")
        
        if os.path.exists(venv_python):
            python_executable = venv_python
            print(f"Using virtual environment: {venv_python}")
        else:
            python_executable = sys.executable
            print(f"Using system Python: {python_executable}")
        
        # Start Streamlit
        cmd = [
            python_executable, 
            "-m", "streamlit", "run", 
            "soakwell_dashboard.py",
            "--server.port", "8502",
            "--server.address", "localhost"
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Streamlit is installed: pip install streamlit")
        print("2. Try running manually: python -m streamlit run soakwell_dashboard.py")

if __name__ == "__main__":
    start_dashboard()
