#!/usr/bin/env python3
"""
Direct Streamlit Server Starter
Bypasses command line issues
"""

import os
import sys
import subprocess
import time

def setup_streamlit_config():
    """Setup Streamlit configuration files"""
    
    # Create .streamlit directory if it doesn't exist
    streamlit_dir = ".streamlit"
    if not os.path.exists(streamlit_dir):
        os.makedirs(streamlit_dir)
    
    # Create config.toml
    config_content = """[general]
email = ""

[browser]
gatherUsageStats = false

[server]
port = 8504
address = "localhost"
headless = false
runOnSave = true

[theme]
base = "light"
"""
    
    with open(os.path.join(streamlit_dir, "config.toml"), "w") as f:
        f.write(config_content)
    
    # Create credentials.toml
    credentials_content = """[general]
email = ""
"""
    
    with open(os.path.join(streamlit_dir, "credentials.toml"), "w") as f:
        f.write(credentials_content)
    
    print("✓ Streamlit configuration files created")

def start_dashboard():
    """Start the dashboard"""
    try:
        print("🌧️ Setting up Soakwell Dashboard...")
        
        # Setup config files
        setup_streamlit_config()
        
        # Set environment variables to skip setup
        os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        
        print("🚀 Starting dashboard server...")
        print("📱 Dashboard will be available at: http://localhost:8504")
        print("🛑 Press Ctrl+C to stop")
        print("-" * 60)
        
        # Import and run streamlit directly
        try:
            import streamlit.web.cli as stcli
            sys.argv = [
                "streamlit", 
                "run", 
                "test_dashboard.py",
                "--server.port", "8504",
                "--server.address", "localhost"
            ]
            stcli.main()
        except ImportError:
            # Fallback to subprocess
            subprocess.run([
                sys.executable, 
                "-m", "streamlit", 
                "run", 
                "test_dashboard.py",
                "--server.port", "8504"
            ])
            
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTry running manually:")
        print("python -m streamlit run test_dashboard.py --server.port 8504")

if __name__ == "__main__":
    start_dashboard()
