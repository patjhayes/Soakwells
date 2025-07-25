#!/usr/bin/env python3
"""
Engineering Report Launcher
Easy-to-use launcher for generating infiltration system analysis reports
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required Python modules are available"""
    required_modules = [
        'numpy', 'pandas'
    ]
    
    optional_modules = [
        'plotly', 'streamlit'  # These are optional for standalone reports
    ]
    
    missing_modules = []
    missing_optional = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    for module in optional_modules:
        try:
            __import__(module)
        except ImportError:
            missing_optional.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print(f"💡 Install them with: pip install {' '.join(missing_modules)}")
        return False
    
    if missing_optional:
        print(f"⚠️  Missing optional modules: {', '.join(missing_optional)}")
        print(f"💡 For full dashboard features, install: pip install {' '.join(missing_optional)}")
        print(f"✅ Standalone reports will work without these modules")
    else:
        print("✅ All modules available (including optional dashboard features)")
    
    return True

def check_files():
    """Check if required files are present"""
    required_files = [
        'soakwell_dashboard.py',
        'comprehensive_report_generator.py',
        'standalone_report_generator.py',
        'batch_report_generator.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    return True

def check_storm_data():
    """Check if storm data is available"""
    drains_dir = "DRAINS"
    if not os.path.exists(drains_dir):
        print(f"❌ DRAINS directory not found")
        print(f"💡 Please ensure the DRAINS folder with .ts1 files is present")
        return False
    
    ts1_files = [f for f in os.listdir(drains_dir) if f.endswith('.ts1')]
    if not ts1_files:
        print(f"❌ No .ts1 storm files found in DRAINS directory")
        return False
    
    print(f"✅ Found {len(ts1_files)} storm files in DRAINS directory")
    return True

def show_menu():
    """Display the main menu"""
    print("\n🌧️  Engineering Report Generator")
    print("=" * 40)
    print("1. Interactive Single Report Generator")
    print("   → Generate report for specific storm/configuration")
    print()
    print("2. Batch Report Generator")
    print("   → Generate reports for multiple standard configurations")
    print()
    print("3. Check System Status")
    print("   → Verify all dependencies and files are available")
    print()
    print("4. Exit")
    print()

def run_interactive_generator():
    """Run the interactive single report generator"""
    print("\n🔄 Starting Interactive Report Generator...")
    try:
        import standalone_report_generator
        standalone_report_generator.main()
    except Exception as e:
        print(f"❌ Error running interactive generator: {e}")

def run_batch_generator():
    """Run the batch report generator"""
    print("\n🔄 Starting Batch Report Generator...")
    try:
        import batch_report_generator
        batch_report_generator.generate_batch_reports()
    except Exception as e:
        print(f"❌ Error running batch generator: {e}")

def check_system_status():
    """Check and display system status"""
    print("\n🔍 System Status Check")
    print("-" * 30)
    
    # Check dependencies
    print("📦 Checking Python dependencies...")
    deps_ok = check_dependencies()
    if deps_ok:
        print("✅ All required Python modules are available")
    
    # Check files
    print("\n📁 Checking required files...")
    files_ok = check_files()
    if files_ok:
        print("✅ All required Python files are present")
    
    # Check storm data
    print("\n🌧️  Checking storm data...")
    storm_ok = check_storm_data()
    
    # Overall status
    print(f"\n📊 Overall Status:")
    if deps_ok and files_ok and storm_ok:
        print("✅ System ready for report generation")
        return True
    else:
        print("❌ System not ready - please resolve the issues above")
        return False

def main():
    """Main launcher function"""
    print("🚀 Engineering Report System Launcher")
    print("North Fremantle Pedestrian Infrastructure Project")
    
    while True:
        show_menu()
        
        try:
            choice = input("Select option (1-4): ").strip()
            
            if choice == '1':
                if check_system_status():
                    run_interactive_generator()
                else:
                    print("\n⚠️  Please resolve system issues before proceeding")
            
            elif choice == '2':
                if check_system_status():
                    run_batch_generator()
                else:
                    print("\n⚠️  Please resolve system issues before proceeding")
            
            elif choice == '3':
                check_system_status()
            
            elif choice == '4':
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        input("Press Enter to exit...")
