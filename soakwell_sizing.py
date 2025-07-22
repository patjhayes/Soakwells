#!/usr/bin/env python3
"""
Soakwell Sizing Calculator
Based on formulas from Stormwater Management Manual for Western Australia - Chapter 9
References: Engineers Australia (2006) and Argue (2004)
"""

import math

def calculate_inflow_volume(C, i, A, D):
    """
    Calculate inflow volume based on rainfall and catchment characteristics
    
    Parameters:
    C (float): Runoff coefficient (dimensionless, 0-1)
    i (float): Probabilistic rainfall intensity (mm/hr)
    A (float): Contributing area connected to infiltration system (m²)
    D (float): Storm duration (hours)
    
    Returns:
    float: Inflow volume (m³)
    """
    V = (C * i * A * D) / 1000
    return V

def calculate_soakwell_diameter(V, ks=1e-5, t=60, Sr=1.0):
    """
    Calculate soakwell diameter using Argue (2004) formula
    Formula: d = √[4V/(π + 120*ks*t/Sr)]
    
    Parameters:
    V (float): Storage volume (m³)
    ks (float): Soil saturated hydraulic conductivity (m/s), default 1e-5 m/s
    t (float): Time base of design storm runoff hydrograph (minutes), default 60 min
    Sr (float): Soil moderation factor, default 1.0
    
    Returns:
    float: Soakwell diameter (m)
    """
    # Convert time from minutes to seconds for consistency with ks units
    t_seconds = t * 60
    
    # Calculate denominator
    denominator = math.pi + (120 * ks * t_seconds / Sr)
    
    # Calculate diameter
    d = math.sqrt(4 * V / denominator)
    
    return d

def calculate_emptying_time(d):
    """
    Calculate emptying time using Argue (2004) formula
    Formula: T = 4.6*d / log10(4/d)
    
    Note: This formula has constraints - it's only valid when d < 4m
    
    Parameters:
    d (float): Soakwell diameter (m)
    
    Returns:
    float: Emptying time (hours), or None if formula is not applicable
    """
    if d <= 0:
        raise ValueError("Diameter must be positive")
    
    # Check if formula is valid
    if d >= 4:
        print(f"Warning: d = {d:.2f} m >= 4 m. Emptying time formula not applicable.")
        print("Consider multiple smaller soakwells or alternative design.")
        return None
    
    try:
        T = (4.6 * d) / math.log10(4 / d)
        if T < 0:
            print(f"Warning: Negative emptying time calculated. Formula may not be valid for d = {d:.2f} m")
            return None
        return T
    except (ValueError, ZeroDivisionError):
        print(f"Error: Cannot calculate emptying time for d = {d:.2f} m")
        return None

def alternative_design_multiple_soakwells(V, max_diameter=3.5, ks=1e-5, t=60, Sr=1.0):
    """
    Calculate alternative design using multiple smaller soakwells
    
    Parameters:
    V (float): Total required storage volume (m³)
    max_diameter (float): Maximum allowable diameter (m)
    ks, t, Sr: Soil and design parameters
    
    Returns:
    dict: Alternative design parameters
    """
    # Calculate diameter for full volume
    d_full = calculate_soakwell_diameter(V, ks, t, Sr)
    
    if d_full <= max_diameter:
        return None  # Single soakwell is adequate
    
    # Calculate volume per soakwell with max diameter
    V_per_well = V * (max_diameter / d_full)**2
    
    # Calculate number of soakwells needed
    n_wells = math.ceil(V / V_per_well)
    
    # Recalculate actual volume per well
    V_actual_per_well = V / n_wells
    d_actual = calculate_soakwell_diameter(V_actual_per_well, ks, t, Sr)
    
    return {
        'number_of_wells': n_wells,
        'volume_per_well': V_actual_per_well,
        'diameter_per_well': d_actual,
        'total_volume': V,
        'max_diameter_limit': max_diameter
    }

def soakwell_design(V, ks=1e-5, t=60, Sr=1.0, H=None):
    """
    Complete soakwell design calculation
    
    Parameters:
    V (float): Required storage volume (m³)
    ks (float): Soil saturated hydraulic conductivity (m/s)
    t (float): Time base of design storm runoff hydrograph (minutes)
    Sr (float): Soil moderation factor
    H (float): Soakwell height (m), optional for validation
    
    Returns:
    dict: Design parameters
    """
    print("=" * 60)
    print("SOAKWELL SIZING CALCULATION")
    print("=" * 60)
    print(f"Required Storage Volume (V): {V:.2f} m³")
    print(f"Soil hydraulic conductivity (ks): {ks:.2e} m/s")
    print(f"Storm duration (t): {t:.0f} minutes")
    print(f"Soil moderation factor (Sr): {Sr:.2f}")
    print("-" * 60)
    
    # Calculate diameter
    d = calculate_soakwell_diameter(V, ks, t, Sr)
    print(f"Calculated soakwell diameter (d): {d:.2f} m")
    
    # Check if alternative design is needed
    alternative = alternative_design_multiple_soakwells(V, 3.5, ks, t, Sr)
    if alternative:
        print("\nALTERNATIVE DESIGN (Multiple Soakwells):")
        print(f"Number of soakwells: {alternative['number_of_wells']}")
        print(f"Diameter per soakwell: {alternative['diameter_per_well']:.2f} m")
        print(f"Volume per soakwell: {alternative['volume_per_well']:.2f} m³")
        
        # Calculate emptying time for alternative design
        T_alt = calculate_emptying_time(alternative['diameter_per_well'])
        if T_alt:
            print(f"Emptying time per soakwell: {T_alt:.2f} hours ({T_alt/24:.1f} days)")
    
    # If height is provided, check the approximation d ≈ H
    if H is not None:
        print(f"\nProvided soakwell height (H): {H:.2f} m")
        ratio = d / H
        print(f"Diameter to height ratio (d/H): {ratio:.2f}")
        if abs(ratio - 1.0) > 0.2:  # More than 20% difference
            print("Warning: The formula assumes d ≈ H. Consider adjusting dimensions.")
    
        # Calculate actual volume with calculated diameter
        actual_volume = math.pi * (d/2)**2 * H
        print(f"Actual volume with calculated diameter: {actual_volume:.2f} m³")
        volume_ratio = actual_volume / V
        print(f"Volume ratio (actual/required): {volume_ratio:.2f}")
    
    # Calculate emptying time for single soakwell
    T = calculate_emptying_time(d)
    if T is not None:
        print(f"\nEmptying time (T): {T:.2f} hours")
        print(f"Emptying time: {T:.1f} hours = {T/24:.1f} days")
    
    print("-" * 60)
    
    return {
        'diameter': d,
        'volume_required': V,
        'emptying_time_hours': T if T is not None else None,
        'ks': ks,
        'storm_duration_min': t,
        'soil_moderation_factor': Sr,
        'height': H,
        'alternative_design': alternative
    }

def example_inflow_calculation():
    """
    Example calculation of inflow volume
    """
    print("\n" + "=" * 60)
    print("EXAMPLE INFLOW VOLUME CALCULATION")
    print("=" * 60)
    
    # Example parameters
    C = 0.8  # Runoff coefficient for urban area
    i = 50   # Rainfall intensity (mm/hr) - 10 year ARI
    A = 500  # Contributing area (m²) - typical residential lot
    D = 1.0  # Storm duration (hours)
    
    V_inflow = calculate_inflow_volume(C, i, A, D)
    
    print(f"Runoff coefficient (C): {C}")
    print(f"Rainfall intensity (i): {i} mm/hr")
    print(f"Contributing area (A): {A} m²")
    print(f"Storm duration (D): {D} hours")
    print(f"Calculated inflow volume: {V_inflow:.2f} m³")
    
    return V_inflow

# Main execution
if __name__ == "__main__":
    # Example inflow calculation
    V_example = example_inflow_calculation()
    
    # Main calculation with V = 40 m³
    V = 40.0  # Storage volume in m³
    
    # Soil parameters (these should be determined from site investigation)
    ks_sandy = 1e-4   # Sandy soil (higher permeability)
    ks_clay = 1e-6    # Clay soil (lower permeability)
    ks_medium = 1e-5  # Medium soil (default)
    
    # Design scenarios
    print("\n" + "=" * 80)
    print("SOAKWELL DESIGN SCENARIOS")
    print("=" * 80)
    
    # Scenario 1: Medium permeability soil
    print("\nSCENARIO 1: Medium permeability soil")
    result1 = soakwell_design(V=V, ks=ks_medium, t=60, Sr=1.0, H=3.0)
    
    # Scenario 2: Sandy soil (higher permeability)
    print("\nSCENARIO 2: Sandy soil (higher permeability)")
    result2 = soakwell_design(V=V, ks=ks_sandy, t=60, Sr=1.0, H=3.0)
    
    # Scenario 3: Clay soil (lower permeability)
    print("\nSCENARIO 3: Clay soil (lower permeability)")
    result3 = soakwell_design(V=V, ks=ks_clay, t=60, Sr=1.0, H=3.0)
    
    # Summary comparison
    print("\n" + "=" * 80)
    print("SUMMARY COMPARISON")
    print("=" * 80)
    print(f"{'Soil Type':<20} {'ks (m/s)':<12} {'Diameter (m)':<15} {'Emptying Time (hrs)':<20}")
    print("-" * 80)
    
    # Handle potential None values for emptying time
    def format_emptying_time(t_hours):
        return f"{t_hours:.2f}" if t_hours is not None else "N/A (d >= 4m)"
    
    print(f"{'Medium':<20} {ks_medium:<12.2e} {result1['diameter']:<15.2f} {format_emptying_time(result1['emptying_time_hours']):<20}")
    print(f"{'Sandy':<20} {ks_sandy:<12.2e} {result2['diameter']:<15.2f} {format_emptying_time(result2['emptying_time_hours']):<20}")
    print(f"{'Clay':<20} {ks_clay:<12.2e} {result3['diameter']:<15.2f} {format_emptying_time(result3['emptying_time_hours']):<20}")
    
    print("\n" + "=" * 80)
    print("DESIGN NOTES:")
    print("=" * 80)
    print("1. Formula assumes d ≈ H (diameter approximately equals height)")
    print("2. Soil hydraulic conductivity (ks) should be determined from site testing")
    print("3. Consider local regulations for minimum emptying times")
    print("4. Pre-treatment may be required to prevent clogging")
    print("5. Minimum separation to groundwater typically required")
    print("6. Setback distances from buildings must be considered")
    print("=" * 80)
