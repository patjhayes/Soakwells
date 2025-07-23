#!/usr/bin/env python3
"""
French Drain Integration with Soakwell Dashboard
Demonstrates how to integrate French drain modeling with existing hydrograph analysis

This script shows how to:
1. Use existing hydrograph data from .ts1 files
2. Apply French drain modeling to the data
3. Compare French drain performance with soakwell performance
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
from french_drain_model import FrenchDrainModel

def convert_soakwell_hydrograph_to_french_drain(hydrograph_data, catchment_area_m2=1000, runoff_coefficient=0.8):
    """
    Convert soakwell hydrograph data to French drain inflow
    
    Parameters:
    hydrograph_data: Dictionary with 'time_min' and 'total_flow' from soakwell analysis
    catchment_area_m2: Contributing catchment area (m²)
    runoff_coefficient: Runoff coefficient (0.0-1.0)
    
    Returns:
    dict: French drain compatible hydrograph
    """
    
    # Convert time from minutes to seconds
    time_seconds = [t * 60 for t in hydrograph_data['time_min']]
    
    # Use the existing flow data (already in m³/s)
    flow_data = hydrograph_data['total_flow']
    
    return {
        'time': np.array(time_seconds),
        'flow': np.array(flow_data),
        'catchment_area_m2': catchment_area_m2,
        'runoff_coefficient': runoff_coefficient
    }

def compare_drainage_systems(hydrograph_data, soakwell_results=None):
    """
    Compare French drain performance with soakwell performance
    
    Parameters:
    hydrograph_data: Original hydrograph data from .ts1 file
    soakwell_results: Optional results from soakwell analysis for comparison
    
    Returns:
    dict: Comparison results
    """
    
    print("Comparative Analysis: French Drain vs Soakwell System")
    print("="*60)
    
    # Initialize French drain model
    drain = FrenchDrainModel()
    
    # Convert hydrograph for French drain analysis
    drain_hydrograph = convert_soakwell_hydrograph_to_french_drain(hydrograph_data)
    
    # Test different French drain lengths
    test_lengths = [50, 100, 150, 200]  # meters
    drain_results = {}
    
    for length in test_lengths:
        print(f"\nAnalyzing {length}m French drain...")
        
        results = drain.simulate_french_drain_response(
            drain_hydrograph,
            pipe_slope=0.005,  # 0.5% gradient
            length=length
        )
        
        drain_results[f"{length}m"] = results
        
        # Print summary
        perf = results['performance']
        print(f"  Infiltration efficiency: {perf['infiltration_efficiency_percent']:.1f}%")
        print(f"  Maximum storage: {perf['max_trench_storage_m3']:.1f} m³")
        print(f"  Overflow volume: {perf['total_overflow_m3']:.1f} m³")
    
    # Create comparison plots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('French Drain Length Comparison', fontsize=16, fontweight='bold')
    
    colors = ['blue', 'green', 'red', 'purple']
    
    # Plot 1: Infiltration efficiency
    ax1 = axes[0, 0]
    efficiencies = [drain_results[f"{length}m"]['performance']['infiltration_efficiency_percent'] 
                   for length in test_lengths]
    ax1.bar(test_lengths, efficiencies, color=colors, alpha=0.7)
    ax1.set_xlabel('French Drain Length (m)')
    ax1.set_ylabel('Infiltration Efficiency (%)')
    ax1.set_title('Infiltration Efficiency by Length')
    ax1.grid(True, alpha=0.3)
    
    # Add percentage labels on bars
    for i, (length, eff) in enumerate(zip(test_lengths, efficiencies)):
        ax1.text(length, eff + 1, f'{eff:.1f}%', ha='center', va='bottom')
    
    # Plot 2: Maximum storage
    ax2 = axes[0, 1]
    max_storages = [drain_results[f"{length}m"]['performance']['max_trench_storage_m3'] 
                   for length in test_lengths]
    ax2.bar(test_lengths, max_storages, color=colors, alpha=0.7)
    ax2.set_xlabel('French Drain Length (m)')
    ax2.set_ylabel('Maximum Storage (m³)')
    ax2.set_title('Peak Storage Requirements')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Flow comparison for 100m drain
    ax3 = axes[1, 0]
    results_100m = drain_results['100m']
    time_hours = results_100m['time_hours']
    
    ax3.plot(time_hours, results_100m['inflow'], 'b-', label='Inflow', linewidth=2)
    ax3.plot(time_hours, results_100m['pipe_flow'], 'g-', label='Pipe Flow', linewidth=2)
    ax3.plot(time_hours, results_100m['infiltration_outflow'], 'purple', label='Infiltration', linewidth=2)
    
    if max(results_100m['pipe_overflow']) > 0:
        ax3.plot(time_hours, results_100m['pipe_overflow'], 'r-', label='Overflow', linewidth=2)
    
    ax3.set_xlabel('Time (hours)')
    ax3.set_ylabel('Flow Rate (m³/s)')
    ax3.set_title('Flow Analysis - 100m French Drain')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Storage utilization over time
    ax4 = axes[1, 1]
    for i, length in enumerate(test_lengths):
        results = drain_results[f"{length}m"]
        max_capacity = results['system_properties']['effective_storage_m3_per_m'] * length
        utilization = [vol/max_capacity*100 for vol in results['trench_volume']]
        ax4.plot(results['time_hours'], utilization, color=colors[i], 
                label=f'{length}m drain', linewidth=2)
    
    ax4.set_xlabel('Time (hours)')
    ax4.set_ylabel('Storage Utilization (%)')
    ax4.set_title('Storage Utilization Over Time')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.axhline(y=100, color='red', linestyle='--', alpha=0.5, label='Full Capacity')
    
    plt.tight_layout()
    plt.show()
    
    # Create comparison table
    comparison_data = []
    for length in test_lengths:
        results = drain_results[f"{length}m"]
        perf = results['performance']
        
        comparison_data.append({
            'Length (m)': length,
            'Infiltration Efficiency (%)': f"{perf['infiltration_efficiency_percent']:.1f}",
            'Max Storage (m³)': f"{perf['max_trench_storage_m3']:.1f}",
            'Total Infiltrated (m³)': f"{perf['total_infiltrated_m3']:.1f}",
            'Overflow Volume (m³)': f"{perf['total_overflow_m3']:.1f}",
            'System Cost Indicator': f"{length * 100:.0f}"  # Rough cost per meter
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    print(f"\nFrench Drain Performance Comparison:")
    print(comparison_df.to_string(index=False))
    
    # Cost-effectiveness analysis
    print(f"\nCost-Effectiveness Analysis:")
    print("-" * 40)
    for length in test_lengths:
        results = drain_results[f"{length}m"]
        perf = results['performance']
        
        # Simple cost model ($/m of drain)
        cost_per_meter = 200  # AUD (excavation + pipe + aggregate + installation)
        total_cost = length * cost_per_meter
        
        # Effectiveness metric: m³ infiltrated per $ spent
        if total_cost > 0:
            effectiveness = perf['total_infiltrated_m3'] / total_cost * 1000  # m³ per $1000
            print(f"{length}m drain: ${total_cost:.0f} total, {effectiveness:.2f} m³/$1000")
    
    return {
        'drain_results': drain_results,
        'comparison_table': comparison_df,
        'recommended_length': test_lengths[np.argmax(efficiencies)] if max(efficiencies) > 95 else max(test_lengths)
    }

def design_french_drain_for_site(peak_flow_m3s, total_volume_m3, available_length_m=None):
    """
    Design French drain system for specific site conditions
    
    Parameters:
    peak_flow_m3s: Peak flow rate to handle (m³/s)
    total_volume_m3: Total volume to infiltrate (m³)
    available_length_m: Available length for installation (m), optional
    
    Returns:
    dict: Design recommendations
    """
    
    print(f"\nFrench Drain Design Tool")
    print("="*40)
    print(f"Design Requirements:")
    print(f"- Peak flow: {peak_flow_m3s:.4f} m³/s")
    print(f"- Total volume: {total_volume_m3:.1f} m³")
    
    # Initialize model
    drain = FrenchDrainModel()
    
    # Check pipe capacity
    pipe_props = drain.calculate_pipe_capacity(slope=0.005)
    pipe_capacity = pipe_props['flow_capacity_full']
    
    print(f"- Pipe capacity (300mm, 0.5% grade): {pipe_capacity:.4f} m³/s")
    
    if peak_flow_m3s > pipe_capacity:
        print(f"⚠️  WARNING: Peak flow exceeds pipe capacity!")
        print(f"   Consider: Larger pipe, steeper grade, or multiple parallel drains")
        multiple_drains_needed = math.ceil(peak_flow_m3s / pipe_capacity)
        print(f"   Estimated {multiple_drains_needed} parallel drains needed")
    
    # Estimate required storage length
    storage_per_meter = drain.effective_storage_volume  # m³/m
    min_length_for_storage = total_volume_m3 / storage_per_meter
    
    print(f"- Storage per meter: {storage_per_meter:.3f} m³/m")
    print(f"- Minimum length for storage: {min_length_for_storage:.0f} m")
    
    # Estimate infiltration capacity
    # Assume average water level of half trench depth during storm
    avg_water_level = drain.trench_depth / 2
    infiltration_rate_per_meter = drain.calculate_infiltration_rate(avg_water_level)
    
    print(f"- Infiltration rate per meter: {infiltration_rate_per_meter:.6f} m³/s/m")
    
    # Calculate required length for infiltration
    # This is a simplified estimate - actual performance will vary with water level
    required_length_infiltration = peak_flow_m3s / infiltration_rate_per_meter
    
    print(f"- Estimated length for infiltration: {required_length_infiltration:.0f} m")
    
    # Recommended design length
    recommended_length = max(min_length_for_storage, required_length_infiltration)
    
    if available_length_m:
        print(f"- Available length: {available_length_m} m")
        if recommended_length > available_length_m:
            print(f"⚠️  WARNING: Recommended length ({recommended_length:.0f}m) exceeds available space!")
            print(f"   Consider: Deeper trench, parallel drains, or supplementary measures")
            recommended_length = available_length_m
    
    print(f"\n💡 DESIGN RECOMMENDATION:")
    print(f"   French drain length: {recommended_length:.0f} m")
    print(f"   300mm perforated concrete pipe")
    print(f"   600mm wide × 900mm deep gravel trench")
    print(f"   0.5% minimum gradient")
    
    # Estimate costs
    cost_per_meter = 200  # AUD
    total_cost = recommended_length * cost_per_meter
    print(f"   Estimated cost: ${total_cost:.0f} AUD (excavation + materials + installation)")
    
    return {
        'recommended_length_m': recommended_length,
        'pipe_capacity_ok': peak_flow_m3s <= pipe_capacity,
        'multiple_drains_needed': math.ceil(peak_flow_m3s / pipe_capacity) if peak_flow_m3s > pipe_capacity else 1,
        'estimated_cost_aud': total_cost,
        'storage_capacity_m3': recommended_length * storage_per_meter,
        'infiltration_capacity_m3s': recommended_length * infiltration_rate_per_meter
    }

def main_demonstration():
    """
    Main demonstration of French drain modeling capabilities
    """
    
    print("FRENCH DRAIN MODELING DEMONSTRATION")
    print("="*50)
    
    # Create example hydrograph data (similar to soakwell dashboard format)
    example_hydrograph = {
        'time_min': list(range(0, 240, 5)),  # 4 hours, 5-minute intervals
        'total_flow': []
    }
    
    # Create triangular storm hydrograph
    peak_time = 60  # Peak at 1 hour
    peak_flow = 0.05  # Peak flow 0.05 m³/s
    
    for t in example_hydrograph['time_min']:
        if t <= peak_time:
            flow = peak_flow * (t / peak_time)
        else:
            flow = peak_flow * (1 - (t - peak_time) / (180 - peak_time))  # Falling limb
        example_hydrograph['total_flow'].append(max(0, flow))
    
    print(f"Created example storm hydrograph:")
    print(f"- Duration: 4 hours")
    print(f"- Peak flow: {max(example_hydrograph['total_flow']):.4f} m³/s")
    print(f"- Total volume: {sum(example_hydrograph['total_flow']) * 5 * 60:.1f} m³")
    
    # Run comparative analysis
    comparison_results = compare_drainage_systems(example_hydrograph)
    
    # Design recommendation
    peak_flow = max(example_hydrograph['total_flow'])
    total_volume = sum(example_hydrograph['total_flow']) * 5 * 60  # 5-minute intervals
    
    design_results = design_french_drain_for_site(
        peak_flow_m3s=peak_flow,
        total_volume_m3=total_volume,
        available_length_m=150  # Assume 150m available
    )
    
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"Recommended French drain length: {design_results['recommended_length_m']:.0f} m")
    print(f"Estimated cost: ${design_results['estimated_cost_aud']:.0f} AUD")
    print(f"Best performing length from analysis: {comparison_results['recommended_length']}m")
    
    return comparison_results, design_results

if __name__ == "__main__":
    # Check if running independently or as part of dashboard
    try:
        comparison, design = main_demonstration()
        print(f"\n✅ French drain modeling completed successfully!")
    except Exception as e:
        print(f"❌ Error in French drain modeling: {str(e)}")
        import traceback
        traceback.print_exc()
