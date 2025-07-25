#!/usr/bin/env python3
"""
Test cumulative volume calculation with sample data
"""

def calculate_cumulative_volume(time_min, flow_m3s):
    """Calculate cumulative volume from flow rate data"""
    if not time_min or not flow_m3s or len(time_min) != len(flow_m3s):
        return []
    
    cumulative_volume = []
    total_volume = 0.0
    
    for i in range(len(time_min)):
        if i == 0:
            dt_seconds = 0
        else:
            dt_minutes = time_min[i] - time_min[i-1]
            dt_seconds = dt_minutes * 60
            avg_flow = (flow_m3s[i] + flow_m3s[i-1]) / 2
            volume_increment = avg_flow * dt_seconds
            total_volume += volume_increment
        
        cumulative_volume.append(total_volume)
    
    return cumulative_volume

def test_cumulative_calculation():
    """Test the cumulative volume calculation with simple data"""
    print("🧪 Testing cumulative volume calculation")
    print("=" * 50)
    
    # Test data: 5 minutes with constant 0.001 m³/s flow
    time_min = [1.0, 2.0, 3.0, 4.0, 5.0]
    flow_m3s = [0.001, 0.001, 0.001, 0.001, 0.001]
    
    print(f"📊 Test data:")
    print(f"   Time points: {time_min}")
    print(f"   Flow rates: {flow_m3s} m³/s")
    
    cumulative = calculate_cumulative_volume(time_min, flow_m3s)
    
    print(f"\n📈 Cumulative volumes:")
    for i, (t, f, c) in enumerate(zip(time_min, flow_m3s, cumulative)):
        print(f"   t={t:.1f}min: flow={f:.3f}m³/s → cumulative={c:.3f}m³")
    
    # Expected: Each 1-minute interval at 0.001 m³/s should add 0.06 m³
    # (0.001 m³/s × 60 s = 0.06 m³ per minute)
    expected_final = 4 * 0.06  # 4 intervals × 0.06 m³ = 0.24 m³
    actual_final = cumulative[-1] if cumulative else 0
    
    print(f"\n✅ Expected final volume: ~{expected_final:.3f} m³")
    print(f"✅ Actual final volume: {actual_final:.3f} m³")
    print(f"✅ Calculation {'PASSED' if abs(actual_final - expected_final) < 0.01 else 'FAILED'}")

if __name__ == "__main__":
    test_cumulative_calculation()
