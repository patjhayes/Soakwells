#!/usr/bin/env python3
"""
Quick Test Script for Standalone Report Generator
Tests basic functionality without full interactive mode
"""

import os
import sys

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        from core_soakwell_analysis import simulate_soakwell_performance, read_hydrograph_data_from_content
        print("✅ core_soakwell_analysis imported successfully")
    except ImportError as e:
        print(f"❌ core_soakwell_analysis import failed: {e}")
        return False
    
    try:
        from lightweight_report_generator import generate_comprehensive_engineering_report_lightweight
        print("✅ lightweight_report_generator imported successfully")
    except ImportError as e:
        try:
            from comprehensive_report_generator import generate_comprehensive_engineering_report
            generate_comprehensive_engineering_report_lightweight = generate_comprehensive_engineering_report
            print("✅ comprehensive_report_generator imported successfully (fallback)")
        except ImportError as e2:
            print(f"❌ Report generator import failed: {e2}")
            return False
    
    return True

def test_storm_data():
    """Test if storm data is accessible"""
    print("\n🌧️  Testing storm data access...")
    
    drains_dir = "DRAINS"
    if not os.path.exists(drains_dir):
        print(f"❌ DRAINS directory not found")
        return False
    
    storm_files = [f for f in os.listdir(drains_dir) if f.endswith('.ts1')]
    if not storm_files:
        print(f"❌ No .ts1 files found in DRAINS directory")
        return False
    
    print(f"✅ Found {len(storm_files)} storm files")
    
    # Test loading one storm file
    try:
        test_file = os.path.join(drains_dir, storm_files[0])
        with open(test_file, 'r') as f:
            content = f.read()
        
        from core_soakwell_analysis import read_hydrograph_data_from_content
        hydrograph_data = read_hydrograph_data_from_content(content)
        
        if hydrograph_data and len(hydrograph_data.get('time_min', [])) > 0:
            print(f"✅ Successfully loaded test storm: {storm_files[0]}")
            print(f"   Data points: {len(hydrograph_data['time_min'])}")
            return True
        else:
            print(f"❌ Failed to parse storm data")
            return False
            
    except Exception as e:
        print(f"❌ Error loading storm data: {e}")
        return False

def test_analysis():
    """Test basic soakwell analysis"""
    print("\n⚙️  Testing soakwell analysis...")
    
    try:
        # Create simple test data
        test_hydrograph = {
            'time_min': [0, 5, 10, 15, 20, 25, 30],
            'total_flow': [0.0, 0.5, 1.0, 1.5, 1.0, 0.5, 0.0],  # m³/s
            'cat1240_flow': [0.0, 0.3, 0.6, 0.9, 0.6, 0.3, 0.0],
            'cat3_flow': [0.0, 0.2, 0.4, 0.6, 0.4, 0.2, 0.0]
        }
        
        from core_soakwell_analysis import simulate_soakwell_performance
        
        result = simulate_soakwell_performance(
            test_hydrograph,
            diameter=2.0,
            ks=4.63e-5,
            Sr=1.0,
            max_height=2.0,
            extend_to_hours=6
        )
        
        if result and 'stored_volume' in result:
            max_storage = max(result['stored_volume'])
            print(f"✅ Soakwell analysis successful")
            print(f"   Max storage: {max_storage:.2f} m³")
            print(f"   Data points: {len(result['time_min'])}")
            return True
        else:
            print(f"❌ Soakwell analysis failed - no results")
            return False
            
    except Exception as e:
        print(f"❌ Soakwell analysis error: {e}")
        return False

def test_report_generation():
    """Test basic report generation"""
    print("\n📄 Testing report generation...")
    
    try:
        # Create minimal test data
        test_soakwell_results = {
            'time_min': [0, 5, 10],
            'inflow_rate': [0.0, 1.0, 0.0],
            'stored_volume': [0.0, 2.0, 1.0],
            'outflow_rate': [0.0, 0.5, 0.5],
            'cumulative_inflow': [0.0, 300.0, 600.0],
            'cumulative_outflow': [0.0, 150.0, 450.0],
            'overflow_rate': [0.0, 0.0, 0.0],
            'water_level': [0.0, 0.6, 0.3],
            'max_volume': 6.28,
            'max_height': 2.0,
            'diameter': 2.0,
            'emptying_time_minutes': 60,
            'mass_balance': {
                'total_inflow_m3': 600.0,
                'total_outflow_m3': 450.0,
                'total_overflow_m3': 0.0,
                'mass_balance_error_percent': 0.05
            }
        }
        
        test_config = {
            'soakwell_diameter': 2.0,
            'soakwell_depth': 2.0,
            'num_soakwells': 1,
            'ks': 4.63e-5,
            'french_drain_length': 100.0
        }
        
        from lightweight_report_generator import generate_comprehensive_engineering_report_lightweight
        
        html_report = generate_comprehensive_engineering_report_lightweight(
            soakwell_results=test_soakwell_results,
            french_drain_results=None,
            storm_name="Test Storm",
            config=test_config,
            hydrograph_data=None
        )
        
        if html_report and len(html_report) > 1000:  # Reasonable report size
            print(f"✅ Report generation successful")
            print(f"   Report size: {len(html_report)} characters")
            return True
        else:
            print(f"❌ Report generation failed - insufficient content")
            return False
            
    except Exception as e:
        print(f"❌ Report generation error: {e}")
        return False

def run_quick_test():
    """Run all tests"""
    print("🚀 Quick Test of Standalone Report Generator")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Storm Data Test", test_storm_data),
        ("Analysis Test", test_analysis),
        ("Report Generation Test", test_report_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n📊 Test Results")
    print("=" * 20)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.0f}%")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready for report generation.")
        print("\n💡 Next steps:")
        print("   1. Run: python report_launcher.py")
        print("   2. Or run: python standalone_report_generator.py")
        print("   3. Or run: python batch_report_generator.py")
    else:
        print(f"\n⚠️  {total-passed} test(s) failed. Please resolve issues before proceeding.")

if __name__ == "__main__":
    try:
        run_quick_test()
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
