#!/usr/bin/env python3
"""
Diagnostic Tool for TS1 Files
Quick check to identify issues with .ts1 files before running the full dashboard
"""

import sys
import os
import traceback

def read_hydrograph_data_from_content(content):
    """
    Read hydrograph data from uploaded file content
    """
    data = {
        'time_min': [],
        'cat1240_flow': [],
        'cat3_flow': [],
        'total_flow': []
    }
    
    lines = content.split('\n')
    
    # Find the start of data (after header lines) - try multiple header patterns
    data_start = 0
    header_patterns = [
        'Time (min)',
        'Time(min)',
        'Time',
        'time',
        'TIME'
    ]
    
    print(f"   Looking for data start...")
    for i, line in enumerate(lines[:20]):  # Check first 20 lines
        line_lower = line.lower().strip()
        print(f"   Line {i+1}: {line[:60]}...")
        
        # Check for common header patterns
        if any(pattern.lower() in line_lower for pattern in header_patterns):
            data_start = i + 1
            print(f"   Found header at line {i+1}")
            break
        # Also check if line starts with numbers (direct data start)
        elif line.strip() and not line.startswith('!') and ',' in line:
            parts = line.split(',')
            try:
                # Try to parse first two values as numbers
                float(parts[0])
                float(parts[1]) if len(parts) > 1 else 0
                data_start = i
                print(f"   Found data start at line {i+1} (no header)")
                break
            except (ValueError, IndexError):
                continue
    
    # Parse data lines
    line_count = 0
    successful_lines = 0
    
    for line in lines[data_start:]:
        line = line.strip()
        if line and not line.startswith('!'):
            parts = line.split(',')
            
            # Try to parse with different column configurations
            try:
                if len(parts) >= 3:
                    # Standard format: Time, Cat1, Cat2, ...
                    time_min = float(parts[0])
                    cat1 = float(parts[1])
                    cat2 = float(parts[2])
                    total = cat1 + cat2
                elif len(parts) >= 2:
                    # Simplified format: Time, Total_Flow
                    time_min = float(parts[0])
                    total = float(parts[1])
                    cat1 = total  # Assume single catchment
                    cat2 = 0.0
                else:
                    continue
                
                data['time_min'].append(time_min)
                data['cat1240_flow'].append(cat1)
                data['cat3_flow'].append(cat2)
                data['total_flow'].append(total)
                
                successful_lines += 1
                line_count += 1
                
                # Safety limit
                if line_count > 10000:
                    print(f"   WARNING: File truncated at 10,000 lines for safety")
                    break
                    
            except (ValueError, IndexError):
                continue
    
    print(f"   Parsed {successful_lines} valid data lines")
    return data

def diagnose_ts1_files(folder_path):
    """
    Diagnose all .ts1 files in a folder
    """
    print("TS1 File Diagnostic Tool")
    print("=" * 50)
    
    ts1_files = [f for f in os.listdir(folder_path) if f.endswith('.ts1')]
    
    if not ts1_files:
        print("No .ts1 files found in the directory")
        return
    
    print(f"Found {len(ts1_files)} .ts1 files:")
    
    for filename in ts1_files:
        filepath = os.path.join(folder_path, filename)
        print(f"\n📄 {filename}")
        print("-" * 30)
        
        try:
            # Read file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_size = len(content)
            line_count = len(content.split('\n'))
            
            print(f"   File size: {file_size:,} characters")
            print(f"   Total lines: {line_count:,}")
            
            # Parse data
            data = read_hydrograph_data_from_content(content)
            
            if len(data['time_min']) > 0:
                duration = max(data['time_min']) - min(data['time_min'])
                peak_flow = max(data['total_flow'])
                total_volume = sum(data['total_flow']) * 60  # rough estimate
                
                print(f"   Data points: {len(data['time_min']):,}")
                print(f"   Duration: {duration:.1f} minutes")
                print(f"   Peak flow: {peak_flow:.6f} m³/s")
                print(f"   Total volume: {total_volume:.2f} m³")
                print(f"   ✅ File looks good")
                
                # Check for potential issues
                if len(data['time_min']) > 5000:
                    print(f"   ⚠️  Large dataset ({len(data['time_min'])} points) - may be slow")
                
                if peak_flow > 1.0:
                    print(f"   ⚠️  Very high peak flow ({peak_flow:.3f} m³/s)")
                
                if duration > 1440:  # 24 hours
                    print(f"   ⚠️  Very long duration ({duration/60:.1f} hours)")
                    
            else:
                print(f"   ❌ No valid data found")
                
                # Show first few lines for debugging
                lines = content.split('\n')[:10]
                print(f"   First 10 lines:")
                for i, line in enumerate(lines):
                    print(f"   {i+1:2d}: {line[:60]}...")
                
        except Exception as e:
            print(f"   ❌ Error reading file: {str(e)}")
            print(f"   {traceback.format_exc()}")

if __name__ == "__main__":
    # Use current directory if no path provided
    folder_path = r"c:\Users\Patrick.Hayes\OneDrive - Aurecon Group\Documents\North Fremantle Ped\DRAINS\_data"
    
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    
    if os.path.exists(folder_path):
        diagnose_ts1_files(folder_path)
    else:
        print(f"Path not found: {folder_path}")
