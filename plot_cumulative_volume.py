#!/usr/bin/env python3
"""
Plot NF_ILSAX_Catchments Cumulative Volume Time Series
Creates a comprehensive cumulative volume plot of all NF_ILSAX_Catchments storm files
Shows total water volume accumulated over time for each storm event
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

def calculate_cumulative_volume(time_min, flow_m3s):
    """
    Calculate cumulative volume from flow rate data
    
    Parameters:
    time_min: list of time points in minutes
    flow_m3s: list of flow rates in m³/s
    
    Returns:
    list: cumulative volumes in m³
    """
    if not time_min or not flow_m3s or len(time_min) != len(flow_m3s):
        return []
    
    cumulative_volume = []
    total_volume = 0.0
    
    for i in range(len(time_min)):
        if i == 0:
            # First point - no previous interval
            dt_seconds = 0
        else:
            # Time interval in seconds
            dt_minutes = time_min[i] - time_min[i-1]
            dt_seconds = dt_minutes * 60
            
            # Add volume for this interval (flow rate * time)
            # Use average flow rate over the interval
            avg_flow = (flow_m3s[i] + flow_m3s[i-1]) / 2
            volume_increment = avg_flow * dt_seconds
            total_volume += volume_increment
        
        cumulative_volume.append(total_volume)
    
    return cumulative_volume

def plot_nf_ilsax_cumulative_volume():
    """Plot cumulative volume for all NF_ILSAX_Catchments files"""
    
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
    max_volume = 0
    valid_files = 0
    
    # Storage for summary statistics
    storm_summary = []
    
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
                
                # Calculate cumulative volume
                cumulative_volume = calculate_cumulative_volume(time_min, total_flow)
                
                if not cumulative_volume:
                    print(f"   ❌ Failed to calculate cumulative volume: {filename}")
                    continue
                
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
                
                # Plot the cumulative volume
                plt.plot(time_hours, cumulative_volume, 
                        color=colors[i], 
                        linewidth=2.0, 
                        label=label,
                        alpha=0.8)
                
                # Track maximum values for axis scaling
                if time_hours:
                    max_time = max(max_time, max(time_hours))
                if cumulative_volume:
                    final_volume = cumulative_volume[-1]
                    max_volume = max(max_volume, final_volume)
                
                # Store summary data
                storm_summary.append({
                    'filename': filename,
                    'duration': duration_str,
                    'storm_num': storm_num,
                    'final_volume_m3': final_volume,
                    'duration_hours': max(time_hours) if time_hours else 0,
                    'peak_flow_m3s': max(total_flow) if total_flow else 0
                })
                
                valid_files += 1
                print(f"   ✅ {filename}: {len(time_min)} points, final volume: {final_volume:.1f} m³")
            
            else:
                print(f"   ❌ Failed to parse: {filename}")
                
        except Exception as e:
            print(f"   ❌ Error processing {filename}: {e}")
    
    if valid_files == 0:
        print("❌ No valid storm files could be processed")
        return None
    
    # Customize the plot
    plt.title('NF_ILSAX_Catchments Storm Events - Cumulative Volume Comparison\n'
              'North Fremantle Pedestrian Infrastructure - 10% AEP Events', 
              fontsize=16, fontweight='bold', pad=20)
    
    plt.xlabel('Time (hours)', fontsize=12, fontweight='bold')
    plt.ylabel('Cumulative Volume (m³)', fontsize=12, fontweight='bold')
    
    # Set axis limits with some margin
    plt.xlim(0, max_time * 1.1 if max_time > 0 else 10)
    plt.ylim(0, max_volume * 1.1 if max_volume > 0 else 100)
    
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
    
    # Calculate summary statistics
    volumes = [s['final_volume_m3'] for s in storm_summary]
    durations = [s['duration_hours'] for s in storm_summary]
    
    # Add text box with summary statistics
    stats_text = f"""Cumulative Volume Statistics:
• Total files processed: {valid_files}/{len(storm_files)}
• Max cumulative volume: {max_volume:.1f} m³
• Min cumulative volume: {min(volumes):.1f} m³
• Average final volume: {np.mean(volumes):.1f} m³
• Max storm duration: {max(durations):.1f} hours
• Data source: DRAINS model outputs (.ts1 format)"""
    
    plt.text(0.02, 0.98, stats_text, 
             transform=plt.gca().transAxes, 
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
             fontsize=9)
    
    # Save the plot
    output_path = "NF_ILSAX_Catchments_Cumulative_Volume_Plot.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"\n📈 Cumulative volume plot saved as: {output_path}")
    
    # Print summary table
    print(f"\n📋 Storm Volume Summary:")
    print(f"{'Duration':<15} {'Storm':<5} {'Final Volume (m³)':<18} {'Duration (hrs)':<15}")
    print("-" * 60)
    
    # Sort by final volume for summary
    storm_summary.sort(key=lambda x: x['final_volume_m3'], reverse=True)
    
    for storm in storm_summary[:10]:  # Show top 10
        print(f"{storm['duration']:<15} {storm['storm_num']:<5} {storm['final_volume_m3']:<18.1f} {storm['duration_hours']:<15.1f}")
    
    if len(storm_summary) > 10:
        print(f"... and {len(storm_summary) - 10} more storms")
    
    return output_path

def main():
    """Main function to run the cumulative volume plotting"""
    print("📊 NF_ILSAX_Catchments Cumulative Volume Plotter")
    print("=" * 60)
    print("🎯 This script creates a cumulative volume time series plot")
    print("   showing total water volume accumulated over time")
    print("=" * 60)
    
    try:
        # Quick test of our corrected parsing first
        test_file = r"DRAINS\NF_ILSAX_Catchments_10% AEP, 1 hour burst, Storm 8.ts1"
        if os.path.exists(test_file):
            print(f"🔍 Testing file parsing: {os.path.basename(test_file)}")
            with open(test_file, 'r') as f:
                content = f.read()
            data = read_hydrograph_data_from_content(content)
            if data.get('total_flow'):
                cumulative = calculate_cumulative_volume(data['time_min'], data['total_flow'])
                print(f"   ✅ Sample cumulative volume: {cumulative[-1] if cumulative else 0:.1f} m³")
        
        output_file = plot_nf_ilsax_cumulative_volume()
        
        if output_file:
            print(f"\n✅ Success! Cumulative volume plot created.")
            print(f"📂 Output file: {output_file}")
            print(f"\n💡 The plot shows:")
            print(f"   • Cumulative water volume (m³) vs time (hours)")
            print(f"   • All NF_ILSAX_Catchments storm events")
            print(f"   • Different colors for each storm duration")
            print(f"   • Final volumes for comparison of total storm water")
            print(f"   • Useful for soakwell storage sizing")
            
            # Check if the file was actually created
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"📏 Plot file size: {file_size:,} bytes")
            else:
                print(f"⚠️ Plot file not found at expected location")
        else:
            print(f"\n❌ Failed to create plot")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
