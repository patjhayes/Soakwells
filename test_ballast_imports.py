#!/usr/bin/env python3
"""
Test ballast storage module imports after installing dependencies
"""

print("Testing ballast storage module imports...")
print("=" * 50)

try:
    print("✅ Testing scipy import...")
    import scipy
    print(f"   scipy version: {scipy.__version__}")
except ImportError as e:
    print(f"❌ scipy import failed: {e}")

try:
    print("✅ Testing beautifulsoup4 import...")
    from bs4 import BeautifulSoup
    print(f"   beautifulsoup4 imported successfully")
except ImportError as e:
    print(f"❌ beautifulsoup4 import failed: {e}")

try:
    print("✅ Testing lxml import...")
    import lxml
    print(f"   lxml version: {lxml.__version__}")
except ImportError as e:
    print(f"❌ lxml import failed: {e}")

print("\n" + "=" * 50)
print("Testing ballast storage analysis modules...")

try:
    print("✅ Testing ballast_storage_analysis import...")
    from ballast_storage_analysis import BallastStorageAnalyzer
    print("   BallastStorageAnalyzer class imported successfully")
    
    # Test instantiation
    analyzer = BallastStorageAnalyzer()
    print(f"   Default ballast void ratio: {analyzer.ballast_void_ratio}")
    print(f"   Default effective porosity: {analyzer.effective_porosity:.3f}")
    
except ImportError as e:
    print(f"❌ ballast_storage_analysis import failed: {e}")
except Exception as e:
    print(f"❌ ballast_storage_analysis error: {e}")

try:
    print("✅ Testing ballast_integration import...")
    from ballast_integration import add_ballast_storage_ui, run_ballast_analysis, display_ballast_results
    print("   Ballast integration functions imported successfully")
    
except ImportError as e:
    print(f"❌ ballast_integration import failed: {e}")
except Exception as e:
    print(f"❌ ballast_integration error: {e}")

print("\n" + "=" * 50)
print("Testing dashboard integration...")

try:
    # Test the import pattern used in the dashboard
    BALLAST_AVAILABLE = False
    try:
        from ballast_storage_analysis import BallastStorageAnalyzer
        from ballast_integration import add_ballast_storage_ui, run_ballast_analysis, display_ballast_results
        BALLAST_AVAILABLE = True
        print("✅ Dashboard ballast integration: AVAILABLE")
    except ImportError as e:
        print(f"❌ Dashboard ballast integration: NOT AVAILABLE - {e}")
    except Exception as e:
        print(f"❌ Dashboard ballast integration: ERROR - {e}")
    
    if BALLAST_AVAILABLE:
        print("🎉 Ballast storage analysis is ready for use in the dashboard!")
    else:
        print("⚠️ Ballast storage analysis is still not available in the dashboard")
        
except Exception as e:
    print(f"❌ Dashboard integration test failed: {e}")

print("\n" + "=" * 50)
print("Import test completed!")
