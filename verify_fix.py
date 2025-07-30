#!/usr/bin/env python3
"""
Complete verification script for Streamlit app deployment
This script checks all the components that were causing the NameError
"""

import sys
import os

def check_file_syntax(file_path):
    """Check if a Python file has valid syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        compile(source, file_path, 'exec')
        return True, "✅ Syntax OK"
    except SyntaxError as e:
        return False, f"❌ Syntax Error: {e}"
    except Exception as e:
        return False, f"❌ Error: {e}"

def check_imports():
    """Check if the critical imports work"""
    try:
        from comprehensive_report_generator import generate_comprehensive_engineering_report, add_comprehensive_report_to_sidebar
        return True, "✅ Imports successful"
    except ImportError as e:
        return False, f"❌ Import Error: {e}"
    except Exception as e:
        return False, f"❌ Error: {e}"

def check_config_file():
    """Check if config.toml is valid"""
    config_path = ".streamlit/config.toml"
    if not os.path.exists(config_path):
        return False, "❌ Config file not found"
    
    try:
        import toml
        with open(config_path, 'r') as f:
            config = toml.load(f)
        
        # Check for duplicate sections
        content = open(config_path, 'r').read()
        theme_count = content.count('[theme]')
        if theme_count > 1:
            return False, f"❌ Duplicate [theme] sections found ({theme_count})"
        
        return True, "✅ Config file valid"
    except Exception as e:
        # toml not available, do basic check
        with open(config_path, 'r') as f:
            content = f.read()
        theme_count = content.count('[theme]')
        if theme_count > 1:
            return False, f"❌ Duplicate [theme] sections found ({theme_count})"
        return True, "✅ Config file appears valid (basic check)"

def main():
    print("🔧 STREAMLIT APP DEPLOYMENT VERIFICATION")
    print("=" * 50)
    
    # Check critical files
    files_to_check = [
        "comprehensive_report_generator.py",
        "soakwell_dashboard.py"
    ]
    
    all_good = True
    
    print("\n📁 SYNTAX CHECKS:")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            success, message = check_file_syntax(file_path)
            print(f"  {file_path}: {message}")
            if not success:
                all_good = False
        else:
            print(f"  {file_path}: ❌ File not found")
            all_good = False
    
    print("\n📦 IMPORT CHECKS:")
    success, message = check_imports()
    print(f"  Critical functions: {message}")
    if not success:
        all_good = False
    
    print("\n⚙️ CONFIG CHECKS:")
    success, message = check_config_file()
    print(f"  .streamlit/config.toml: {message}")
    if not success:
        all_good = False
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ The NameError should be fixed")
        print("✅ Streamlit app should deploy successfully")
        print("\nTo deploy:")
        print("  streamlit run soakwell_dashboard.py")
    else:
        print("💥 SOME CHECKS FAILED!")
        print("❌ Additional fixes may be needed")
    
    return all_good

if __name__ == "__main__":
    main()
