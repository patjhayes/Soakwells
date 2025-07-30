#!/usr/bin/env python3
"""
Minimal test for ballast integration issues
"""

print("Testing minimal ballast imports...")

# Test 1: Basic dependencies
try:
    import streamlit as st
    print("✅ streamlit imported")
except Exception as e:
    print(f"❌ streamlit error: {e}")

try:
    import pandas as pd
    print("✅ pandas imported")
except Exception as e:
    print(f"❌ pandas error: {e}")

try:
    import numpy as np
    print("✅ numpy imported")
except Exception as e:
    print(f"❌ numpy error: {e}")

try:
    from ballast_storage_analysis import BallastStorageAnalyzer
    print("✅ BallastStorageAnalyzer imported")
except Exception as e:
    print(f"❌ BallastStorageAnalyzer error: {e}")

# Test 2: Check specific ballast_integration error
print("\nTesting ballast_integration step by step...")

try:
    # Try importing without running streamlit code
    import importlib.util
    spec = importlib.util.spec_from_file_location("ballast_integration", "ballast_integration.py")
    ballast_module = importlib.util.module_from_spec(spec)
    
    # Execute module but catch any streamlit-specific errors
    spec.loader.exec_module(ballast_module)
    print("✅ ballast_integration module loaded successfully")
    
    # Test function access
    if hasattr(ballast_module, 'add_ballast_storage_ui'):
        print("✅ add_ballast_storage_ui function found")
    else:
        print("❌ add_ballast_storage_ui function not found")
        
except Exception as e:
    print(f"❌ ballast_integration error: {e}")
    import traceback
    traceback.print_exc()

print("\nMinimal test completed.")
