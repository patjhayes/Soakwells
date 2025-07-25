#!/usr/bin/env python3
"""
Test .ts1 file parsing with corrected format understanding
"""

import os
from core_soakwell_analysis import read_hydrograph_data_from_content

def test_single_file():
    """Test parsing a single .ts1 file"""
    test_file = r"DRAINS\NF_ILSAX_Catchments_10% AEP, 1 hour burst, Storm 8.ts1"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    print(f"🔍 Testing file: {test_file}")
    
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Show the file structure
    lines = content.strip().split('\n')
    print(f"📄 Total lines: {len(lines)}")
    print(f"📄 First 10 lines:")
    for i, line in enumerate(lines[:10]):
        print(f"   {i+1:2d}: {line}")
    
    # Parse with corrected function
    data = read_hydrograph_data_from_content(content)
    
    print(f"\n📊 Parsing results:")
    print(f"   Time points: {len(data['time_min'])}")
    print(f"   Flow points: {len(data['total_flow'])}")
    
    if data['total_flow']:
        max_flow = max(data['total_flow'])
        min_flow = min(data['total_flow'])
        non_zero_flows = [f for f in data['total_flow'] if f > 0]
        
        print(f"   Max flow: {max_flow:.6f} m³/s")
        print(f"   Min flow: {min_flow:.6f} m³/s")
        print(f"   Non-zero flows: {len(non_zero_flows)}")
        
        if non_zero_flows:
            print(f"   Max non-zero flow: {max(non_zero_flows):.6f} m³/s")
            
        # Show first few non-zero flows
        print(f"   Sample flows (first 5):")
        for i, flow in enumerate(data['total_flow'][:5]):
            time = data['time_min'][i] if i < len(data['time_min']) else 0
            print(f"      t={time:.1f}min: {flow:.6f} m³/s")

if __name__ == "__main__":
    test_single_file()
