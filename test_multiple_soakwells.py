#!/usr/bin/env python3
"""
Test script for multiple soakwell functionality
"""

import sys
sys.path.append(r"c:\Users\Patrick.Hayes\OneDrive - Aurecon Group\Documents\North Fremantle Ped")

from soakwell_dashboard import simulate_soakwell_performance, scale_multiple_soakwell_results

def test_multiple_soakwells():
    """Test the multiple soakwell scaling functionality"""
    
    # Create simple test hydrograph data
    test_hydrograph = {
        'time_min': [0, 5, 10, 15, 20, 25, 30],
        'total_flow': [0.0, 0.5, 1.0, 1.5, 1.0, 0.5, 0.0]  # m³/s
    }
    
    print("Testing Multiple Soakwell Functionality")
    print("=" * 50)
    
    # Test with single soakwell (1.2m diameter, 1.2m deep)
    print("\n1. Single Soakwell Analysis:")
    single_result = simulate_soakwell_performance(
        test_hydrograph,
        diameter=1.2,
        ks=1e-5,  # Medium soil
        Sr=1.0,
        max_height=1.2
    )
    
    print(f"   Max Volume: {single_result['max_volume']:.2f} m³")
    print(f"   Peak Storage: {max(single_result['stored_volume']):.2f} m³")
    print(f"   Peak Overflow: {max(single_result['overflow_rate']):.4f} m³/s")
    
    # Test with multiple soakwells (3 units of 1.2m diameter)
    print("\n2. Multiple Soakwell Analysis (3x 1.2m units):")
    
    # Distribute flow among 3 soakwells
    num_soakwells = 3
    distributed_hydrograph = {
        'time_min': test_hydrograph['time_min'],
        'total_flow': [flow / num_soakwells for flow in test_hydrograph['total_flow']]
    }
    
    # Analyze single soakwell with reduced flow
    distributed_result = simulate_soakwell_performance(
        distributed_hydrograph,
        diameter=1.2,
        ks=1e-5,
        Sr=1.0,
        max_height=1.2
    )
    
    # Scale results back
    scaled_result = scale_multiple_soakwell_results(
        distributed_result, 
        num_soakwells, 
        test_hydrograph
    )
    
    print(f"   Individual Max Volume: {scaled_result['individual_max_volume']:.2f} m³")
    print(f"   Total Max Volume: {scaled_result['max_volume']:.2f} m³")
    print(f"   Individual Peak Storage: {max(distributed_result['stored_volume']):.2f} m³")
    print(f"   Total Peak Storage: {max(scaled_result['stored_volume']):.2f} m³")
    print(f"   Total Peak Overflow: {max(scaled_result['overflow_rate']):.4f} m³/s")
    
    # Compare performance
    print("\n3. Performance Comparison:")
    single_overflow = max(single_result['overflow_rate'])
    multiple_overflow = max(scaled_result['overflow_rate'])
    
    print(f"   Single unit overflow: {single_overflow:.4f} m³/s")
    print(f"   Multiple units overflow: {multiple_overflow:.4f} m³/s")
    
    if multiple_overflow < single_overflow:
        reduction = ((single_overflow - multiple_overflow) / single_overflow) * 100
        print(f"   ✅ Multiple units reduce overflow by {reduction:.1f}%")
    elif multiple_overflow > single_overflow:
        increase = ((multiple_overflow - single_overflow) / single_overflow) * 100
        print(f"   ⚠️ Multiple units increase overflow by {increase:.1f}%")
    else:
        print(f"   ➡️ No change in overflow performance")
    
    print("\n4. Volume Utilization:")
    single_utilization = max(single_result['stored_volume']) / single_result['max_volume'] * 100
    multiple_utilization = max(scaled_result['stored_volume']) / scaled_result['max_volume'] * 100
    
    print(f"   Single unit: {single_utilization:.1f}%")
    print(f"   Multiple units: {multiple_utilization:.1f}%")
    
    print("\nTest completed successfully! ✅")

if __name__ == "__main__":
    test_multiple_soakwells()
