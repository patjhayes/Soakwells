#!/usr/bin/env python3
"""
Simple verification of .ts1 file parsing
"""

def test_ts1_format():
    """Test the .ts1 file format understanding"""
    
    # Simulate a typical .ts1 file structure
    sample_content = """! File created from: C:\\Users\\Patrick.Hayes\\OneDrive - Aurecon Group\\Documents\\North Fremantle Ped\\DRAINS\\Hydrology_ILSAX.drn
! Storm event:10% AEP_1 hour burst_Storm 8
! Default ILSAX model: Freo_ILSAX, 1.5, 10, 10, Soil Type = 2
! Timestep: 1 min
! Number of catchments: 1
1,95
Start_Index,1
End_Index,95
Time (min),Cat3
1.000,0.000
2.000,0.000
3.000,0.001
4.000,0.002
5.000,0.005"""
    
    lines = sample_content.strip().split('\n')
    print("📄 Sample .ts1 file structure:")
    for i, line in enumerate(lines):
        print(f"   Line {i+1:2d}: {line}")
    
    print(f"\n🔍 According to format:")
    print(f"   Lines 1-5: Metadata (start with '!')")
    print(f"   Line 6: 1,95 (metadata: 1 catchment, 95 points)")
    print(f"   Line 7: Start_Index,1 (metadata)")
    print(f"   Line 8: End_Index,95 (metadata)")
    print(f"   Line 9: Time (min),Cat3 (HEADER)")
    print(f"   Line 10+: Data (time, flow)")
    
    # Test our parsing logic
    header_line = lines[8]  # Line 9 (index 8)
    print(f"\n✅ Header line (line 9): '{header_line}'")
    
    data_lines = lines[9:]  # Line 10+ (index 9+)
    print(f"✅ Data lines start from line 10:")
    for i, line in enumerate(data_lines):
        parts = line.split(',')
        if len(parts) == 2:
            try:
                time_min = float(parts[0])
                flow_m3s = float(parts[1])
                print(f"   Data {i+1}: t={time_min:.1f}min, flow={flow_m3s:.6f}m³/s")
            except:
                print(f"   Data {i+1}: Invalid - {line}")

if __name__ == "__main__":
    test_ts1_format()
