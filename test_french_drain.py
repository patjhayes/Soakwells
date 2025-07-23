#!/usr/bin/env python3
"""
Test script for French drain integration
Verifies that all components work together correctly
"""

def test_french_drain_model():
    """Test the basic French drain model"""
    try:
        from french_drain_model import FrenchDrainModel
        
        # Create model instance
        drain = FrenchDrainModel()
        
        # Test basic properties
        print(f"✅ French drain model loaded successfully")
        print(f"   - Pipe diameter: {drain.pipe_diameter*1000:.0f}mm")
        print(f"   - Trench dimensions: {drain.trench_width*1000:.0f}mm × {drain.trench_depth*1000:.0f}mm")
        print(f"   - Soil permeability: {drain.soil_k:.2e} m/s")
        print(f"   - Storage per meter: {drain.effective_storage_volume:.3f} m³/m")
        
        # Test pipe capacity calculation
        pipe_props = drain.calculate_pipe_capacity(slope=0.005)
        print(f"   - Pipe flow capacity: {pipe_props['flow_capacity_full']:.4f} m³/s")
        
        # Test infiltration calculation
        infiltration_rate = drain.calculate_infiltration_rate(0.5)  # 0.5m water level
        print(f"   - Infiltration rate (0.5m level): {infiltration_rate:.6f} m³/s/m")
        
        return True
        
    except Exception as e:
        print(f"❌ French drain model test failed: {str(e)}")
        return False

def test_hydrograph_processing():
    """Test hydrograph data processing"""
    try:
        from french_drain_model import FrenchDrainModel
        
        # Create simple test hydrograph
        test_hydrograph = {
            'time': [0, 60, 120, 180, 240],  # 4 hours in seconds
            'flow': [0.0, 0.02, 0.05, 0.02, 0.0]  # Simple triangular storm
        }
        
        drain = FrenchDrainModel()
        
        # Test simulation
        results = drain.simulate_french_drain_response(
            test_hydrograph,
            pipe_slope=0.005,
            length=100.0
        )
        
        print(f"✅ Hydrograph simulation successful")
        print(f"   - Simulation duration: {results['time_hours'][-1]:.1f} hours")
        print(f"   - Total inflow: {results['performance']['total_inflow_m3']:.1f} m³")
        print(f"   - Total infiltrated: {results['performance']['total_infiltrated_m3']:.1f} m³")
        print(f"   - Infiltration efficiency: {results['performance']['infiltration_efficiency_percent']:.1f}%")
        print(f"   - Max storage: {results['performance']['max_trench_storage_m3']:.1f} m³")
        
        return True
        
    except Exception as e:
        print(f"❌ Hydrograph processing test failed: {str(e)}")
        return False

def test_streamlit_integration():
    """Test Streamlit integration components"""
    try:
        # Test if streamlit components can be imported
        import streamlit as st
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        print(f"✅ Streamlit components available")
        print(f"   - Streamlit version: {st.__version__}")
        
        # Test if integration module can be imported
        try:
            from french_drain_integration import add_french_drain_sidebar
            print(f"✅ French drain integration module loaded")
        except ImportError as e:
            print(f"⚠️  French drain integration module not available: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit integration test failed: {str(e)}")
        return False

def test_soil_parameters():
    """Test with your specific soil parameters"""
    try:
        from french_drain_model import FrenchDrainModel
        
        # Your site conditions
        your_soil_k = 4.63e-5  # m/s
        
        drain = FrenchDrainModel()
        drain.soil_k = your_soil_k  # Update to your soil
        
        # Test infiltration with your soil
        infiltration_rate = drain.calculate_infiltration_rate(0.45)  # Half trench depth
        
        print(f"✅ Site-specific soil analysis")
        print(f"   - Your soil permeability: {your_soil_k:.2e} m/s")
        print(f"   - Infiltration rate per meter: {infiltration_rate:.6f} m³/s/m")
        
        # Estimate for 100m system
        total_infiltration_capacity = infiltration_rate * 100
        print(f"   - Total capacity (100m): {total_infiltration_capacity:.4f} m³/s")
        
        # Compare with typical rainfall intensity
        typical_intensity_mm_hr = 20  # mm/hr
        catchment_area_m2 = 1000  # 1000 m² catchment
        runoff_coeff = 0.8
        
        peak_inflow = (typical_intensity_mm_hr / 1000 / 3600) * catchment_area_m2 * runoff_coeff
        print(f"   - Typical peak inflow (20mm/hr, 1000m²): {peak_inflow:.4f} m³/s")
        
        if total_infiltration_capacity > peak_inflow:
            print(f"   - ✅ 100m French drain can handle typical storms")
        else:
            required_length = peak_inflow / infiltration_rate
            print(f"   - ⚠️  Need {required_length:.0f}m for typical storms")
        
        return True
        
    except Exception as e:
        print(f"❌ Soil parameter test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("FRENCH DRAIN INTEGRATION TEST SUITE")
    print("="*50)
    
    tests = [
        ("French Drain Model", test_french_drain_model),
        ("Hydrograph Processing", test_hydrograph_processing),
        ("Streamlit Integration", test_streamlit_integration),
        ("Site-Specific Analysis", test_soil_parameters)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing: {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
        
        print()
    
    print("="*50)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! French drain integration is ready to use.")
        print("\nNext steps:")
        print("1. Run your soakwell dashboard: streamlit run soakwell_dashboard.py")
        print("2. Upload your .ts1 files")
        print("3. Enable 'French Drain Analysis' in the sidebar")
        print("4. Compare performance between soakwell and French drain systems")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
