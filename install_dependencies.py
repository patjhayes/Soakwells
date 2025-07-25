#!/usr/bin/env python3
"""
Quick Installation Script for Engineering Report Generator
Installs only the essential dependencies needed for standalone reports
"""

import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🔧 Installing Engineering Report Generator Dependencies")
    print("=" * 60)
    
    # Essential packages for standalone reports
    essential_packages = [
        'numpy',
        'pandas'
    ]
    
    # Optional packages for full dashboard functionality
    optional_packages = [
        'streamlit',
        'plotly'
    ]
    
    print("\n📦 Installing essential packages...")
    essential_success = 0
    for package in essential_packages:
        print(f"Installing {package}...", end=" ")
        if install_package(package):
            print("✅ Success")
            essential_success += 1
        else:
            print("❌ Failed")
    
    print(f"\n📊 Essential packages: {essential_success}/{len(essential_packages)} installed")
    
    if essential_success == len(essential_packages):
        print("✅ All essential packages installed successfully!")
        print("🎉 Standalone report generation is ready to use")
        
        install_optional = input("\nInstall optional packages for full dashboard features? (y/n): ").strip().lower()
        
        if install_optional == 'y':
            print("\n📦 Installing optional packages...")
            optional_success = 0
            for package in optional_packages:
                print(f"Installing {package}...", end=" ")
                if install_package(package):
                    print("✅ Success")
                    optional_success += 1
                else:
                    print("❌ Failed")
            
            print(f"\n📊 Optional packages: {optional_success}/{len(optional_packages)} installed")
            
            if optional_success == len(optional_packages):
                print("✅ All packages installed successfully!")
                print("🎉 Full dashboard functionality is available")
            else:
                print("⚠️  Some optional packages failed to install")
                print("📝 Standalone reports will still work")
        else:
            print("📝 Skipping optional packages - standalone reports will work")
    else:
        print("❌ Some essential packages failed to install")
        print("💡 Please check your Python and pip installation")
        return False
    
    print("\n🚀 Installation complete!")
    print("💡 Run: python report_launcher.py to start generating reports")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Installation cancelled by user")
    except Exception as e:
        print(f"\n❌ Installation error: {e}")
        print("💡 Please check your Python environment and try again")
