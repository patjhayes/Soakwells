#!/usr/bin/env python3
"""
Test the exact import pattern used in the soakwell dashboard
"""

print("Testing dashboard import pattern...")

# Test the exact pattern from soakwell_dashboard.py
BALLAST_AVAILABLE = False
try:
    from ballast_storage_analysis import BallastStorageAnalyzer
    from ballast_integration import add_ballast_storage_ui, run_ballast_analysis, display_ballast_results
    BALLAST_AVAILABLE = True
    print("✅ BALLAST_AVAILABLE = True")
    print("✅ All ballast modules imported successfully!")
    
    # Test instantiation
    analyzer = BallastStorageAnalyzer()
    print(f"✅ BallastStorageAnalyzer created: void ratio = {analyzer.ballast_void_ratio}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    BALLAST_AVAILABLE = False
except Exception as e:
    print(f"❌ Other error: {e}")
    BALLAST_AVAILABLE = False

print(f"\nFinal result: BALLAST_AVAILABLE = {BALLAST_AVAILABLE}")

if BALLAST_AVAILABLE:
    print("🎉 SUCCESS: Ballast storage analysis should now be available in the dashboard!")
else:
    print("❌ FAILED: Ballast storage analysis is still not available.")
    print("   Check if running in the correct virtual environment.")
