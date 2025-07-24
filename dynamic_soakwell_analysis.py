#!/usr/bin/env python3
"""
Dynamic Soakwell Analysis using Hydrograph Data
Analyzes soakwell performance using actual storm hydrograph from DRAINS model
"""

import csv
import math
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# Import comparison functions
from soakwell_comparison import create_comparison_plots, create_performance_summary_table

def read_hydrograph_data(file_path):
    """
    Read hydrograph data from .ts1 file
    
    Parameters:
    file_path (str): Path to the .ts1 file
    
    Returns:
    dict: Parsed hydrograph data
    """
    data = {
        'time_min': [],
        'cat1240_flow': [],
        'cat3_flow': [],
        'total_flow': []
    }
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Find the start of data (after header lines)
    data_start = 0
    for i, line in enumerate(lines):
        if line.startswith('Time (min)'):
            data_start = i + 1
            break
    
    # Parse data lines
    for line in lines[data_start:]:
        line = line.strip()
        if line and not line.startswith('!'):
            parts = line.split(',')
            if len(parts) >= 3:
                try:
                    time_min = float(parts[0])
                    cat1240 = float(parts[1])
                    cat3 = float(parts[2])
                    total = cat1240 + cat3
                    
                    data['time_min'].append(time_min)
                    data['cat1240_flow'].append(cat1240)
                    data['cat3_flow'].append(cat3)
                    data['total_flow'].append(total)
                except ValueError:
                    continue
    
    return data

def calculate_soakwell_outflow_rate(diameter, ks=1e-5, Sr=1.0):
    """
    Calculate steady-state outflow rate from soakwell
    Based on infiltration through base and walls
    
    Parameters:
    diameter (float): Soakwell diameter (m)
    ks (float): Soil saturated hydraulic conductivity (m/s)
    Sr (float): Soil moderation factor
    
    Returns:
    float: Outflow rate (m³/s)
    """
    # Assume soakwell height approximately equals diameter
    height = diameter
    
    # Infiltration area = base area + wall area
    base_area = math.pi * (diameter/2)**2
    wall_area = math.pi * diameter * height
    total_area = base_area + wall_area
    
    # Outflow rate = infiltration rate × area
    outflow_rate = ks * total_area / Sr
    
    return outflow_rate

def simulate_soakwell_performance(hydrograph_data, diameter, ks=1e-5, Sr=1.0, max_height=None):
    """
    Simulate soakwell performance over time using hydrograph data
    
    Parameters:
    hydrograph_data (dict): Time series flow data
    diameter (float): Soakwell diameter (m)
    ks (float): Soil hydraulic conductivity (m/s)
    Sr (float): Soil moderation factor
    max_height (float): Maximum soakwell height (m), defaults to diameter
    
    Returns:
    dict: Time series results
    """
    if max_height is None:
        max_height = diameter
    
    max_volume = math.pi * (diameter/2)**2 * max_height
    
    # Initialize arrays
    time_min = hydrograph_data['time_min']
    inflow_rates = hydrograph_data['total_flow']  # m³/s
    
    # Initialize output arrays
    stored_volume = [0.0]  # m³
    outflow_rate = [0.0]   # m³/s
    cumulative_inflow = [0.0]  # m³
    cumulative_outflow = [0.0]  # m³
    overflow = [0.0]  # m³/s
    water_level = [0.0]  # m
    
    # Calculate constant outflow rate (when soakwell is full)
    max_outflow_rate = calculate_soakwell_outflow_rate(diameter, ks, Sr)
    
    for i in range(1, len(time_min)):
        dt = (time_min[i] - time_min[i-1]) * 60  # Convert minutes to seconds
        
        # Current inflow rate
        inflow = inflow_rates[i]  # m³/s
        
        # Current stored volume
        current_volume = stored_volume[i-1]
        
        # Calculate current water level
        current_level = current_volume / (math.pi * (diameter/2)**2)
        water_level.append(min(current_level, max_height))
        
        # Calculate actual outflow rate based on current water level
        if current_volume > 0:
            # Outflow rate scales with wetted area (simplified approach)
            level_factor = min(current_level / max_height, 1.0)
            current_outflow_rate = max_outflow_rate * level_factor
        else:
            current_outflow_rate = 0.0
        
        outflow_rate.append(current_outflow_rate)
        
        # Calculate volume change
        volume_in = inflow * dt
        volume_out = current_outflow_rate * dt
        
        # Update stored volume
        new_volume = current_volume + volume_in - volume_out
        
        # Check for overflow
        if new_volume > max_volume:
            overflow_vol = new_volume - max_volume
            overflow.append(overflow_vol / dt)  # Convert back to rate
            new_volume = max_volume
        else:
            overflow.append(0.0)
        
        # Ensure volume doesn't go negative
        new_volume = max(0.0, new_volume)
        
        stored_volume.append(new_volume)
        
        # Update cumulative values
        cumulative_inflow.append(cumulative_inflow[i-1] + volume_in)
        cumulative_outflow.append(cumulative_outflow[i-1] + volume_out)
    
    # Calculate mass balance
    total_inflow = cumulative_inflow[-1]
    total_outflow = cumulative_outflow[-1]
    total_overflow = sum(overflow[i] * dt for i in range(len(overflow)))
    final_stored = stored_volume[-1]
    
    # Mass balance check: In = Out + Overflow + Stored + Error
    mass_balance_error = total_inflow - (total_outflow + total_overflow + final_stored)
    mass_balance_error_percent = (mass_balance_error / total_inflow * 100) if total_inflow > 0 else 0
    
    return {
        'time_min': time_min,
        'inflow_rate': inflow_rates,
        'stored_volume': stored_volume,
        'outflow_rate': outflow_rate,
        'cumulative_inflow': cumulative_inflow,
        'cumulative_outflow': cumulative_outflow,
        'overflow_rate': overflow,
        'water_level': water_level,
        'mass_balance': {
            'total_inflow_m3': total_inflow,
            'total_outflow_m3': total_outflow,
            'total_overflow_m3': total_overflow,
            'final_stored_m3': final_stored,
            'mass_balance_error_m3': mass_balance_error,
            'mass_balance_error_percent': mass_balance_error_percent
        },
        'max_volume': max_volume,
        'max_height': max_height,
        'diameter': diameter
    }

def plot_soakwell_performance(results, title="Soakwell Performance Analysis"):
    """
    Create comprehensive plots of soakwell performance
    
    Parameters:
    results (dict): Simulation results
    title (str): Plot title
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    time_hours = [t/60 for t in results['time_min']]
    
    # Plot 1: Flow rates
    ax1 = axes[0, 0]
    ax1.plot(time_hours, results['inflow_rate'], 'b-', label='Inflow Rate', linewidth=2)
    ax1.plot(time_hours, results['outflow_rate'], 'g-', label='Outflow Rate', linewidth=2)
    if max(results['overflow_rate']) > 0:
        ax1.plot(time_hours, results['overflow_rate'], 'r-', label='Overflow Rate', linewidth=2)
    ax1.set_xlabel('Time (hours)')
    ax1.set_ylabel('Flow Rate (m³/s)')
    ax1.set_title('Flow Rates')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Storage volume and water level
    ax2 = axes[0, 1]
    ax2_twin = ax2.twinx()
    
    line1 = ax2.plot(time_hours, results['stored_volume'], 'purple', linewidth=2, label='Stored Volume')
    ax2.axhline(y=results['max_volume'], color='red', linestyle='--', alpha=0.7, label='Max Capacity')
    ax2.set_xlabel('Time (hours)')
    ax2.set_ylabel('Volume (m³)', color='purple')
    ax2.set_title('Storage Volume & Water Level')
    
    line2 = ax2_twin.plot(time_hours, results['water_level'], 'orange', linewidth=2, label='Water Level')
    ax2_twin.axhline(y=results['max_height'], color='red', linestyle='--', alpha=0.7)
    ax2_twin.set_ylabel('Water Level (m)', color='orange')
    
    # Combine legends
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Cumulative volumes
    ax3 = axes[1, 0]
    ax3.plot(time_hours, results['cumulative_inflow'], 'b-', linewidth=2, label='Cumulative Inflow')
    ax3.plot(time_hours, results['cumulative_outflow'], 'g-', linewidth=2, label='Cumulative Outflow')
    ax3.set_xlabel('Time (hours)')
    ax3.set_ylabel('Cumulative Volume (m³)')
    ax3.set_title('Cumulative Volumes')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Volume balance
    ax4 = axes[1, 1]
    volume_difference = [inf - out for inf, out in zip(results['cumulative_inflow'], results['cumulative_outflow'])]
    ax4.plot(time_hours, volume_difference, 'purple', linewidth=2, label='Net Volume Change')
    ax4.plot(time_hours, results['stored_volume'], 'orange', linewidth=2, label='Current Storage')
    ax4.set_xlabel('Time (hours)')
    ax4.set_ylabel('Volume (m³)')
    ax4.set_title('Volume Balance')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def analyze_multiple_scenarios(hydrograph_data, scenarios):
    """
    Analyze multiple soakwell design scenarios
    
    Parameters:
    hydrograph_data (dict): Time series flow data
    scenarios (list): List of scenario dictionaries
    
    Returns:
    dict: Results for all scenarios
    """
    results = {}
    
    for scenario in scenarios:
        name = scenario['name']
        print(f"\nAnalyzing scenario: {name}")
        print(f"  Diameter: {scenario['diameter']:.2f} m")
        print(f"  Hydraulic conductivity: {scenario['ks']:.2e} m/s")
        
        result = simulate_soakwell_performance(
            hydrograph_data,
            diameter=scenario['diameter'],
            ks=scenario['ks'],
            Sr=scenario.get('Sr', 1.0),
            max_height=scenario.get('max_height', scenario['diameter'])
        )
        
        # Calculate performance metrics
        total_inflow = result['cumulative_inflow'][-1]
        total_outflow = result['cumulative_outflow'][-1]
        max_storage = max(result['stored_volume'])
        peak_overflow = max(result['overflow_rate'])
        
        result['performance'] = {
            'total_inflow_m3': total_inflow,
            'total_outflow_m3': total_outflow,
            'max_storage_m3': max_storage,
            'peak_overflow_rate': peak_overflow,
            'storage_efficiency': total_outflow / total_inflow if total_inflow > 0 else 0,
            'volume_utilization': max_storage / result['max_volume']
        }
        
        print(f"  Total inflow: {total_inflow:.2f} m³")
        print(f"  Total outflow: {total_outflow:.2f} m³")
        print(f"  Max storage used: {max_storage:.2f} m³ ({max_storage/result['max_volume']*100:.1f}% of capacity)")
        print(f"  Peak overflow: {peak_overflow:.4f} m³/s")
        print(f"  Storage efficiency: {result['performance']['storage_efficiency']*100:.1f}%")
        
        results[name] = result
    
    return results

# Main execution
if __name__ == "__main__":
    # Read hydrograph data
    hydrograph_file = r"c:\Users\Patrick.Hayes\OneDrive - Aurecon Group\Documents\North Fremantle Ped\DRAINS\NF_Catchments_1% AEP, 4.5 hour burst, Storm 1.ts1"
    
    print("Reading hydrograph data...")
    hydrograph_data = read_hydrograph_data(hydrograph_file)
    
    print(f"Loaded {len(hydrograph_data['time_min'])} data points")
    print(f"Storm duration: {max(hydrograph_data['time_min']):.0f} minutes ({max(hydrograph_data['time_min'])/60:.1f} hours)")
    print(f"Peak flow rate: {max(hydrograph_data['total_flow']):.4f} m³/s")
    print(f"Total flow volume: {sum(hydrograph_data['total_flow']) * 60:.2f} m³")  # Approximate, assuming 1-minute intervals
    
    # Define scenarios to analyze
    scenarios = [
        {
            'name': 'Medium Soil - 3m diameter',
            'diameter': 3.0,
            'ks': 1e-5,
            'max_height': 3.0
        },
        {
            'name': 'Medium Soil - 4m diameter',
            'diameter': 4.0,
            'ks': 1e-5,
            'max_height': 3.5
        },
        {
            'name': 'Sandy Soil - 2m diameter',
            'diameter': 2.0,
            'ks': 1e-4,
            'max_height': 3.0
        },
        {
            'name': 'Clay Soil - 5m diameter',
            'diameter': 5.0,
            'ks': 1e-6,
            'max_height': 3.0
        }
    ]
    
    # Analyze all scenarios
    results = analyze_multiple_scenarios(hydrograph_data, scenarios)
    
    # Create plots for each scenario
    for scenario_name, result in results.items():
        fig = plot_soakwell_performance(result, f"Soakwell Performance: {scenario_name}")
        plt.show()
    
    # Create comparison plots
    print("\nCreating comparison plots...")
    comparison_fig = create_comparison_plots(results)
    plt.show()
    
    # Create detailed summary table
    create_performance_summary_table(results)
    
    # Summary comparison
    print("\n" + "=" * 100)
    print("SCENARIO COMPARISON SUMMARY")
    print("=" * 100)
    print(f"{'Scenario':<25} {'Diameter':<10} {'ks (m/s)':<12} {'Max Storage':<12} {'Efficiency':<12} {'Overflow':<10}")
    print("-" * 100)
    
    for scenario_name, result in results.items():
        perf = result['performance']
        scenario_short = scenario_name.split(' - ')[1] if ' - ' in scenario_name else scenario_name
        print(f"{scenario_short:<25} {result['diameter']:<10.1f} {scenarios[list(results.keys()).index(scenario_name)]['ks']:<12.2e} "
              f"{perf['max_storage_m3']:<12.1f} {perf['storage_efficiency']*100:<12.1f}% "
              f"{'Yes' if perf['peak_overflow_rate'] > 0 else 'No':<10}")
