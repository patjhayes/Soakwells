#!/usr/bin/env python3
"""
Test script to verify that the comprehensive_report_generator imports work correctly
"""

def test_imports():
    try:
        from comprehensive_report_generator import generate_comprehensive_engineering_report, add_comprehensive_report_to_sidebar
        print("✅ SUCCESS: Both functions imported successfully!")
        
        # Test that functions are callable
        print(f"✅ generate_comprehensive_engineering_report is callable: {callable(generate_comprehensive_engineering_report)}")
        print(f"✅ add_comprehensive_report_to_sidebar is callable: {callable(add_comprehensive_report_to_sidebar)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Testing comprehensive_report_generator imports...")
    success = test_imports()
    if success:
        print("\n🎉 All tests passed! The NameError should be fixed.")
    else:
        print("\n💥 Tests failed! There are still issues to resolve.")
