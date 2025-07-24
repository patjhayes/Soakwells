#!/usr/bin/env python3
"""
Interactive Soakwell Design Dashboard
Streamlit-based dashboard for dynamic soakwell analysis with file upload and parameter adjustment
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import math
import datetime
import traceback
import io
import tempfile
import os
import datetime

# French drain integration (with robust error handling)
FRENCH_DRAIN_AVAILABLE = False
try:
    from french_drain_integration import integrate_french_drain_analysis, add_french_drain_sidebar
    from report_generator import generate_calculation_report, display_mass_balance_summary
    FRENCH_DRAIN_AVAILABLE = True
except ImportError as e:
    # Don't show warning in sidebar yet - wait until sidebar is created
    pass
except Exception as e:
    # Handle any other import errors
    pass

# Set page config
st.set_page_config(
    page_title="Soakwell Design Dashboard",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_standard_soakwell_specs(diameter, depth):
    """
    Get manufacturer specifications for standard concrete soakwells
    Based on Perth Soakwells specifications from www.soakwells.com
    
    Returns:
    dict: Manufacturer specifications including capacity and weight
    """
    # Convert to mm for lookup
    dia_mm = int(diameter * 1000)
    depth_mm = int(depth * 1000)
    
    # Standard soakwell specifications from manufacturer
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
        # Calculate theoretical capacity if not a standard size
        volume_m3 = math.pi * (diameter/2)**2 * depth
        return {
            'capacity_m3': volume_m3,
            'capacity_L': volume_m3 * 1000,
            'weight_kg': None,
            'price_aud': None,
            'available': False
        }

# Import functions from our analysis module
@st.cache_data
def read_hydrograph_data_from_content(content):
    """
    Read hydrograph data from uploaded file content
    Handles both comma-separated and DRAINS TS1 formats
    
    Parameters:
    content (str): File content as string
    
    Returns:
    dict: Parsed hydrograph data
    """
    data = {
        'time_min': [],
        'cat1240_flow': [],
        'cat3_flow': [],
        'total_flow': []
    }
    
    lines = content.split('\n')
    lines = [line.strip() for line in lines if line.strip()]  # Remove empty lines
    
    # Check if this is a DRAINS TS1 format (time values on separate lines)
    time_header_found = False
    data_section = False
    
    # Look for time header
    for i, line in enumerate(lines):
        if line.lower().strip() in ['time (min)', 'time(min)', 'time']:
            time_header_found = True
            
            # Parse time values
            for j in range(i + 1, len(lines)):
                time_line = lines[j].strip()
                if time_line and not time_line.startswith('!'):
                    try:
                        time_val = float(time_line)
                        data['time_min'].append(time_val)
                    except ValueError:
                        # End of time data
                        break
            
            # For DRAINS TS1 time-only files, create a synthetic storm hydrograph for demonstration
            if len(data['time_min']) > 0:
                # Create a realistic storm hydrograph pattern
                import math
                duration = len(data['time_min'])
                peak_time = duration * 0.3  # Peak at 30% of duration
                
                for i, time_val in enumerate(data['time_min']):
                    # Create triangular hydrograph with some randomness
                    if i <= peak_time:
                        # Rising limb
                        intensity = (i / peak_time) * 0.1  # Peak at 0.1 m³/s
                    else:
                        # Falling limb
                        intensity = 0.1 * (1 - (i - peak_time) / (duration - peak_time))
                    
                    # Add some variability
                    intensity = max(0, intensity + 0.01 * math.sin(i * 0.5))
                    
                    # Split between two catchments
                    cat1_flow = intensity * 0.6
                    cat2_flow = intensity * 0.4
                    
                    data['cat1240_flow'].append(cat1_flow)
                    data['cat3_flow'].append(cat2_flow)
                    data['total_flow'].append(cat1_flow + cat2_flow)
            
            return data
    
    # If not DRAINS format, try comma-separated format
    if not time_header_found:
        
        # Find the start of data (after header lines) - try multiple header patterns
        data_start = 0
        header_patterns = [
            'Time (min)',
            'Time(min)',
            'Time',
            'time',
            'TIME'
        ]
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            line_lower = line_clean.lower()
            
            # Skip comment lines and DRAINS metadata lines
            if (line_clean.startswith('!') or 
                line_clean.startswith('Start_Index') or 
                line_clean.startswith('End_Index') or
                (line_clean.count(',') == 1 and line_clean.split(',')[0].isdigit() and line_clean.split(',')[1].isdigit())):
                continue
                
            # Check for proper CSV header with Time column
            if ',' in line_clean and any(pattern.lower() in line_lower for pattern in header_patterns):
                # Verify this looks like a proper CSV header
                parts = line_clean.split(',')
                if len(parts) >= 2 and 'time' in parts[0].lower():
                    data_start = i + 1
                    break
            # Also check if line starts with numbers (direct data start)
            elif line_clean and not line_clean.startswith('!') and ',' in line_clean:
                # Skip DRAINS metadata lines that look like "1,410"
                parts = line_clean.split(',')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit() and len(parts[0]) <= 3:
                    continue  # Skip lines like "1,410"
                    
                try:
                    # Try to parse first value as float (time) and second as float (flow)
                    time_val = float(parts[0])
                    if len(parts) > 1:
                        flow_val = float(parts[1])
                    # Additional check: time should be reasonable (not a large integer)
                    if time_val > 0 and time_val <= 10000:  # Reasonable time range
                        data_start = i
                        break
                except (ValueError, IndexError):
                    continue
        
        # Parse data lines
        line_count = 0
        successful_lines = 0
        
        for line_num, line in enumerate(lines[data_start:], start=data_start + 1):
            line = line.strip()
            
            # Skip comment lines, metadata lines, and empty lines
            if (not line or 
                line.startswith('!') or 
                line.startswith('Start_Index') or 
                line.startswith('End_Index')):
                continue
            
            # Skip DRAINS metadata lines like "1,410"
            if ',' in line:
                parts = line.split(',')
                if (len(parts) == 2 and 
                    parts[0].isdigit() and 
                    parts[1].isdigit() and 
                    len(parts[0]) <= 3 and
                    int(parts[0]) < 10):  # Skip lines like "1,410"
                    continue
            
            # Skip header lines that might appear in the data section
            if 'Time' in line and ',' in line and any(keyword in line.lower() for keyword in ['time', 'cat', 'flow']):
                continue
                
            if ',' in line:
                parts = line.split(',')
                
                # Try to parse with different column configurations
                try:
                    # Verify this looks like actual time-series data
                    time_min = float(parts[0])
                    
                    # Additional validation: time should be reasonable
                    if time_min <= 0 or time_min > 10000:
                        continue
                    
                    if len(parts) >= 3:
                        # Standard format: Time, Cat1, Cat2, ...
                        cat1 = float(parts[1])
                        cat2 = float(parts[2])
                        total = cat1 + cat2
                    elif len(parts) >= 2:
                        # Simplified format: Time, Total_Flow
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
                    
                    # Safety limit to prevent memory issues
                    if line_count > 10000:
                        st.warning(f"⚠️ File truncated at 10,000 lines for safety")
                        break
                        
                except (ValueError, IndexError) as e:
                    # Silently skip parsing errors for cleaner output
                    continue
        
        # Only show summary if successful parsing occurred
        if successful_lines > 0:
            pass  # Remove verbose output
        else:
            pass  # Remove verbose output
    
    return data

def calculate_soakwell_outflow_rate(diameter, ks=1e-5, Sr=1.0):
    """Calculate steady-state outflow rate from soakwell"""
    height = diameter
    base_area = math.pi * (diameter/2)**2
    wall_area = math.pi * diameter * height
    total_area = base_area + wall_area
    outflow_rate = ks * total_area / Sr
    return outflow_rate

@st.cache_data(max_entries=50)  # Limit cache size for memory management
def simulate_soakwell_performance(hydrograph_data, diameter, ks=1e-5, Sr=1.0, max_height=None, extend_to_hours=24):
    """
    Simulate soakwell performance over time using hydrograph data
    Extended to show complete emptying cycle up to specified hours
    
    Parameters:
    extend_to_hours: Extend simulation to this many hours to show emptying phase
    """
    if max_height is None:
        max_height = diameter
    
    # Safety checks
    if not hydrograph_data or len(hydrograph_data['time_min']) == 0:
        raise ValueError("No valid hydrograph data provided")
    
    if len(hydrograph_data['time_min']) != len(hydrograph_data['total_flow']):
        raise ValueError("Time and flow data arrays have different lengths")
    
    if len(hydrograph_data['time_min']) > 10000:
        raise ValueError(f"Dataset too large ({len(hydrograph_data['time_min'])} points). Limit to <10,000 points.")
    
    max_volume = math.pi * (diameter/2)**2 * max_height
    
    # Original inflow period
    original_time_min = hydrograph_data['time_min']
    original_inflow_rates = hydrograph_data['total_flow']  # m³/s
    original_length = len(original_time_min)
    
    # Extend time series to show emptying phase
    inflow_end_time = max(original_time_min)
    extend_to_min = extend_to_hours * 60
    
    # Create extended time series
    time_min = original_time_min.copy()
    inflow_rates = original_inflow_rates.copy()
    
    # Add emptying phase (no inflow, just outflow)
    if inflow_end_time < extend_to_min:
        # Add time points for emptying phase (every 5 minutes for reasonable resolution)
        emptying_interval = 5.0  # minutes
        emptying_times = []
        t = inflow_end_time + emptying_interval
        
        while t <= extend_to_min:
            emptying_times.append(t)
            t += emptying_interval
        
        # Extend arrays with zero inflow during emptying
        time_min.extend(emptying_times)
        inflow_rates.extend([0.0] * len(emptying_times))
    
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
        
        # Early termination if soakwell is empty and no more inflow
        if new_volume < 1e-6 and inflow == 0.0 and i > original_length:
            # Soakwell is essentially empty, truncate arrays here
            break
    
    # Truncate all arrays to match the actual simulation length if early termination occurred
    actual_length = len(stored_volume)
    time_min = time_min[:actual_length]
    inflow_rates = inflow_rates[:actual_length]
    outflow_rate = outflow_rate[:actual_length]
    water_level = water_level[:actual_length]
    overflow = overflow[:actual_length]
    cumulative_inflow = cumulative_inflow[:actual_length]
    cumulative_outflow = cumulative_outflow[:actual_length]
    
    # Calculate emptying time (time when volume drops to near zero after peak)
    emptying_time = None
    if len(stored_volume) > 0:
        peak_idx = stored_volume.index(max(stored_volume))
        for i in range(peak_idx, len(stored_volume)):
            if stored_volume[i] < 0.01 * max(stored_volume):  # 1% of peak volume
                emptying_time = time_min[i] - time_min[peak_idx]
                break
    
    return {
        'time_min': time_min,
        'time_hours': [t/60 for t in time_min],
        'inflow_rate': inflow_rates,
        'stored_volume': stored_volume,
        'outflow_rate': outflow_rate,
        'cumulative_inflow': cumulative_inflow,
        'cumulative_outflow': cumulative_outflow,
        'overflow_rate': overflow,
        'water_level': water_level,
        'max_volume': max_volume,
        'max_height': max_height,
        'diameter': diameter,
        'emptying_time_minutes': emptying_time  # Time in minutes to empty from peak to near-empty
    }

def scale_multiple_soakwell_results(single_result, num_soakwells, original_hydrograph):
    """
    Scale results from a single soakwell analysis to represent multiple soakwells
    
    Parameters:
    single_result (dict): Results from single soakwell with reduced inflow
    num_soakwells (int): Number of soakwells
    original_hydrograph (dict): Original hydrograph data before flow splitting
    
    Returns:
    dict: Scaled results representing all soakwells combined
    """
    # Scale volume-based results
    scaled_result = single_result.copy()
    
    # Scale volumes by number of soakwells
    scaled_result['stored_volume'] = [vol * num_soakwells for vol in single_result['stored_volume']]
    scaled_result['cumulative_inflow'] = [vol * num_soakwells for vol in single_result['cumulative_inflow']]
    scaled_result['cumulative_outflow'] = [vol * num_soakwells for vol in single_result['cumulative_outflow']]
    scaled_result['max_volume'] = single_result['max_volume'] * num_soakwells
    
    # Scale flow rates by number of soakwells
    scaled_result['outflow_rate'] = [rate * num_soakwells for rate in single_result['outflow_rate']]
    scaled_result['overflow_rate'] = [rate * num_soakwells for rate in single_result['overflow_rate']]
    
    # Use original inflow data
    scaled_result['inflow_rate'] = original_hydrograph['total_flow']
    
    # Add metadata about multiple soakwells
    scaled_result['num_soakwells'] = num_soakwells
    scaled_result['individual_diameter'] = single_result['diameter']
    scaled_result['individual_max_volume'] = single_result['max_volume']
    
    return scaled_result

def solve_for_minimum_soakwells(hydrograph_data_dict, ks=1e-5, Sr=1.0, max_soakwells=30):
    """
    Comprehensive solve function: Find all viable soakwell configurations
    Tests all diameter/depth/quantity combinations against all storm scenarios
    
    Parameters:
    hydrograph_data_dict: Dictionary of storm scenarios {filename: hydrograph_data}
    ks: Soil permeability (m/s) - FIXED parameter set by user
    Sr: Saturation ratio - FIXED parameter set by user
    max_soakwells: Maximum number of soakwells to test
    
    Returns:
    dict: Comprehensive results showing all viable configurations
    """
    # Standard soakwell sizes available from manufacturer
    standard_diameters = [0.6, 0.9, 1.2, 1.5, 1.8]  # meters
    standard_depths = [0.6, 0.9, 1.2, 1.5, 1.8]     # meters
    
    # Results storage
    all_configurations = []
    viable_configurations = []
    
    # Progress tracking
    total_combinations = len(standard_diameters) * len(standard_depths) * max_soakwells * len(hydrograph_data_dict)
    current_combination = 0
    
    # Test all diameter/depth combinations
    for diameter in standard_diameters:
        for depth in standard_depths:
            # Check if this is a standard manufacturer size
            specs = get_standard_soakwell_specs(diameter, depth)
            
            # Only process standard sizes - skip custom sizes
            if not specs['available']:
                continue
            
            # Test different numbers of soakwells for this size
            for num_soakwells in range(1, max_soakwells + 1):
                
                # Test against all storm scenarios
                scenario_results = {}
                all_scenarios_pass = True
                worst_case_storm = None
                worst_case_level = 0
                
                for filename, hydrograph_data in hydrograph_data_dict.items():
                    current_combination += 1
                    
                    try:
                        # Create scaled hydrograph data (each soakwell gets 1/num_soakwells of the total inflow)
                        scaled_hydrograph = {
                            'time_min': hydrograph_data['time_min'],
                            'total_flow': [flow / num_soakwells for flow in hydrograph_data['total_flow']],
                            'cat1240_flow': hydrograph_data.get('cat1240_flow', [flow / num_soakwells for flow in hydrograph_data['total_flow']]),
                            'cat3_flow': hydrograph_data.get('cat3_flow', [0.0] * len(hydrograph_data['total_flow']))
                        }
                        
                        # Simulate single soakwell performance
                        result = simulate_soakwell_performance(scaled_hydrograph, diameter, ks, Sr, depth, extend_to_hours=24)
                        
                        # Check if overflow occurs
                        peak_overflow = max(result['overflow_rate'])
                        max_water_level = max(result['water_level'])
                        
                        # Track worst case scenario (highest water level)
                        if max_water_level > worst_case_level:
                            worst_case_level = max_water_level
                            worst_case_storm = filename
                        
                        scenario_results[filename] = {
                            'peak_overflow': peak_overflow,
                            'max_water_level': max_water_level,
                            'passes': peak_overflow == 0
                        }
                        
                        # If any scenario fails, this configuration is not viable
                        if peak_overflow > 0:
                            all_scenarios_pass = False
                        
                    except Exception as e:
                        # If simulation fails, mark as failed
                        scenario_results[filename] = {
                            'peak_overflow': float('inf'),
                            'max_water_level': float('inf'),
                            'passes': False,
                            'error': str(e)
                        }
                        all_scenarios_pass = False
                
                # Calculate total system properties
                total_volume = specs['capacity_m3'] * num_soakwells
                total_cost = specs['price_aud'] * num_soakwells
                
                # Store configuration result
                config_result = {
                    'diameter': diameter,
                    'depth': depth,
                    'num_soakwells': num_soakwells,
                    'total_volume': total_volume,
                    'total_cost': total_cost,
                    'individual_volume': specs['capacity_m3'],
                    'standard_size': True,  # All configurations are now standard sizes
                    'all_scenarios_pass': all_scenarios_pass,
                    'worst_case_storm': worst_case_storm,
                    'worst_case_level': worst_case_level,
                    'scenario_results': scenario_results,
                    'configuration_name': f"{num_soakwells}x {diameter:.1f}m ⌀ x {depth:.1f}m deep"
                }
                
                all_configurations.append(config_result)
                
                # If this configuration works for all scenarios, add to viable list
                if all_scenarios_pass:
                    viable_configurations.append(config_result)
    
    # Sort viable configurations by various criteria
    viable_by_cost = sorted([c for c in viable_configurations if c['total_cost'] is not None], 
                           key=lambda x: x['total_cost'])
    viable_by_volume = sorted(viable_configurations, key=lambda x: x['total_volume'])
    viable_by_quantity = sorted(viable_configurations, key=lambda x: x['num_soakwells'])
    
    return {
        'total_configurations_tested': len(all_configurations),
        'viable_configurations': viable_configurations,
        'viable_count': len(viable_configurations),
        'all_configurations': all_configurations,
        'soil_conditions': {'ks': ks, 'Sr': Sr},
        'storm_scenarios': list(hydrograph_data_dict.keys()),
        'recommendations': {
            'minimum_cost': viable_by_cost[0] if viable_by_cost else None,
            'minimum_volume': viable_by_volume[0] if viable_by_volume else None,
            'minimum_quantity': viable_by_quantity[0] if viable_by_quantity else None
        }
    }

def create_performance_plots(results, scenario_name):
    """Create interactive plotly charts for soakwell performance"""
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Flow Rates', 'Storage Volume', 
                       'Water Level', 'Cumulative Volumes'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    time_hours = results['time_hours']
    
    # Plot 1: Flow rates
    fig.add_trace(
        go.Scatter(x=time_hours, y=results['inflow_rate'], 
                  name='Inflow Rate', line=dict(color='blue', width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=time_hours, y=results['outflow_rate'], 
                  name='Outflow Rate', line=dict(color='green', width=2)),
        row=1, col=1
    )
    if max(results['overflow_rate']) > 0:
        fig.add_trace(
            go.Scatter(x=time_hours, y=results['overflow_rate'], 
                      name='Overflow Rate', line=dict(color='red', width=2)),
            row=1, col=1
        )
    
    # Plot 2: Storage volume
    fig.add_trace(
        go.Scatter(x=time_hours, y=results['stored_volume'], 
                  name='Stored Volume', line=dict(color='purple', width=2)),
        row=1, col=2
    )
    # Add max capacity line
    fig.add_hline(y=results['max_volume'], line_dash="dash", line_color="red", 
                  annotation_text="Max Capacity", row=1, col=2)
    
    # Plot 3: Water level
    fig.add_trace(
        go.Scatter(x=time_hours, y=results['water_level'], 
                  name='Water Level', line=dict(color='orange', width=2)),
        row=2, col=1
    )
    # Add max height line
    fig.add_hline(y=results['max_height'], line_dash="dash", line_color="red", 
                  annotation_text="Max Height", row=2, col=1)
    
    # Plot 4: Cumulative volumes
    fig.add_trace(
        go.Scatter(x=time_hours, y=results['cumulative_inflow'], 
                  name='Cumulative Inflow', line=dict(color='blue', width=2)),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=time_hours, y=results['cumulative_outflow'], 
                  name='Cumulative Outflow', line=dict(color='green', width=2)),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text=f"Soakwell Performance Analysis: {scenario_name}",
        title_x=0.5,
        height=800,
        showlegend=True
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Time (hours)")
    fig.update_yaxes(title_text="Flow Rate (m³/s)", row=1, col=1)
    fig.update_yaxes(title_text="Volume (m³)", row=1, col=2)
    fig.update_yaxes(title_text="Water Level (m)", row=2, col=1)
    fig.update_yaxes(title_text="Cumulative Volume (m³)", row=2, col=2)
    
    return fig

def create_comparison_chart(all_results):
    """Create comparison chart for multiple scenarios"""
    
    # Prepare data for comparison
    scenarios = []
    efficiencies = []
    max_storages = []
    overflows = []
    
    for name, result in all_results.items():
        scenarios.append(name)
        total_inflow = result['cumulative_inflow'][-1]
        total_outflow = result['cumulative_outflow'][-1]
        efficiency = (total_outflow / total_inflow * 100) if total_inflow > 0 else 0
        efficiencies.append(efficiency)
        max_storages.append(max(result['stored_volume']))
        overflows.append(max(result['overflow_rate']))
    
    # Create comparison chart
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Storage Efficiency (%)', 'Maximum Storage (m³)', 'Peak Overflow (m³/s)'),
        specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
    )
    
    # Efficiency chart
    fig.add_trace(
        go.Bar(x=scenarios, y=efficiencies, name='Efficiency', 
               marker_color='lightblue', text=[f'{e:.1f}%' for e in efficiencies],
               textposition='auto'),
        row=1, col=1
    )
    
    # Storage chart
    fig.add_trace(
        go.Bar(x=scenarios, y=max_storages, name='Max Storage', 
               marker_color='lightgreen', text=[f'{s:.1f}' for s in max_storages],
               textposition='auto'),
        row=1, col=2
    )
    
    # Overflow chart
    fig.add_trace(
        go.Bar(x=scenarios, y=overflows, name='Peak Overflow', 
               marker_color='lightcoral', text=[f'{o:.4f}' for o in overflows],
               textposition='auto'),
        row=1, col=3
    )
    
    fig.update_layout(
        title_text="Scenario Comparison",
        title_x=0.5,
        height=400,
        showlegend=False
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig

def generate_configuration_report(config, hydrograph_data_dict, soil_conditions, ks, Sr):
    """
    Generate a comprehensive report for a specific soakwell configuration
    
    Parameters:
    config: Configuration dictionary from solve results
    hydrograph_data_dict: Dictionary of storm scenarios
    soil_conditions: Soil parameter dictionary
    ks, Sr: Soil parameters for simulation
    """
    
    # Create a new section for the report
    st.markdown("---")
    st.header(f"📊 Configuration Report: {config['configuration_name']}")
    
    # Report metadata
    st.subheader("📋 Report Summary")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        **Configuration Details:**
        - Diameter: {config['diameter']:.1f}m
        - Depth: {config['depth']:.1f}m  
        - Number of Units: {config['num_soakwells']}
        - Individual Volume: {config['individual_volume']:.2f} m³
        - Total System Volume: {config['total_volume']:.1f} m³
        """)
        
    with col2:
        st.markdown(f"""
        **Performance Summary:**
        - Standard Size: {'Yes' if config['standard_size'] else 'No'}
        - Total Cost: {'$' + f"{config['total_cost']:.0f}" + ' AUD' if config['total_cost'] else 'Custom Size'}
        - Worst Case Storm: {config['worst_case_storm']}
        - Max Water Level: {config['worst_case_level']:.2f}m
        """)
    
    # Soil conditions used
    st.subheader("🌍 Soil Conditions")
    soil_col1, soil_col2, soil_col3 = st.columns(3)
    with soil_col1:
        st.metric("Hydraulic Conductivity", f"{ks:.2e} m/s")
    with soil_col2:
        st.metric("Moderation Factor", f"{Sr:.1f}")
    with soil_col3:
        soil_type_desc = "Sandy" if ks >= 1e-4 else "Medium" if ks >= 1e-5 else "Clay"
        st.metric("Soil Classification", soil_type_desc)
    
    # Analysis methodology
    st.subheader("🔬 Analysis Methodology")
    st.markdown(f"""
    **Comprehensive Testing Approach:**
    
    This report presents the performance analysis of the {config['configuration_name']} soakwell configuration against all uploaded storm scenarios. The analysis methodology follows these steps:
    
    1. **Configuration Testing**: The selected configuration was tested against {len(hydrograph_data_dict)} storm scenario(s)
    2. **Flow Distribution**: For multiple soakwell systems, total catchment flow is equally distributed among all {config['num_soakwells']} units
    3. **Hydraulic Modeling**: Each soakwell is modeled as a cylindrical storage with variable outflow rate based on water level
    4. **Performance Criteria**: Configuration passes if no overflow occurs in any storm scenario
    5. **Worst Case Identification**: The storm producing the highest water level is identified as the design-critical scenario
    
    **Key Assumptions:**
    - Soakwells operate independently with equal flow distribution
    - Outflow rate is proportional to water level and soil permeability
    - No clogging or maintenance degradation over the storm duration
    - Fixed soil conditions throughout the analysis period
    """)
    
    # Storm scenario analysis
    st.subheader("🌧️ Storm Scenario Performance")
    
    # Create detailed analysis for each storm
    scenario_performance = []
    all_scenario_results = {}
    
    for filename, hydrograph_data in hydrograph_data_dict.items():
        # Run simulation for this specific configuration
        try:
            # Create scaled hydrograph for multiple soakwells
            if config['num_soakwells'] > 1:
                scaled_hydrograph = {
                    'time_min': hydrograph_data['time_min'],
                    'total_flow': [flow / config['num_soakwells'] for flow in hydrograph_data['total_flow']],
                    'cat1240_flow': hydrograph_data.get('cat1240_flow', [flow / config['num_soakwells'] for flow in hydrograph_data['total_flow']]),
                    'cat3_flow': hydrograph_data.get('cat3_flow', [0.0] * len(hydrograph_data['total_flow']))
                }
                
                # Simulate single soakwell
                single_result = simulate_soakwell_performance(
                    scaled_hydrograph, 
                    config['diameter'], 
                    ks, Sr, 
                    config['depth'],
                    extend_to_hours=24
                )
                
                # Scale back to represent all soakwells
                result = scale_multiple_soakwell_results(single_result, config['num_soakwells'], hydrograph_data)
            else:
                # Single soakwell analysis
                result = simulate_soakwell_performance(
                    hydrograph_data, 
                    config['diameter'], 
                    ks, Sr, 
                    config['depth'],
                    extend_to_hours=24
                )
            
            # Calculate performance metrics
            total_inflow = result['cumulative_inflow'][-1]
            total_outflow = result['cumulative_outflow'][-1]
            max_storage = max(result['stored_volume'])
            peak_overflow = max(result['overflow_rate'])
            max_water_level = max(result['water_level'])
            efficiency = (total_outflow / total_inflow * 100) if total_inflow > 0 else 0
            utilization = (max_storage / result['max_volume'] * 100) if result['max_volume'] > 0 else 0
            
            scenario_performance.append({
                'Storm Scenario': filename,
                'Duration (min)': f"{max(hydrograph_data['time_min']):.0f}",
                'Peak Inflow (m³/s)': f"{max(hydrograph_data['total_flow']):.4f}",
                'Total Inflow (m³)': f"{total_inflow:.1f}",
                'Max Water Level (m)': f"{max_water_level:.2f}",
                'Storage Efficiency (%)': f"{efficiency:.1f}",
                'Volume Utilization (%)': f"{utilization:.0f}",
                'Peak Overflow (m³/s)': f"{peak_overflow:.4f}",
                'Result': "✅ Pass" if peak_overflow == 0 else "❌ Overflow"
            })
            
            # Store result for plotting
            all_scenario_results[filename] = result
            
        except Exception as e:
            scenario_performance.append({
                'Storm Scenario': filename,
                'Duration (min)': 'Error',
                'Peak Inflow (m³/s)': 'Error', 
                'Total Inflow (m³)': 'Error',
                'Max Water Level (m)': 'Error',
                'Storage Efficiency (%)': 'Error',
                'Volume Utilization (%)': 'Error',
                'Peak Overflow (m³/s)': 'Error',
                'Result': f"❌ Error: {str(e)}"
            })
    
    # Display scenario performance table
    scenario_df = pd.DataFrame(scenario_performance)
    st.dataframe(scenario_df, use_container_width=True)
    
    # Performance plots for each scenario
    st.subheader("📈 Detailed Performance Analysis")
    
    for filename, result in all_scenario_results.items():
        with st.expander(f"📊 Detailed Analysis: {filename}", expanded=(filename == config['worst_case_storm'])):
            
            # Scenario-specific metrics
            perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
            
            total_inflow = result['cumulative_inflow'][-1]
            total_outflow = result['cumulative_outflow'][-1] 
            efficiency = (total_outflow / total_inflow * 100) if total_inflow > 0 else 0
            max_storage = max(result['stored_volume'])
            utilization = (max_storage / result['max_volume'] * 100) if result['max_volume'] > 0 else 0
            peak_overflow = max(result['overflow_rate'])
            
            with perf_col1:
                st.metric("Storage Efficiency", f"{efficiency:.1f}%")
            with perf_col2:
                st.metric("Max Storage", f"{max_storage:.1f} m³")
            with perf_col3:
                st.metric("Volume Utilization", f"{utilization:.0f}%")
            with perf_col4:
                overflow_status = "No Overflow" if peak_overflow == 0 else f"Overflow: {peak_overflow:.4f} m³/s"
                st.metric("Overflow Status", overflow_status)
            
            # Additional performance metrics row
            perf_col5, perf_col6, perf_col7, perf_col8 = st.columns(4)
            
            with perf_col5:
                emptying_time = result.get('emptying_time_minutes', None)
                if emptying_time is not None:
                    emptying_hours = emptying_time / 60
                    st.metric("Emptying Time", f"{emptying_hours:.1f} hrs")
                else:
                    st.metric("Emptying Time", "Still draining")
            
            with perf_col6:
                simulation_duration = result['time_hours'][-1]
                st.metric("Simulation Duration", f"{simulation_duration:.1f} hrs")
            
            with perf_col7:
                final_storage = result['stored_volume'][-1]
                st.metric("Final Storage", f"{final_storage:.2f} m³")
            
            with perf_col8:
                # Calculate drainage rate at end of simulation
                if len(result['outflow_rate']) > 1:
                    final_outflow = result['outflow_rate'][-1]
                    st.metric("Final Outflow", f"{final_outflow:.5f} m³/s")
                else:
                    st.metric("Final Outflow", "0 m³/s")
            
            # Generate performance plot
            scenario_name = f"{filename} - {config['configuration_name']}"
            fig = create_performance_plots(result, scenario_name)
            st.plotly_chart(fig, use_container_width=True)
    
    # Design recommendations
    st.subheader("💡 Design Recommendations")
    
    # Check if configuration passes all scenarios
    all_pass = all('Pass' in perf['Result'] for perf in scenario_performance if 'Error' not in perf['Result'])
    
    if all_pass:
        st.success("✅ **Configuration Approved**: This soakwell configuration successfully handles all tested storm scenarios without overflow.")
        
        st.markdown(f"""
        **Implementation Notes:**
        - Total system capacity: {config['total_volume']:.1f} m³
        - Individual soakwell specification: {config['diameter']:.1f}m diameter × {config['depth']:.1f}m deep
        - Installation requirement: {config['num_soakwells']} unit(s)
        """)
        
        if config['total_cost']:
            st.info(f"**Estimated Cost**: ${config['total_cost']:.0f} AUD (excluding installation, GST)")
        
    else:
        st.error("❌ **Configuration Not Suitable**: This configuration experiences overflow in one or more storm scenarios.")
        st.markdown("**Recommended Actions:**")
        st.markdown("- Increase soakwell size or quantity")
        st.markdown("- Improve soil conditions")
        st.markdown("- Consider supplementary drainage measures")
    
    # Technical specifications
    st.subheader("📐 Technical Specifications")
    
    if config['standard_size']:
        # Get manufacturer specs
        specs = get_standard_soakwell_specs(config['diameter'], config['depth'])
        
        spec_col1, spec_col2 = st.columns(2)
        with spec_col1:
            st.markdown(f"""
            **Individual Unit Specifications:**
            - Diameter: {config['diameter']:.1f}m
            - Depth: {config['depth']:.1f}m
            - Capacity: {specs['capacity_L']:.0f}L ({specs['capacity_m3']:.2f} m³)
            - Weight: {specs['weight_kg']}kg
            - Unit Price: ${specs['price_aud']:.0f} AUD
            """)
        
        with spec_col2:
            st.markdown(f"""
            **Total System Requirements:**
            - Number of Units: {config['num_soakwells']}
            - Total Capacity: {config['total_volume']:.1f} m³
            - Total Weight: {specs['weight_kg'] * config['num_soakwells']:.0f}kg
            - Total Cost: ${config['total_cost']:.0f} AUD (ex GST)
            """)
    else:
        st.warning("⚠️ **Non-Standard Size**: This configuration requires custom soakwell dimensions not available from standard manufacturers.")
    
    # Report footer
    st.markdown("---")
    st.markdown(f"""
    **Report Generated**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
    **Analysis Software**: Soakwell Design Dashboard v1.0  
    **Standards**: Based on manufacturer specifications and hydraulic modeling principles  
    """)

def main():
    """Main dashboard function"""
    
    # Title and description
    st.title("🌧️ Interactive Soakwell Design Dashboard")
    st.markdown("""
    This dashboard allows you to upload storm hydrograph files (.ts1) and analyze soakwell performance 
    with different design parameters. Adjust the parameters in real-time to see how they affect storage 
    efficiency and overflow characteristics.
    """)
    
    # Sidebar for file upload and parameters
    with st.sidebar:
        st.header("📁 File Upload")
        uploaded_files = st.file_uploader(
            "Upload .ts1 hydrograph files",
            type=['ts1'],
            accept_multiple_files=True,
            help="Upload one or more .ts1 files from DRAINS or similar software"
        )
        
        st.header("⚙️ Soakwell Parameters")
        
        # Soakwell geometry
        st.subheader("Geometry")
        diameter = st.selectbox(
            "Diameter (m)",
            [0.6, 0.9, 1.2, 1.5, 1.8],
            index=2,
            help="Standard concrete soakwell diameters available from manufacturers"
        )
        
        depth = st.selectbox(
            "Depth (m)",
            [0.6, 0.9, 1.2, 1.5, 1.8],
            index=2,
            help="Standard concrete soakwell depths available from manufacturers"
        )
        
        num_soakwells = st.number_input(
            "Number of Soakwells",
            min_value=1,
            max_value=30,
            value=1,
            step=1,
            help="Multiple smaller soakwells may be more effective than one large unit"
        )
        
        # Display manufacturer specifications
        specs = get_standard_soakwell_specs(diameter, depth)
        if specs['available']:
            st.info(f"""
            **Manufacturer Specifications:**
            - Capacity: {specs['capacity_L']:.0f} L ({specs['capacity_m3']:.2f} m³)
            - Weight: {specs['weight_kg']} kg
            - Price: ${specs['price_aud']:.0f} AUD (ex GST)
            """)
            if num_soakwells > 1:
                total_capacity = specs['capacity_m3'] * num_soakwells
                total_cost = specs['price_aud'] * num_soakwells
                st.info(f"""
                **Total System ({num_soakwells} units):**
                - Total Capacity: {total_capacity:.2f} m³
                - Total Cost: ${total_cost:.0f} AUD (ex GST)
                """)
        else:
            st.warning("⚠️ Non-standard size - not available from manufacturer")
        
        # Soil parameters
        st.subheader("Soil Properties")
        soil_type = st.selectbox(
            "Soil Type",
            ["Custom", "Sandy Soil", "Medium Soil", "Clay Soil"],
            index=2
        )
        
        # Hydraulic conductivity based on soil type
        if soil_type == "Sandy Soil":
            default_ks = 1e-4
        elif soil_type == "Medium Soil":
            default_ks = 1e-5
        elif soil_type == "Clay Soil":
            default_ks = 1e-6
        else:
            default_ks = 1e-5
        
        ks = st.number_input(
            "Hydraulic Conductivity (m/s)",
            min_value=1e-7,
            max_value=1e-3,
            value=default_ks,
            format="%.2e",
            help="Soil saturated hydraulic conductivity"
        )
        
        Sr = st.slider(
            "Soil Moderation Factor",
            0.5, 2.0, 1.0, 0.1,
            help="Factor to account for soil variability and clogging"
        )
        
        # Analysis options
        st.subheader("Analysis Options")
        show_individual = st.checkbox("Show individual scenario plots", True)
        show_comparison = st.checkbox("Show comparison chart", True)
        
        # French drain analysis toggle
        french_drain_params = {'enabled': False}
        if FRENCH_DRAIN_AVAILABLE:
            french_drain_params = add_french_drain_sidebar()
        elif uploaded_files:  # Only show warning if files are uploaded
            st.warning("⚠️ French drain analysis not available - module not found")
        
        # Solve functionality
        st.subheader("🔧 Comprehensive Design Solver")
        st.markdown("Test **all possible configurations** against **all storm scenarios**:")
        st.markdown("- All standard diameter/depth combinations")
        st.markdown("- 1-30 soakwells per configuration") 
        st.markdown("- Fixed soil conditions (set above)")
        
        solve_button = st.button(
            "🎯 Find All Viable Configurations",
            help="Test all possible soakwell configurations against all uploaded storm scenarios to find comprehensive design solutions"
        )
        
        # Clear results button if solve has been run
        if st.session_state.get('solve_results', None) is not None:
            clear_button = st.button(
                "🗑️ Clear Previous Results",
                help="Clear previous solve results to run a new analysis"
            )
            if clear_button:
                st.session_state.solve_results = None
                st.session_state.solve_hydrograph_data = None
                st.session_state.selected_config = None
                st.session_state.generate_report = False
                st.session_state.report_page = 0
        
        if solve_button:
            st.session_state.run_solve = True
        
        # Performance options for large datasets
        if uploaded_files and len(uploaded_files) > 5:
            max_plots = st.slider(
                "Max individual plots to show",
                min_value=1,
                max_value=min(10, len(uploaded_files)),
                value=5,
                help="Limit number of detailed plots for better performance"
            )
        else:
            max_plots = len(uploaded_files) if uploaded_files else 0
        
    # Main content area
    if uploaded_files:
        st.header("📊 Analysis Results")
        
        # Check if too many files
        if len(uploaded_files) > 10:
            st.warning(f"⚠️ You've uploaded {len(uploaded_files)} files. For performance, consider analyzing in smaller batches (≤10 files).")
            
            # Option to select subset
            st.subheader("📂 File Selection")
            file_names = [f.name for f in uploaded_files]
            selected_files = st.multiselect(
                "Select files to analyze (recommended: ≤10 at a time)",
                file_names,
                default=file_names[:5],  # Default to first 5 files
                help="Select fewer files for faster processing"
            )
            
            # Filter uploaded files based on selection
            uploaded_files = [f for f in uploaded_files if f.name in selected_files]
            
            if not uploaded_files:
                st.info("Please select at least one file to analyze.")
                return
        
        # Process uploaded files
        hydrograph_data_dict = {}
        file_summaries = []
        
        # Create a container for log messages
        log_messages = []
        
        for uploaded_file in uploaded_files:
            # Read file content
            try:
                content = uploaded_file.read().decode('utf-8')
                
                # Add file preview to log
                lines = content.split('\n')[:10]
                log_messages.append(f"🔍 Preview first 10 lines of {uploaded_file.name}:")
                for i, line in enumerate(lines):
                    log_messages.append(f"  {i+1:2d}: {line}")
                
                # Parse hydrograph data
                log_messages.append(f"📊 Analyzing file format for {uploaded_file.name}...")
                hydrograph_data = read_hydrograph_data_from_content(content)
                
                if len(hydrograph_data['time_min']) > 0:
                    log_messages.append(f"✅ Successfully parsed {len(hydrograph_data['time_min'])} data points from {uploaded_file.name}")
                    
                    hydrograph_data_dict[uploaded_file.name] = hydrograph_data
                    
                    # Calculate summary statistics
                    duration = max(hydrograph_data['time_min'])
                    peak_flow = max(hydrograph_data['total_flow'])
                    total_volume = sum([
                        flow * 60 for flow in hydrograph_data['total_flow']  # Approximate
                    ])
                    
                    file_summaries.append({
                        'File': uploaded_file.name,
                        'Duration (min)': f"{duration:.0f}",
                        'Peak Flow (m³/s)': f"{peak_flow:.4f}",
                        'Total Volume (m³)': f"{total_volume:.1f}",
                        'Data Points': len(hydrograph_data['time_min'])
                    })
                    
                    peak_flow = max(hydrograph_data['total_flow'])
                    log_messages.append(f"✅ {uploaded_file.name}: {len(hydrograph_data['time_min'])} data points, peak flow: {peak_flow:.4f} m³/s")
                else:
                    log_messages.append(f"⚠️ {uploaded_file.name}: No valid data found")
                    st.warning(f"⚠️ {uploaded_file.name}: No valid data found")
                    
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
        
        if hydrograph_data_dict:
            # Display file summary
            st.subheader("📋 Uploaded Files Summary")
            summary_df = pd.DataFrame(file_summaries)
            st.dataframe(summary_df, use_container_width=True)
            
            # Run analysis for each file
            all_results = {}
            
            # Add progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_files = len(hydrograph_data_dict)
            
            for idx, (filename, hydrograph_data) in enumerate(hydrograph_data_dict.items()):
                # Update progress
                progress = (idx + 1) / total_files
                progress_bar.progress(progress)
                status_text.text(f"Processing {filename} ({idx + 1}/{total_files})...")
                
                # Log detailed information
                log_messages.append(f"🔍 Analyzing {filename} with {len(hydrograph_data['time_min'])} data points...")
                
                # Create scenario name
                scenario_name = f"{filename} - {soil_type} ({num_soakwells}x {diameter:.1f}m ⌀ x {depth:.1f}m deep)"
                
                # Run simulation for multiple soakwells
                try:
                    log_messages.append(f"⚙️ Starting simulation for {filename}...")
                    
                    if num_soakwells == 1:
                        # Single soakwell analysis
                        log_messages.append(f"📊 Running single soakwell analysis...")
                        result = simulate_soakwell_performance(
                            hydrograph_data,
                            diameter=diameter,
                            ks=ks,
                            Sr=Sr,
                            max_height=depth,
                            extend_to_hours=24
                        )
                        log_messages.append(f"✅ Single soakwell analysis completed for {filename}")
                    else:
                        # Multiple soakwells - distribute the inflow
                        log_messages.append(f"📊 Running multiple soakwell analysis ({num_soakwells} units)...")
                        # Modify hydrograph data to split flow between soakwells
                        modified_hydrograph = {
                            'time_min': hydrograph_data['time_min'],
                            'total_flow': [flow / num_soakwells for flow in hydrograph_data['total_flow']]
                        }
                        
                        # Analyze single soakwell with reduced flow
                        single_result = simulate_soakwell_performance(
                            modified_hydrograph,
                            diameter=diameter,
                            ks=ks,
                            Sr=Sr,
                            max_height=depth,
                            extend_to_hours=24
                        )
                        
                        # Scale results back to represent all soakwells
                        result = scale_multiple_soakwell_results(single_result, num_soakwells, hydrograph_data)
                        log_messages.append(f"✅ Multiple soakwell analysis completed for {filename}")
                    
                    log_messages.append(f"📈 Calculating performance metrics for {filename}...")
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
                    
                    all_results[scenario_name] = result
                    
                except Exception as e:
                    error_msg = f"Error analyzing {filename}: {str(e)}"
                    log_messages.append(f"❌ {error_msg}")
                    st.error(error_msg)
                    continue
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            if not all_results:
                st.error("No files were successfully processed. Please check your file formats.")
                return
            
            # Display performance summary
            st.subheader("🎯 Performance Summary")
            
            performance_data = []
            for scenario_name, result in all_results.items():
                perf = result['performance']
                
                # Extract scenario details
                filename_part = scenario_name.split(' - ')[0]
                config_part = scenario_name.split(' - ')[1] if ' - ' in scenario_name else ""
                
                # Check if this is multiple soakwells
                if 'num_soakwells' in result and result['num_soakwells'] > 1:
                    config_display = f"{result['num_soakwells']}x {result['individual_diameter']:.1f}m"
                    total_volume = f"{result['max_volume']:.1f}"
                    individual_note = f" (each: {result['individual_max_volume']:.1f} m³)"
                else:
                    config_display = f"1x {result['diameter']:.1f}m"
                    total_volume = f"{result['max_volume']:.1f}"
                    individual_note = ""
                
                performance_data.append({
                    'Scenario': filename_part,
                    'Configuration': config_display,
                    'Storage Efficiency (%)': f"{perf['storage_efficiency']*100:.1f}",
                    'Total Capacity (m³)': total_volume + individual_note,
                    'Max Storage Used (m³)': f"{perf['max_storage_m3']:.1f}",
                    'Volume Utilization (%)': f"{perf['volume_utilization']*100:.0f}",
                    'Peak Overflow (m³/s)': f"{perf['peak_overflow_rate']:.4f}",
                    'Overflow?': "Yes" if perf['peak_overflow_rate'] > 0 else "No"
                })
            
            performance_df = pd.DataFrame(performance_data)
            st.dataframe(performance_df, use_container_width=True)
            
            # Individual scenario plots
            if show_individual:
                st.subheader("📈 Individual Scenario Analysis")
                
                # Limit number of plots for performance
                scenarios_to_plot = list(all_results.items())
                if 'max_plots' in locals() and len(scenarios_to_plot) > max_plots:
                    st.info(f"Showing first {max_plots} scenarios. Adjust the limit in Analysis Options to see more.")
                    scenarios_to_plot = scenarios_to_plot[:max_plots]
                
                for scenario_name, result in scenarios_to_plot:
                    with st.expander(f"📊 {scenario_name}", expanded=len(all_results) == 1):
                        
                        # Key metrics in columns
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric(
                                "Storage Efficiency",
                                f"{result['performance']['storage_efficiency']*100:.1f}%"
                            )
                        
                        with col2:
                            st.metric(
                                "Max Storage",
                                f"{result['performance']['max_storage_m3']:.1f} m³"
                            )
                        
                        with col3:
                            st.metric(
                                "Volume Utilization",
                                f"{result['performance']['volume_utilization']*100:.0f}%"
                            )
                        
                        with col4:
                            overflow_status = "Yes" if result['performance']['peak_overflow_rate'] > 0 else "No"
                            st.metric(
                                "Overflow",
                                overflow_status,
                                delta=f"{result['performance']['peak_overflow_rate']:.4f} m³/s"
                            )
                        
                        # Performance plot
                        fig = create_performance_plots(result, scenario_name)
                        st.plotly_chart(fig, use_container_width=True)
            
            # Comparison chart
            if show_comparison and len(all_results) > 1:
                st.subheader("⚖️ Scenario Comparison")
                comparison_fig = create_comparison_chart(all_results)
                st.plotly_chart(comparison_fig, use_container_width=True)
            
            # Design recommendations
            st.subheader("💡 Design Recommendations")
            
            # Find worst case scenario (highest water level)
            worst_case = max(all_results.values(), key=lambda x: max(x['water_level']))
            worst_case_name = [name for name, result in all_results.items() if result == worst_case][0]
            
            st.warning(f"**Worst Case Storm (Highest Water Level):** {worst_case_name}")
            st.write(f"- Maximum Water Level: {max(worst_case['water_level']):.2f}m")
            st.write(f"- Peak Overflow: {worst_case['performance']['peak_overflow_rate']:.4f} m³/s")
            st.write(f"- Storage Efficiency: {worst_case['performance']['storage_efficiency']*100:.1f}%")
            
            # Comprehensive Solve Analysis
            if st.session_state.get('run_solve', False) or st.session_state.get('solve_results', None) is not None:
                st.subheader("🎯 Comprehensive Solve Analysis - All Viable Configurations")
                
                # Run solve only if not already done
                if st.session_state.get('run_solve', False) and st.session_state.get('solve_results', None) is None:
                    st.info("Testing all possible soakwell configurations against all storm scenarios...")
                    
                    # Run comprehensive solve
                    solve_progress = st.progress(0)
                    solve_status = st.empty()
                    solve_status.text("Testing all diameter/depth/quantity combinations...")
                    
                    comprehensive_results = solve_for_minimum_soakwells(
                        hydrograph_data_dict,
                        ks=ks,
                        Sr=Sr,
                        max_soakwells=30
                    )
                    
                    # Store results in session state
                    st.session_state.solve_results = comprehensive_results
                    st.session_state.solve_hydrograph_data = hydrograph_data_dict
                    
                    solve_progress.progress(1.0)
                    solve_status.text("Analysis complete!")
                    
                    # Clear progress indicators
                    solve_progress.empty()
                    solve_status.empty()
                    
                    # Reset solve state
                    st.session_state.run_solve = False
                else:
                    # Use stored results
                    comprehensive_results = st.session_state.solve_results
                    hydrograph_data_dict = st.session_state.solve_hydrograph_data
                
                # Display summary statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Configurations Tested", comprehensive_results['total_configurations_tested'])
                with col2:
                    st.metric("Viable Solutions Found", comprehensive_results['viable_count'])
                with col3:
                    st.metric("Storm Scenarios Tested", len(comprehensive_results['storm_scenarios']))
                with col4:
                    success_rate = (comprehensive_results['viable_count'] / comprehensive_results['total_configurations_tested']) * 100
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                
                # Display soil conditions used
                st.info(f"**Fixed Soil Conditions:** Hydraulic Conductivity = {comprehensive_results['soil_conditions']['ks']:.2e} m/s, Moderation Factor = {comprehensive_results['soil_conditions']['Sr']}")
                
                if comprehensive_results['viable_configurations']:
                    # Show top recommendations
                    st.subheader("🏆 Top Recommendations")
                    
                    rec_col1, rec_col2, rec_col3 = st.columns(3)
                    
                    with rec_col1:
                        if comprehensive_results['recommendations']['minimum_cost']:
                            min_cost = comprehensive_results['recommendations']['minimum_cost']
                            st.success("💰 **Most Cost-Effective**")
                            st.write(f"Configuration: {min_cost['configuration_name']}")
                            st.write(f"Total Cost: ${min_cost['total_cost']:.0f} AUD")
                            st.write(f"Total Volume: {min_cost['total_volume']:.1f} m³")
                            st.write(f"Worst Case Level: {min_cost['worst_case_level']:.2f}m")
                    
                    with rec_col2:
                        if comprehensive_results['recommendations']['minimum_volume']:
                            min_vol = comprehensive_results['recommendations']['minimum_volume']
                            st.success("📏 **Smallest Total Volume**")
                            st.write(f"Configuration: {min_vol['configuration_name']}")
                            if min_vol['total_cost']:
                                st.write(f"Total Cost: ${min_vol['total_cost']:.0f} AUD")
                            st.write(f"Total Volume: {min_vol['total_volume']:.1f} m³")
                            st.write(f"Worst Case Level: {min_vol['worst_case_level']:.2f}m")
                    
                    with rec_col3:
                        if comprehensive_results['recommendations']['minimum_quantity']:
                            min_qty = comprehensive_results['recommendations']['minimum_quantity']
                            st.success("🔢 **Fewest Soakwells**")
                            st.write(f"Configuration: {min_qty['configuration_name']}")
                            if min_qty['total_cost']:
                                st.write(f"Total Cost: ${min_qty['total_cost']:.0f} AUD")
                            st.write(f"Total Volume: {min_qty['total_volume']:.1f} m³")
                            st.write(f"Worst Case Level: {min_qty['worst_case_level']:.2f}m")
                    
                    # Complete viable configurations table
                    st.subheader("📋 All Viable Configurations")
                    
                    viable_data = []
                    for config in comprehensive_results['viable_configurations']:
                        viable_data.append({
                            'Configuration': config['configuration_name'],
                            'Diameter (m)': config['diameter'],
                            'Depth (m)': config['depth'],
                            'Quantity': config['num_soakwells'],
                            'Total Volume (m³)': f"{config['total_volume']:.1f}",
                            'Individual Volume (m³)': f"{config['individual_volume']:.2f}",
                            'Total Cost (AUD)': f"${config['total_cost']:.0f}",
                            'Worst Case Storm': config['worst_case_storm'],
                            'Max Water Level (m)': f"{config['worst_case_level']:.2f}"
                        })
                    
                    viable_df = pd.DataFrame(viable_data)
                    st.dataframe(viable_df, use_container_width=True)
                    
                    # Add report generation buttons for each configuration
                    st.subheader("📋 Generate Configuration Reports")
                    st.markdown("Click any button below to generate a comprehensive report for that soakwell configuration:")
                    
                    # Sort configurations by quantity first, then by total volume
                    sorted_configs = sorted(comprehensive_results['viable_configurations'], 
                                          key=lambda x: (x['num_soakwells'], x['total_volume']))
                    
                    # Pagination setup
                    configs_per_page = 5
                    total_configs = len(sorted_configs)
                    total_pages = (total_configs + configs_per_page - 1) // configs_per_page
                    
                    if total_configs > configs_per_page:
                        # Initialize session state for pagination
                        if 'report_page' not in st.session_state:
                            st.session_state.report_page = 0
                        
                        # Pagination controls
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col1:
                            if st.button("◀ Previous", disabled=st.session_state.report_page == 0):
                                st.session_state.report_page -= 1
                        with col2:
                            st.write(f"Page {st.session_state.report_page + 1} of {total_pages}")
                        with col3:
                            if st.button("Next ▶", disabled=st.session_state.report_page >= total_pages - 1):
                                st.session_state.report_page += 1
                        
                        # Get configurations for current page
                        start_idx = st.session_state.report_page * configs_per_page
                        end_idx = min(start_idx + configs_per_page, total_configs)
                        page_configs = sorted_configs[start_idx:end_idx]
                    else:
                        page_configs = sorted_configs
                    
                    # Create report buttons for current page
                    for i, config in enumerate(page_configs):
                        button_text = f"📊 Report: {config['configuration_name']} (${config['total_cost']:.0f} AUD)"
                        button_key = f"report_btn_{config['diameter']}_{config['depth']}_{config['num_soakwells']}"
                        
                        if st.button(button_text, key=button_key):
                            # Store the config in session state for report generation
                            st.session_state.selected_config = config
                            st.session_state.generate_report = True
                            st.session_state.report_hydrograph_data = hydrograph_data_dict
                            st.session_state.report_soil_conditions = comprehensive_results['soil_conditions']
                            st.session_state.report_ks = ks
                            st.session_state.report_Sr = Sr
                    
                    # Generate report if one was requested
                    if st.session_state.get('generate_report', False):
                        generate_configuration_report(
                            st.session_state.selected_config, 
                            st.session_state.report_hydrograph_data, 
                            st.session_state.report_soil_conditions,
                            st.session_state.report_ks, 
                            st.session_state.report_Sr
                        )
                        # Clear the report flag but keep the report visible
                        st.session_state.generate_report = False
                    
                    # Configuration analysis
                    st.subheader("📊 Configuration Analysis")
                    
                    # Group by size and show minimum quantities needed
                    size_analysis = {}
                    for config in comprehensive_results['viable_configurations']:
                        size_key = f"{config['diameter']:.1f}m ⌀ x {config['depth']:.1f}m"
                        if size_key not in size_analysis:
                            size_analysis[size_key] = {
                                'min_quantity': config['num_soakwells'],
                                'individual_volume': config['individual_volume'],
                                'individual_cost': config['total_cost'] / config['num_soakwells'] if config['total_cost'] else None,
                                'standard_size': config['standard_size']
                            }
                        else:
                            size_analysis[size_key]['min_quantity'] = min(
                                size_analysis[size_key]['min_quantity'], 
                                config['num_soakwells']
                            )
                    
                    size_data = []
                    for size, analysis in size_analysis.items():
                        size_data.append({
                            'Soakwell Size': size,
                            'Minimum Quantity': analysis['min_quantity'],
                            'Individual Volume (m³)': f"{analysis['individual_volume']:.2f}",
                            'Individual Cost (AUD)': f"${analysis['individual_cost']:.0f}",
                            'Min Total Volume (m³)': f"{analysis['individual_volume'] * analysis['min_quantity']:.1f}",
                            'Min Total Cost (AUD)': f"${analysis['individual_cost'] * analysis['min_quantity']:.0f}"
                        })
                    
                    size_df = pd.DataFrame(size_data)
                    st.dataframe(size_df, use_container_width=True)
                    
                else:
                    st.error("❌ **No viable configurations found!**")
                    st.write("None of the tested configurations can handle all storm scenarios without overflow.")
                    st.write("**Recommendations:**")
                    st.write("- Consider improving soil conditions (higher hydraulic conductivity)")
                    st.write("- Reduce soil moderation factor (better installation/maintenance)")
                    st.write("- Consider non-standard larger soakwell sizes")
                    st.write("- Implement additional drainage measures")
                    
                    # Show configurations that came close
                    close_configs = sorted(comprehensive_results['all_configurations'], 
                                         key=lambda x: sum(1 for r in x['scenario_results'].values() if r['passes']))
                    
                    if close_configs:
                        st.subheader("🔍 Configurations That Handle Most Storms")
                        close_data = []
                        for config in close_configs[-5:]:  # Top 5 closest
                            scenarios_passed = sum(1 for r in config['scenario_results'].values() if r['passes'])
                            total_scenarios = len(config['scenario_results'])
                            close_data.append({
                                'Configuration': config['configuration_name'],
                                'Scenarios Passed': f"{scenarios_passed}/{total_scenarios}",
                                'Success Rate': f"{(scenarios_passed/total_scenarios)*100:.0f}%",
                                'Total Volume (m³)': f"{config['total_volume']:.1f}",
                                'Worst Case Level (m)': f"{config['worst_case_level']:.2f}"
                            })
                        
                        close_df = pd.DataFrame(close_data)
                        st.dataframe(close_df, use_container_width=True)
            
            # Check for no overflow scenarios
            no_overflow_scenarios = [name for name, result in all_results.items() 
                                   if result['performance']['peak_overflow_rate'] == 0]
            
            if no_overflow_scenarios:
                st.info(f"**Scenarios with No Overflow:** {', '.join([s.split(' - ')[0] for s in no_overflow_scenarios])}")
            else:
                st.warning("**All scenarios experience overflow.** Consider:")
                st.write("- Increasing soakwell diameter or height")
                st.write("- Using multiple soakwell units")
                st.write("- Improving soil conditions or drainage")
            
            # Parameter sensitivity note
            with st.expander("🔧 Parameter Sensitivity Guide"):
                st.markdown("""
                **Diameter:** Larger diameter increases storage volume (∝ d²) and infiltration area
                - Available: 600mm, 900mm, 1200mm, 1500mm, 1800mm
                
                **Height:** Directly increases storage volume but doesn't affect infiltration significantly
                - Available: 600mm, 900mm, 1200mm, 1500mm, 1800mm
                
                **Multiple Units:** Consider multiple smaller units vs single large unit:
                - Benefits: Better flow distribution, installation flexibility, cost optimization
                - Trade-offs: More excavation, higher complexity
                
                **Hydraulic Conductivity (ks):** 
                - Sandy soil: ~1×10⁻⁴ m/s (high infiltration)
                - Medium soil: ~1×10⁻⁵ m/s (moderate infiltration)  
                - Clay soil: ~1×10⁻⁶ m/s (low infiltration)
                
                **Soil Moderation Factor (Sr):** Accounts for clogging and soil variability (>1.0 reduces performance)
                
                **Manufacturer Data:** Prices and specifications from www.soakwells.com (Perth Soakwells)
                """)
            
            # French Drain Integration
            if FRENCH_DRAIN_AVAILABLE and french_drain_params['enabled']:
                st.markdown("---")
                
                # Prepare soil parameters for French drain analysis
                soil_params = {
                    'ks': ks,
                    'Sr': Sr,
                    'soil_type': soil_type
                }
                
                # Run French drain analysis with error handling for version compatibility
                try:
                    # Try new 3-argument version first
                    french_drain_results = integrate_french_drain_analysis(hydrograph_data_dict, soil_params, french_drain_params)
                except TypeError as e:
                    # Fall back to 2-argument version for backward compatibility
                    if "takes 2 positional arguments" in str(e):
                        st.warning("Using backward compatibility mode for French drain analysis...")
                        french_drain_results = integrate_french_drain_analysis(hydrograph_data_dict, soil_params)
                    else:
                        st.error(f"Error in French drain analysis: {str(e)}")
                        french_drain_results = None
                except Exception as e:
                    st.error(f"Unexpected error in French drain analysis: {str(e)}")
                    french_drain_results = None
                
                # If French drain analysis was run, offer comparison
                if french_drain_results:
                    st.subheader("⚖️ Soakwell vs French Drain Comparison")
                    
                    # Create comparison summary
                    comparison_data = []
                    for filename in hydrograph_data_dict.keys():
                        if filename in all_results and filename in french_drain_results:
                            
                            # Soakwell performance
                            sw_result = None
                            for name, result in all_results.items():
                                if filename in name:
                                    sw_result = result
                                    break
                            
                            if sw_result and french_drain_results[filename]:
                                sw_efficiency = sw_result['performance']['storage_efficiency'] * 100
                                fd_efficiency = french_drain_results[filename]['performance']['infiltration_efficiency_percent']
                                
                                sw_overflow = "Yes" if sw_result['performance']['peak_overflow_rate'] > 0 else "No"
                                fd_overflow = "Yes" if french_drain_results[filename]['performance']['total_overflow_m3'] > 0 else "No"
                                
                                comparison_data.append({
                                    'Storm Scenario': filename,
                                    'Soakwell Efficiency (%)': f"{sw_efficiency:.1f}",
                                    'French Drain Efficiency (%)': f"{fd_efficiency:.1f}",
                                    'Soakwell Overflow': sw_overflow,
                                    'French Drain Overflow': fd_overflow,
                                    'Better System': 'French Drain' if fd_efficiency > sw_efficiency else 'Soakwell' if sw_efficiency > fd_efficiency else 'Similar'
                                })
                    
                    if comparison_data:
                        comparison_df = pd.DataFrame(comparison_data)
                        st.dataframe(comparison_df, use_container_width=True)
                        
                        # Overall recommendation
                        fd_wins = sum(1 for row in comparison_data if row['Better System'] == 'French Drain')
                        sw_wins = sum(1 for row in comparison_data if row['Better System'] == 'Soakwell')
                        
                        if fd_wins > sw_wins:
                            st.success("🏆 **Overall Recommendation: French Drain System**")
                            st.markdown("French drain shows better performance across most storm scenarios.")
                        elif sw_wins > fd_wins:
                            st.success("🏆 **Overall Recommendation: Soakwell System**")
                            st.markdown("Soakwell system shows better performance across most storm scenarios.")
                        else:
                            st.info("⚖️ **Both systems show similar performance**")
                            st.markdown("Consider other factors like cost, installation complexity, and site constraints.")
                        
                        # Mass balance summary for both systems
                        st.markdown("---")
                        display_mass_balance_summary(sw_result, french_drain_results[list(french_drain_results.keys())[0]])
                        
                        # Report generation
                        if french_drain_params.get('generate_report', False):
                            st.markdown("---")
                            st.subheader("📊 Engineering Calculation Report")
                            
                            # Find worst-case storm (highest overflow or lowest efficiency)
                            worst_storm = None
                            worst_metric = -1
                            for filename in hydrograph_data_dict.keys():
                                if filename in french_drain_results and french_drain_results[filename]:
                                    # Use overflow volume as primary criterion
                                    overflow = french_drain_results[filename]['performance']['total_overflow_m3']
                                    if overflow > worst_metric:
                                        worst_metric = overflow
                                        worst_storm = filename
                            
                            if worst_storm:
                                # Get results for worst-case storm
                                worst_sw_result = None
                                for name, result in all_results.items():
                                    if worst_storm in name:
                                        worst_sw_result = result
                                        break
                                
                                worst_fd_result = french_drain_results[worst_storm]
                                
                                # Configuration details
                                config = {
                                    'soakwell_diameter': diameter,
                                    'soakwell_depth': depth,  
                                    'num_soakwells': num_soakwells,
                                    'ks': ks,
                                    'Sr': Sr,
                                    'french_drain_length': french_drain_params.get('system_length_m', 100)
                                }
                                
                                # Generate report
                                with st.spinner("Generating detailed calculation report..."):
                                    report_html = generate_calculation_report(
                                        worst_sw_result,
                                        worst_fd_result, 
                                        worst_storm,
                                        config
                                    )
                                
                                # Display report in expandable section
                                with st.expander("📋 Step-by-Step Calculation Report", expanded=True):
                                    st.markdown(report_html, unsafe_allow_html=True)
                                
                                # Download button for report
                                st.download_button(
                                    label="📥 Download Report as HTML",
                                    data=report_html,
                                    file_name=f"infiltration_analysis_report_{worst_storm}_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                                    mime="text/html",
                                    key="download_report"
                                )
                            else:
                                st.warning("Could not identify worst-case storm for report generation.")
            
            # Processing log (collapsed by default)
            if 'log_messages' in locals() and log_messages:
                with st.expander("🔍 Processing Log (click to view detailed analysis steps)", expanded=False):
                    for message in log_messages:
                        st.text(message)
    
    else:
        # Instructions when no files uploaded
        st.header("📤 Getting Started")
        st.markdown("""
        1. **Upload .ts1 files** using the sidebar file uploader
        2. **Adjust soakwell parameters** in the sidebar
        3. **View real-time results** as you change parameters
        4. **Compare multiple scenarios** to find optimal design
        
        ### File Format
        Upload .ts1 files generated from DRAINS or similar stormwater modeling software. 
        These files should contain time series flow data with:
        - Time column (minutes)
        - Flow rate columns (m³/s)
        """)
        
        # Example data preview
        with st.expander("📄 Example .ts1 File Format"):
            st.code("""
! File created from: Storm_Model.drn
! Storm event: 1% AEP_4.5 hour burst_Storm 1
! Timestep: 1 min
Time (min),Cat1240,Cat3
1.000,0.000,0.000
2.000,0.000,0.000
3.000,0.001,0.001
...
            """)

if __name__ == "__main__":
    main()
