#!/usr/bin/env python3
"""
Plot All NF_ILSAX_Catchments Time Series
Creates a comprehensive time series plot of all NF_ILSAX_Catchments storm files
"""

import os
import glob
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from core_soakwell_analysis import read_hydrograph_data_from_content
import re

def extract_duration_from_filename(filename):
    """Extract duration from filename for sorting purposes"""
    # Pattern to match duration like "1 hour", "30 min", "144 hour"
    duration_pattern = r'(\d+(?:\.\d+)?)\s*(min|hour)'
    match = re.search(duration_pattern, filename)
    
    if match:
        value = float(match.group(1))
        unit = match.group(2)
        
        # Convert everything to minutes for sorting
        if unit == 'hour':
            return value * 60
        else:  # unit == 'min'
            return value
    
    return 0  # Default if no match

def plot_nf_ilsax_catchments():
    """Plot all NF_ILSAX_Catchments files on a single time series graph"""
    
    # Set up the directory path
    drains_dir = "DRAINS"
    if not os.path.exists(drains_dir):
        print(f"❌ DRAINS directory not found")
        return
    
    # Find all NF_ILSAX_Catchments files
    pattern = os.path.join(drains_dir, "NF_ILSAX_Catchments*.ts1")
    storm_files = glob.glob(pattern)
    
    if not storm_files:
        print(f"❌ No NF_ILSAX_Catchments files found")
        return
    
    print(f"📊 Found {len(storm_files)} NF_ILSAX_Catchments files")
    
    # Sort files by duration for better legend organization
    storm_files.sort(key=extract_duration_from_filename)
    
    # Create the plot
    plt.figure(figsize=(16, 10))
    
    # Set up color palette for different durations
    colors = plt.cm.tab20(np.linspace(0, 1, len(storm_files)))
    
    max_time = 0
    max_flow = 0
    
    # Process each storm file
    for i, file_path in enumerate(storm_files):
        try:
            # Extract filename for legend
            filename = os.path.basename(file_path)
            
            # Read the file
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse the hydrograph data
            hydrograph_data = read_hydrograph_data_from_content(content)
            
            if hydrograph_data and len(hydrograph_data.get('time_min', [])) > 0:
                time_min = hydrograph_data['time_min']
                total_flow = hydrograph_data['total_flow']
                
                # Convert to hours for plotting
                time_hours = [t/60 for t in time_min]
                
                # Extract duration for label
                duration_match = re.search(r'(\d+(?:\.\d+)?)\s*(min|hour)', filename)
                if duration_match:
                    duration_str = f"{duration_match.group(1)} {duration_match.group(2)}"
                else:
                    duration_str = "Unknown"
                
                # Extract storm number
                storm_match = re.search(r'Storm (\d+)', filename)
                storm_num = storm_match.group(1) if storm_match else "?"
                
                # Create label
                label = f"{duration_str} (Storm {storm_num})"
                
                # Plot the data
                plt.plot(time_hours, total_flow, 
                        color=colors[i], 
                        linewidth=1.5, 
                        label=label,
                        alpha=0.8)
                
                # Track maximum values for axis scaling
                if time_hours:
                    max_time = max(max_time, max(time_hours))
                if total_flow:
                    max_flow = max(max_flow, max(total_flow))
                
                print(f"   ✅ {filename}: {len(time_min)} data points, peak flow: {max(total_flow):.3f} m³/s")
            
            else:
                print(f"   ❌ Failed to parse: {filename}")
                
        except Exception as e:
            print(f"   ❌ Error processing {filename}: {e}")
    
    # Customize the plot
    plt.title('NF_ILSAX_Catchments Storm Events - Flow Rate Comparison\n'
              'North Fremantle Pedestrian Infrastructure - 10% AEP Events', 
              fontsize=16, fontweight='bold', pad=20)
    
    plt.xlabel('Time (hours)', fontsize=12, fontweight='bold')
    plt.ylabel('Flow Rate (m³/s)', fontsize=12, fontweight='bold')
    
    # Set axis limits with some margin
    plt.xlim(0, max_time * 1.1 if max_time > 0 else 10)
    plt.ylim(0, max_flow * 1.1 if max_flow > 0 else 1)
    
    # Add grid
    plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    
    # Legend - split into two columns if many items
    if len(storm_files) > 12:
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', 
                  fontsize=8, ncol=2)
    else:
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', 
                  fontsize=9)
    
    # Adjust layout to prevent legend cutoff
    plt.tight_layout()
    
    # Add text box with summary statistics
    stats_text = f"""Storm File Statistics:
• Total files: {len(storm_files)}
• Max flow rate: {max_flow:.3f} m³/s
• Max duration: {max_time:.1f} hours
• Data source: DRAINS model outputs"""
    
    plt.text(0.02, 0.98, stats_text, 
             transform=plt.gca().transAxes, 
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
             fontsize=9)
    
    # Save the plot
    output_path = "NF_ILSAX_Catchments_Time_Series_Plot.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"\n📈 Plot saved as: {output_path}")
    
    # Don't show the plot to avoid hanging in terminal
    # plt.show()
    
    return output_path

def main():
    """Main function to run the plotting"""
    print("🌧️ NF_ILSAX_Catchments Time Series Plotter")
    print("=" * 50)
    
    try:
        # Quick test of a single file first
        test_file = r"DRAINS\NF_ILSAX_Catchments_10% AEP, 1 hour burst, Storm 8.ts1"
        if os.path.exists(test_file):
            print(f"🔍 Testing single file: {test_file}")
            with open(test_file, 'r') as f:
                content = f.read()
            data = read_hydrograph_data_from_content(content)
            print(f"   ✅ Parsed {len(data.get('total_flow', []))} data points")
            if data.get('total_flow'):
                max_flow = max(data['total_flow'])
                print(f"   ✅ Max flow: {max_flow:.6f} m³/s")
        
        output_file = plot_nf_ilsax_catchments()
        
        if output_file:
            print(f"\n✅ Success! Time series plot created.")
            print(f"📂 Output file: {output_file}")
            print(f"\n💡 The plot shows:")
            print(f"   • All NF_ILSAX_Catchments storm events on one graph")
            print(f"   • Different colors for each storm duration")
            print(f"   • Time axis in hours, flow rate in m³/s")
            print(f"   • Legend showing duration and storm number")
        else:
            print(f"\n❌ Failed to create plot")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
