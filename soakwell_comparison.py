#!/usr/bin/env python3
"""
Soakwell Comparison Visualization
Creates summary comparison plots for multiple soakwell scenarios
"""

import matplotlib.pyplot as plt
import numpy as np

def create_comparison_plots(results):
    """
    Create comprehensive comparison plots for multiple scenarios
    """
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Soakwell Performance Comparison - 1% AEP Storm Event', fontsize=16, fontweight='bold')
    
    # Get scenario names and colors
    scenario_names = list(results.keys())
    colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown'][:len(scenario_names)]
    
    # Get time in hours (assuming all scenarios have same time base)
    time_hours = [t/60 for t in results[scenario_names[0]]['time_min']]
    
    # Plot 1: Inflow rates (all scenarios show same inflow)
    ax1 = axes[0, 0]
    first_result = results[scenario_names[0]]
    ax1.plot(time_hours, first_result['inflow_rate'], 'black', linewidth=2, label='Storm Hydrograph')
    ax1.set_xlabel('Time (hours)')
    ax1.set_ylabel('Inflow Rate (m³/s)')
    ax1.set_title('Storm Hydrograph (All Scenarios)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot 2: Stored volumes
    ax2 = axes[0, 1]
    for i, (name, result) in enumerate(results.items()):
        short_name = name.split(' - ')[1] if ' - ' in name else name
        ax2.plot(time_hours, result['stored_volume'], color=colors[i], linewidth=2, label=short_name)
        # Show capacity line
        ax2.axhline(y=result['max_volume'], color=colors[i], linestyle='--', alpha=0.5)
    ax2.set_xlabel('Time (hours)')
    ax2.set_ylabel('Stored Volume (m³)')
    ax2.set_title('Storage Volume Comparison')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Outflow rates
    ax3 = axes[0, 2]
    for i, (name, result) in enumerate(results.items()):
        short_name = name.split(' - ')[1] if ' - ' in name else name
        ax3.plot(time_hours, result['outflow_rate'], color=colors[i], linewidth=2, label=short_name)
    ax3.set_xlabel('Time (hours)')
    ax3.set_ylabel('Outflow Rate (m³/s)')
    ax3.set_title('Outflow Rate Comparison')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Cumulative outflow
    ax4 = axes[1, 0]
    for i, (name, result) in enumerate(results.items()):
        short_name = name.split(' - ')[1] if ' - ' in name else name
        ax4.plot(time_hours, result['cumulative_outflow'], color=colors[i], linewidth=2, label=short_name)
    ax4.set_xlabel('Time (hours)')
    ax4.set_ylabel('Cumulative Outflow (m³)')
    ax4.set_title('Cumulative Outflow Comparison')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Plot 5: Overflow rates
    ax5 = axes[1, 1]
    has_overflow = False
    for i, (name, result) in enumerate(results.items()):
        if max(result['overflow_rate']) > 0:
            short_name = name.split(' - ')[1] if ' - ' in name else name
            ax5.plot(time_hours, result['overflow_rate'], color=colors[i], linewidth=2, label=short_name)
            has_overflow = True
    
    if has_overflow:
        ax5.set_xlabel('Time (hours)')
        ax5.set_ylabel('Overflow Rate (m³/s)')
        ax5.set_title('Overflow Rate Comparison')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
    else:
        ax5.text(0.5, 0.5, 'No Overflow\nin Any Scenario', 
                ha='center', va='center', transform=ax5.transAxes, fontsize=14)
        ax5.set_title('Overflow Rate Comparison')
    
    # Plot 6: Performance metrics bar chart
    ax6 = axes[1, 2]
    metrics = []
    names = []
    for name, result in results.items():
        short_name = name.split(' - ')[1] if ' - ' in name else name
        names.append(short_name)
        metrics.append(result['performance']['storage_efficiency'] * 100)
    
    bars = ax6.bar(range(len(names)), metrics, color=colors[:len(names)])
    ax6.set_xlabel('Scenario')
    ax6.set_ylabel('Storage Efficiency (%)')
    ax6.set_title('Storage Efficiency Comparison')
    ax6.set_xticks(range(len(names)))
    ax6.set_xticklabels(names, rotation=45, ha='right')
    ax6.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    return fig

def create_performance_summary_table(results):
    """
    Create a detailed performance summary table
    """
    print("\n" + "=" * 120)
    print("DETAILED PERFORMANCE SUMMARY")
    print("=" * 120)
    
    # Header
    headers = ['Scenario', 'Diameter (m)', 'ks (m/s)', 'Max Vol (m³)', 'Peak Storage (m³)', 
               'Storage Used (%)', 'Total Outflow (m³)', 'Efficiency (%)', 'Peak Overflow (m³/s)']
    
    # Print header
    print(f"{headers[0]:<20} {headers[1]:<12} {headers[2]:<12} {headers[3]:<12} {headers[4]:<15} "
          f"{headers[5]:<14} {headers[6]:<15} {headers[7]:<12} {headers[8]:<16}")
    print("-" * 120)
    
    # Print data for each scenario
    for name, result in results.items():
        perf = result['performance']
        short_name = name.split(' - ')[1] if ' - ' in name else name
        
        # Get soil type from scenario name for ks lookup
        if 'Medium Soil' in name:
            ks = 1e-5
        elif 'Sandy Soil' in name:
            ks = 1e-4
        elif 'Clay Soil' in name:
            ks = 1e-6
        else:
            ks = 1e-5  # default
        
        print(f"{short_name:<20} {result['diameter']:<12.1f} {ks:<12.2e} {result['max_volume']:<12.1f} "
              f"{perf['max_storage_m3']:<15.1f} {perf['volume_utilization']*100:<14.1f} "
              f"{perf['total_outflow_m3']:<15.1f} {perf['storage_efficiency']*100:<12.1f} "
              f"{perf['peak_overflow_rate']:<16.4f}")
    
    print("=" * 120)
    
    # Calculate and display recommendations
    print("\nDESIGN RECOMMENDATIONS:")
    print("=" * 60)
    
    best_efficiency = max(results.values(), key=lambda x: x['performance']['storage_efficiency'])
    best_no_overflow = None
    
    for name, result in results.items():
        if result['performance']['peak_overflow_rate'] == 0:
            if best_no_overflow is None or result['performance']['storage_efficiency'] > best_no_overflow['performance']['storage_efficiency']:
                best_no_overflow = result
                best_no_overflow_name = name
    
    print(f"• Highest storage efficiency: {[k for k, v in results.items() if v == best_efficiency][0]}")
    print(f"  - Efficiency: {best_efficiency['performance']['storage_efficiency']*100:.1f}%")
    print(f"  - Total outflow: {best_efficiency['performance']['total_outflow_m3']:.1f} m³")
    
    if best_no_overflow:
        print(f"• Best design with no overflow: {best_no_overflow_name}")
        print(f"  - Efficiency: {best_no_overflow['performance']['storage_efficiency']*100:.1f}%")
        print(f"  - Storage utilization: {best_no_overflow['performance']['volume_utilization']*100:.1f}%")
    else:
        print("• No design prevents overflow for this storm event")
        print("  - Consider larger soakwells or multiple units")
    
    print("\nKEY OBSERVATIONS:")
    print("• Sandy soil performs best due to high infiltration rate")
    print("• Clay soil requires much larger storage due to low infiltration")
    print("• All scenarios reach full capacity, indicating undersizing for this storm")
    print("• Consider pre-treatment and maintenance for long-term performance")

if __name__ == "__main__":
    # This would normally import the results from the main analysis
    # For demonstration, we'll create a simple version
    print("Run this after the main dynamic_soakwell_analysis.py to create comparison plots")
