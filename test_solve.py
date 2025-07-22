#!/usr/bin/env python3
"""
Test script for the comprehensive solve functionality
"""

import math

def get_standard_soakwell_specs(diameter, depth):
    """Get manufacturer specifications for standard concrete soakwells"""
    dia_mm = int(diameter * 1000)
    depth_mm = int(depth * 1000)
    
    specs_data = {
        (600, 600): {"capacity_L": 175, "weight_kg": 150, "price_aud": 231},
        (900, 600): {"capacity_L": 386, "weight_kg": 280, "price_aud": 308},
        (900, 900): {"capacity_L": 570, "weight_kg": 420, "price_aud": 286},
        (900, 1200): {"capacity_L": 760, "weight_kg": 560, "price_aud": 319},
        (1200, 600): {"capacity_L": 688, "weight_kg": 390, "price_aud": 319},
        (1200, 900): {"capacity_L": 1000, "weight_kg": 650, "price_aud": 341},
        (1200, 1200): {"capacity_L": 1360, "weight_kg": 780, "price_aud": 385},
        (1200, 1500): {"capacity_L": 1560, "weight_kg": 975, "price_aud": 385},
        (1500, 900): {"capacity_L": 1550, "weight_kg": 560, "price_aud": 396},
        (1500, 1200): {"capacity_L": 2090, "weight_kg": 1080, "price_aud": 451},
        (1500, 1500): {"capacity_L": 2560, "weight_kg": 1350, "price_aud": 528},
        (1800, 600): {"capacity_L": 1520, "weight_kg": 750, "price_aud": 385},
        (1800, 900): {"capacity_L": 2190, "weight_kg": 1100, "price_aud": 440},
        (1800, 1200): {"capacity_L": 3050, "weight_kg": 1500, "price_aud": 583},
        (1800, 1500): {"capacity_L": 3820, "weight_kg": 1852, "price_aud": 671},
        (1800, 1800): {"capacity_L": 4580, "weight_kg": 2200, "price_aud": 693},
    }
    
    key = (dia_mm, depth_mm)
    if key in specs_data:
        specs = specs_data[key].copy()
        specs['capacity_m3'] = specs['capacity_L'] / 1000.0
        specs['available'] = True
        return specs
    else:
        volume_m3 = math.pi * (diameter/2)**2 * depth
        return {
            'capacity_m3': volume_m3,
            'capacity_L': volume_m3 * 1000,
            'weight_kg': None,
            'price_aud': None,
            'available': False
        }

def test_comprehensive_solve():
    """Test the comprehensive solve function structure"""
    # Standard soakwell sizes available from manufacturer
    standard_diameters = [0.6, 0.9, 1.2, 1.5, 1.8]  # meters
    standard_depths = [0.6, 0.9, 1.2, 1.5, 1.8]     # meters
    max_soakwells = 5  # Reduced for testing
    
    print("Testing comprehensive solve function structure...")
    print(f"Standard diameters: {standard_diameters}")
    print(f"Standard depths: {standard_depths}")
    print(f"Max soakwells: {max_soakwells}")
    
    # Calculate total combinations
    total_combinations = len(standard_diameters) * len(standard_depths) * max_soakwells
    print(f"Total configurations to test: {total_combinations}")
    
    # Test manufacturer specs lookup
    test_configs = 0
    available_configs = 0
    
    for diameter in standard_diameters:
        for depth in standard_depths:
            specs = get_standard_soakwell_specs(diameter, depth)
            test_configs += 1
            
            if specs['available']:
                available_configs += 1
                print(f"✅ {diameter}m × {depth}m: {specs['capacity_m3']:.2f}m³, ${specs['price_aud']}")
            else:
                print(f"❌ {diameter}m × {depth}m: Custom size, {specs['capacity_m3']:.2f}m³")
    
    print(f"\nManufacturer specifications:")
    print(f"- Total size combinations: {test_configs}")
    print(f"- Standard sizes available: {available_configs}")
    print(f"- Custom sizes needed: {test_configs - available_configs}")
    
    # Test configuration naming
    print(f"\nExample configuration names:")
    for num in [1, 3, 5]:
        for d, depth in [(0.9, 0.9), (1.2, 1.2), (1.8, 1.5)]:
            config_name = f"{num}x {d:.1f}m ⌀ x {depth:.1f}m deep"
            specs = get_standard_soakwell_specs(d, depth)
            total_vol = specs['capacity_m3'] * num
            total_cost = specs['price_aud'] * num if specs['available'] else None
            print(f"  {config_name}: {total_vol:.1f}m³, ${total_cost if total_cost else 'Custom'}")

if __name__ == "__main__":
    test_comprehensive_solve()
