#!/usr/bin/env python3
"""
Dynamic Soakwell Analysis using Hydrograph Data - File Output Version
Analyzes soakwell performance and saves plots to files
"""

import csv
import math
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import os

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
    """
    height = diameter
    base_area = math.pi * (diameter/2)**2
    wall_area = math.pi * diameter * height
    total_area = base_area + wall_area
    outflow_rate = ks * total_area / Sr
    return outflow_rate

def simulate_soakwell_performance(hydrograph_data, diameter, ks=1e-5, Sr=1.0, max_height=None):
    """
    Simulate soakwell performance over time using hydrograph data
    """
    if max_height is None:
        max_height = diameter
    
    max_volume = math.pi * (diameter/2)**2 * max_height
    
    # Initialize arrays
    time_min = hydrograph_data['time_min']
    inflow_rates = hydrograph_data['total_flow']  # m³/s
    
    # Initialize output arrays
    stored_volume = [0.0]
    outflow_rate = [0.0]
    cumulative_inflow = [0.0]
    cumulative_outflow = [0.0]
    overflow = [0.0]
    water_level = [0.0]
    
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
            overflow.append(overflow_vol / dt)
            new_volume = max_volume
        else:
            overflow.append(0.0)
        
        # Ensure volume doesn't go negative
        new_volume = max(0.0, new_volume)
        
        stored_volume.append(new_volume)
        
        # Update cumulative values
        cumulative_inflow.append(cumulative_inflow[i-1] + volume_in)
        cumulative_outflow.append(cumulative_outflow[i-1] + volume_out)
    
    return {
        'time_min': time_min,
        'inflow_rate': inflow_rates,
        'stored_volume': stored_volume,
        'outflow_rate': outflow_rate,
        'cumulative_inflow': cumulative_inflow,
        'cumulative_outflow': cumulative_outflow,
        'overflow_rate': overflow,
        'water_level': water_level,
        'max_volume': max_volume,
        'max_height': max_height,
        'diameter': diameter
    }

def plot_soakwell_performance(results, title="Soakwell Performance Analysis", save_path=None):
    """
    Create comprehensive plots of soakwell performance and save to file
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
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    
    plt.close()
    return fig

def create_comparison_plot(results, save_path=None):
    """
    Create comparison plot for all scenarios
    """
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Soakwell Performance Comparison - 10% AEP Storm Event', fontsize=16, fontweight='bold')
    
    # Get scenario names and colors
    scenario_names = list(results.keys())
    # Expanded color palette to support more scenarios
    colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan', 
              'magenta', 'yellow', 'navy', 'lime', 'teal', 'silver', 'maroon', 'aqua', 'fuchsia', 'black'][:len(scenario_names)]
    
    # Get time in hours
    time_hours = [t/60 for t in results[scenario_names[0]]['time_min']]
    
    # Plot 1: Inflow rates
    ax1 = axes[0, 0]
    first_result = results[scenario_names[0]]
    ax1.plot(time_hours, first_result['inflow_rate'], 'black', linewidth=2, label='Storm Hydrograph')
    ax1.set_xlabel('Time (hours)')
    ax1.set_ylabel('Inflow Rate (m³/s)')
    ax1.set_title('Storm Hydrograph')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot 2: Stored volumes
    ax2 = axes[0, 1]
    for i, (name, result) in enumerate(results.items()):
        short_name = name.split(' - ')[1] if ' - ' in name else name
        ax2.plot(time_hours, result['stored_volume'], color=colors[i], linewidth=2, label=short_name)
        ax2.axhline(y=result['max_volume'], color=colors[i], linestyle='--', alpha=0.5)
    ax2.set_xlabel('Time (hours)')
    ax2.set_ylabel('Stored Volume (m³)')
    ax2.set_title('Storage Volume Comparison')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Outflow rates
    ax3 = axes[0, 2]
    for i, (name, result) in enumerate(results.items()):
        short_name = name.split(' - ')[1] if ' - ' in name else name
        ax3.plot(time_hours, result['outflow_rate'], color=colors[i], linewidth=2, label=short_name)
    ax3.set_xlabel('Time (hours)')
    ax3.set_ylabel('Outflow Rate (m³/s)')
    ax3.set_title('Outflow Rate Comparison')
    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Cumulative outflow
    ax4 = axes[1, 0]
    for i, (name, result) in enumerate(results.items()):
        short_name = name.split(' - ')[1] if ' - ' in name else name
        ax4.plot(time_hours, result['cumulative_outflow'], color=colors[i], linewidth=2, label=short_name)
    ax4.set_xlabel('Time (hours)')
    ax4.set_ylabel('Cumulative Outflow (m³)')
    ax4.set_title('Cumulative Outflow')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Plot 5: Storage efficiency
    ax5 = axes[1, 1]
    names = []
    efficiencies = []
    for name, result in results.items():
        short_name = name.split(' - ')[1] if ' - ' in name else name
        names.append(short_name)
        total_inflow = result['cumulative_inflow'][-1]
        total_outflow = result['cumulative_outflow'][-1]
        efficiency = (total_outflow / total_inflow * 100) if total_inflow > 0 else 0
        efficiencies.append(efficiency)
    
    bars = ax5.bar(range(len(names)), efficiencies, color=colors[:len(names)])
    ax5.set_xlabel('Scenario')
    ax5.set_ylabel('Storage Efficiency (%)')
    ax5.set_title('Storage Efficiency')
    ax5.set_xticks(range(len(names)))
    ax5.set_xticklabels(names, rotation=45, ha='right')
    ax5.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%', ha='center', va='bottom')
    
    # Plot 6: Volume utilization
    ax6 = axes[1, 2]
    utilizations = []
    for name, result in results.items():
        max_storage = max(result['stored_volume'])
        utilization = (max_storage / result['max_volume'] * 100)
        utilizations.append(utilization)
    
    bars = ax6.bar(range(len(names)), utilizations, color=colors[:len(names)])
    ax6.set_xlabel('Scenario')
    ax6.set_ylabel('Volume Utilization (%)')
    ax6.set_title('Maximum Volume Utilization')
    ax6.set_xticks(range(len(names)))
    ax6.set_xticklabels(names, rotation=45, ha='right')
    ax6.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.0f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Comparison plot saved to: {save_path}")
    
    plt.close()
    return fig

def solve_for_minimum_soakwells(hydrograph_data, diameter, ks=1e-5, Sr=1.0, max_height=None, max_soakwells=20):
    """
    Find the minimum number of soakwells needed to prevent overflow
    
    Parameters:
    hydrograph_data: Storm hydrograph data
    diameter: Soakwell diameter (m)
    ks: Soil permeability (m/s)
    Sr: Saturation ratio
    max_height: Maximum soakwell height (m)
    max_soakwells: Maximum number of soakwells to test
    
    Returns:
    dict: Results including minimum number needed and performance data
    """
    if max_height is None:
        max_height = diameter
    
    # Test increasing numbers of soakwells
    for num_soakwells in range(1, max_soakwells + 1):
        # Simulate single soakwell performance
        single_result = simulate_soakwell_performance(hydrograph_data, diameter, ks, Sr, max_height)
        
        # Scale by number of soakwells
        # Each soakwell gets 1/num_soakwells of the total inflow
        scaled_inflow = [flow / num_soakwells for flow in single_result['inflow_rate']]
        
        # Create scaled hydrograph data
        scaled_hydrograph = {
            'time_min': hydrograph_data['time_min'],
            'total_flow': scaled_inflow,
            'cat1240_flow': [flow / num_soakwells for flow in hydrograph_data['cat1240_flow']],
            'cat3_flow': [flow / num_soakwells for flow in hydrograph_data['cat3_flow']]
        }
        
        # Simulate scaled performance
        result = simulate_soakwell_performance(scaled_hydrograph, diameter, ks, Sr, max_height)
        
        # Check if overflow occurs
        peak_overflow = max(result['overflow_rate'])
        
        if peak_overflow == 0:  # No overflow - solution found
            # Scale results back up for total system
            total_result = {
                'num_soakwells': num_soakwells,
                'diameter': diameter,
                'ks': ks,
                'max_height': max_height,
                'single_soakwell_result': result,
                'total_volume': result['max_volume'] * num_soakwells,
                'total_max_water_level': max(result['water_level']),
                'solution_found': True
            }
            return total_result
    
    # No solution found within the limit
    return {
        'num_soakwells': max_soakwells,
        'diameter': diameter,
        'ks': ks,
        'max_height': max_height,
        'single_soakwell_result': None,
        'total_volume': None,
        'total_max_water_level': None,
        'solution_found': False
    }

def run_solve_analysis(hydrograph_data, scenarios, max_soakwells=20):
    """
    Run solve analysis for all scenarios to find minimum soakwells needed
    
    Parameters:
    hydrograph_data: Storm hydrograph data
    scenarios: List of scenario configurations
    max_soakwells: Maximum number of soakwells to test
    
    Returns:
    dict: Solve results for each scenario
    """
    print("\n" + "=" * 80)
    print("SOLVE ANALYSIS - Finding Minimum Soakwells to Prevent Overflow")
    print("=" * 80)
    
    solve_results = {}
    
    for scenario in scenarios:
        print(f"\nSolving for: {scenario['name']}")
        print(f"   Diameter: {scenario['diameter']:.1f}m, ks: {scenario['ks']:.2e} m/s")
        
        result = solve_for_minimum_soakwells(
            hydrograph_data,
            diameter=scenario['diameter'],
            ks=scenario['ks'],
            Sr=scenario.get('Sr', 1.0),
            max_height=scenario.get('max_height', scenario['diameter']),
            max_soakwells=max_soakwells
        )
        
        if result['solution_found']:
            print(f"   ✓ Solution found: {result['num_soakwells']} soakwells")
            print(f"   → Total volume: {result['total_volume']:.1f} m³")
            print(f"   → Max water level per soakwell: {result['total_max_water_level']:.2f}m")
        else:
            print(f"   ✗ No solution found (tested up to {max_soakwells} soakwells)")
        
        solve_results[scenario['name']] = result
    
    # Print summary table
    print("\n" + "=" * 100)
    print("SOLVE RESULTS SUMMARY")
    print("=" * 100)
    print(f"{'Scenario':<30} {'Diameter':<10} {'ks (m/s)':<12} {'Min Soakwells':<15} {'Total Volume':<15} {'Status':<10}")
    print("-" * 100)
    
    for name, result in solve_results.items():
        short_name = name.split(' - ')[1] if ' - ' in name else name
        
        if result['solution_found']:
            status = "✓ Solved"
            num_wells = result['num_soakwells']
            total_vol = f"{result['total_volume']:.1f} m³"
        else:
            status = "✗ No solution"
            num_wells = f">{max_soakwells}"
            total_vol = "N/A"
        
        print(f"{short_name:<30} {result['diameter']:<10.1f} {result['ks']:<12.2e} "
              f"{num_wells:<15} {total_vol:<15} {status:<10}")
    
    print("=" * 100)
    
    return solve_results

# Main execution
if __name__ == "__main__":
    # Read hydrograph data
    hydrograph_file = r"DRAINS\North_Freo_Catchments_10% AEP, 4.5 hour burst, Storm 4.ts1"
    
    print("Dynamic Soakwell Analysis - File Output Version")
    print("=" * 60)
    print("Reading hydrograph data...")
    
    try:
        hydrograph_data = read_hydrograph_data(hydrograph_file)
        
        print(f"Loaded {len(hydrograph_data['time_min'])} data points")
        print(f"Storm duration: {max(hydrograph_data['time_min']):.0f} minutes ({max(hydrograph_data['time_min'])/60:.1f} hours)")
        print(f"Peak flow rate: {max(hydrograph_data['total_flow']):.4f} m³/s")
        
        # Calculate total volume (approximate)
        total_volume = 0
        for i in range(1, len(hydrograph_data['time_min'])):
            dt = (hydrograph_data['time_min'][i] - hydrograph_data['time_min'][i-1]) * 60  # seconds
            total_volume += hydrograph_data['total_flow'][i] * dt
        
        print(f"Total flow volume: {total_volume:.2f} m³")
        
    except Exception as e:
        print(f"Error reading hydrograph data: {e}")
        exit(1)
    
    # Define scenarios to analyze - expanded coverage
    scenarios = [
        # Sandy soil scenarios (high permeability)
        {
            'name': 'Sandy Soil - 2m diameter',
            'diameter': 2.0,
            'ks': 1e-4,
            'max_height': 3.0
        },
        {
            'name': 'Sandy Soil - 3m diameter',
            'diameter': 3.0,
            'ks': 1e-4,
            'max_height': 3.0
        },
        {
            'name': 'Sandy Soil - 4m diameter',
            'diameter': 4.0,
            'ks': 1e-4,
            'max_height': 3.5
        },
        # Medium soil scenarios (standard permeability)
        {
            'name': 'Medium Soil - 2m diameter',
            'diameter': 2.0,
            'ks': 1e-5,
            'max_height': 3.0
        },
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
            'name': 'Medium Soil - 5m diameter',
            'diameter': 5.0,
            'ks': 1e-5,
            'max_height': 3.5
        },
        # Clay soil scenarios (low permeability)
        {
            'name': 'Clay Soil - 3m diameter',
            'diameter': 3.0,
            'ks': 1e-6,
            'max_height': 3.0
        },
        {
            'name': 'Clay Soil - 4m diameter',
            'diameter': 4.0,
            'ks': 1e-6,
            'max_height': 3.5
        },
        {
            'name': 'Clay Soil - 5m diameter',
            'diameter': 5.0,
            'ks': 1e-6,
            'max_height': 3.5
        },
        {
            'name': 'Clay Soil - 6m diameter',
            'diameter': 6.0,
            'ks': 1e-6,
            'max_height': 3.5
        },
        # Very clay soil scenarios (very low permeability)
        {
            'name': 'Very Clay Soil - 4m diameter',
            'diameter': 4.0,
            'ks': 5e-7,
            'max_height': 3.5
        },
        {
            'name': 'Very Clay Soil - 5m diameter',
            'diameter': 5.0,
            'ks': 5e-7,
            'max_height': 3.5
        },
        {
            'name': 'Very Clay Soil - 6m diameter',
            'diameter': 6.0,
            'ks': 5e-7,
            'max_height': 3.5
        }
    ]
    
    # Create output directory for plots
    output_dir = "soakwell_analysis_plots"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"\nAnalyzing {len(scenarios)} scenarios...")
    print("-" * 60)
    
    results = {}
    
    # Analyze each scenario
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Analyzing: {scenario['name']}")
        print(f"   Diameter: {scenario['diameter']:.1f}m, ks: {scenario['ks']:.2e} m/s")
        
        # Run simulation
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
        
        # Print results
        print(f"   -> Total inflow: {total_inflow:.1f} m³")
        print(f"   -> Total outflow: {total_outflow:.1f} m³")
        print(f"   -> Storage efficiency: {result['performance']['storage_efficiency']*100:.1f}%")
        print(f"   -> Max storage used: {max_storage:.1f} m³ ({result['performance']['volume_utilization']*100:.0f}% of capacity)")
        print(f"   -> Peak overflow: {peak_overflow:.4f} m³/s")
        
        # Save individual plot
        safe_name = scenario['name'].replace(' ', '_').replace('-', '').replace(',', '')
        plot_path = os.path.join(output_dir, f"soakwell_{safe_name}.png")
        plot_soakwell_performance(result, f"Soakwell Performance: {scenario['name']}", plot_path)
        
        results[scenario['name']] = result
    
    # Create comparison plot
    print(f"\nCreating comparison plot...")
    comparison_path = os.path.join(output_dir, "soakwell_comparison.png")
    create_comparison_plot(results, comparison_path)
    
    # Print summary table
    print("\n" + "=" * 100)
    print("SUMMARY TABLE")
    print("=" * 100)
    print(f"{'Scenario':<25} {'Diameter':<10} {'ks (m/s)':<12} {'Efficiency':<12} {'Max Storage':<12} {'Overflow?':<10}")
    print("-" * 100)
    
    for name, result in results.items():
        perf = result['performance']
        short_name = name.split(' - ')[1] if ' - ' in name else name
        
        # Get ks value
        for scenario in scenarios:
            if scenario['name'] == name:
                ks = scenario['ks']
                break
        
        overflow_status = "Yes" if perf['peak_overflow_rate'] > 0 else "No"
        
        print(f"{short_name:<25} {result['diameter']:<10.1f} {ks:<12.2e} "
              f"{perf['storage_efficiency']*100:<12.1f}% {perf['max_storage_m3']:<12.1f} {overflow_status:<10}")
    
    print("=" * 100)
    print(f"\nAnalysis complete! Check the '{output_dir}' folder for all plots.")
    print(f"Individual scenario plots and comparison plot saved.")
    
    # Find worst case scenario (highest water level)
    worst_case = max(results.values(), key=lambda x: max(x['water_level']))
    worst_case_name = [name for name, result in results.items() if result == worst_case][0]
    
    print(f"\nWorst case storm (highest water level): {worst_case_name}")
    print(f"   Maximum water level: {max(worst_case['water_level']):.2f}m")
    print(f"   Peak overflow: {worst_case['performance']['peak_overflow_rate']:.4f} m³/s")
    print(f"   Storage efficiency: {worst_case['performance']['storage_efficiency']*100:.1f}%")
    
    # Run solve analysis to find minimum soakwells needed
    solve_results = run_solve_analysis(hydrograph_data, scenarios, max_soakwells=20)
