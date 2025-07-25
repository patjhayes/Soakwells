#!/usr/bin/env python3
"""
Core Soakwell Analysis Functions
Standalone analysis functions without UI dependencies
"""

import pandas as pd
import math

def get_standard_soakwell_specs(diameter, depth):
    """
    Get manufacturer specifications for standard concrete soakwells
    Based on Perth Soakwells specifications from www.soakwells.com
    
    Returns:
    dict: Manufacturer specifications including capacity and weight
    """
    # Convert to mm for lookup
    diameter_mm = int(diameter * 1000)
    depth_mm = int(depth * 1000)
    
    # Standard Perth Soakwells pricing and specifications (2024)
    specs = {
        'available': False,
        'diameter_mm': diameter_mm,
        'depth_mm': depth_mm,
        'diameter_m': diameter,
        'depth_m': depth,
        'capacity_m3': math.pi * (diameter/2)**2 * depth,
        'weight_kg': 0,
        'price_aud': 0,
        'product_code': f"Custom_{diameter_mm}x{depth_mm}"
    }
    
    # Standard sizes and pricing
    standard_sizes = {
        (900, 900): {'weight': 330, 'price': 286, 'code': 'SW0909'},
        (900, 1200): {'weight': 430, 'price': 374, 'code': 'SW0912'},
        (900, 1500): {'weight': 530, 'price': 462, 'code': 'SW0915'},
        (900, 1800): {'weight': 630, 'price': 550, 'code': 'SW0918'},
        (1200, 900): {'weight': 460, 'price': 341, 'code': 'SW1209'},
        (1200, 1200): {'weight': 620, 'price': 451, 'code': 'SW1212'},
        (1200, 1500): {'weight': 780, 'price': 561, 'code': 'SW1215'},
        (1200, 1800): {'weight': 940, 'price': 671, 'code': 'SW1218'},
        (1500, 900): {'weight': 650, 'price': 424, 'code': 'SW1509'},
        (1500, 1200): {'weight': 870, 'price': 566, 'code': 'SW1512'},
        (1500, 1500): {'weight': 1090, 'price': 708, 'code': 'SW1515'},
        (1500, 1800): {'weight': 1310, 'price': 850, 'code': 'SW1518'},
        (1800, 900): {'weight': 920, 'price': 529, 'code': 'SW1809'},
        (1800, 1200): {'weight': 1230, 'price': 708, 'code': 'SW1812'},
        (1800, 1500): {'weight': 1540, 'price': 887, 'code': 'SW1815'},
        (1800, 1800): {'weight': 1850, 'price': 1066, 'code': 'SW1818'},
        (2100, 900): {'weight': 1250, 'price': 660, 'code': 'SW2109'},
        (2100, 1200): {'weight': 1670, 'price': 880, 'code': 'SW2112'},
        (2100, 1500): {'weight': 2090, 'price': 1100, 'code': 'SW2115'},
        (2100, 1800): {'weight': 2510, 'price': 1320, 'code': 'SW2118'},
        (2400, 900): {'weight': 1650, 'price': 825, 'code': 'SW2409'},
        (2400, 1200): {'weight': 2200, 'price': 1100, 'code': 'SW2412'},
        (2400, 1500): {'weight': 2750, 'price': 1375, 'code': 'SW2415'},
        (2400, 1800): {'weight': 3300, 'price': 1650, 'code': 'SW2418'},
    }
    
    # Check if this is a standard size
    size_key = (diameter_mm, depth_mm)
    if size_key in standard_sizes:
        std_spec = standard_sizes[size_key]
        specs.update({
            'available': True,
            'weight_kg': std_spec['weight'],
            'price_aud': std_spec['price'],
            'product_code': std_spec['code']
        })
    
    return specs

def read_hydrograph_data_from_content(content):
    """
    Parse hydrograph data from TS1 file content without streamlit dependencies
    .ts1 format: First 8 lines are metadata, 9th line is header, then CSV data (time, flow_m3/s)
    """
    data = {
        'time_min': [],
        'cat1240_flow': [],
        'cat3_flow': [],
        'total_flow': []
    }
    
    lines = content.strip().split('\n')
    
    if len(lines) < 10:  # Need at least 8 metadata + 1 header + 1 data line
        return data
    
    # .ts1 format: 9th line (index 8) is the header
    header_line = lines[8].strip() if len(lines) > 8 else ""
    column_headers = [col.strip() for col in header_line.split(',')]
    
    # Data starts from line 10 (index 9)
    data_start_line = 9
    
    # Parse the actual data - simple two-column format: time(min), flow(m³/s)
    for i in range(data_start_line, len(lines)):
        line = lines[i].strip()
        if not line or line.startswith('#') or line.startswith('!'):
            continue
        
        parts = line.split(',')
        if len(parts) < 2:
            continue
            
        try:
            time_min = float(parts[0])
            flow_m3s = float(parts[1])  # Flow already in m³/s
            
            # For .ts1 files, we typically have single catchment data
            # Store in total_flow and cat3_flow for compatibility
            data['time_min'].append(time_min)
            data['cat1240_flow'].append(0.0)  # Not used in .ts1 format
            data['cat3_flow'].append(flow_m3s)
            data['total_flow'].append(flow_m3s)
            
        except (ValueError, IndexError):
            continue
    
    return data

def calculate_soakwell_outflow_rate(diameter, ks=1e-5, Sr=1.0):
    """Calculate steady-state outflow rate from soakwell"""
    height = diameter
    base_area = math.pi * (diameter/2)**2
    wall_area = math.pi * diameter * height
    total_area = base_area + wall_area
    outflow_rate = ks * total_area / Sr
    return outflow_rate

def simulate_soakwell_performance(hydrograph_data, diameter, ks=1e-5, Sr=1.0, max_height=None, extend_to_hours=24):
    """
    Simulate soakwell performance over time using hydrograph data
    Standalone version without streamlit cache decorators
    """
    if max_height is None:
        max_height = diameter
    
    max_volume = math.pi * (diameter/2)**2 * max_height
    
    # Initialize arrays
    time_min = list(hydrograph_data['time_min'])  # Create copy
    inflow_rates = list(hydrograph_data['total_flow'])  # m³/s
    
    # Extend simulation time to ensure complete emptying analysis
    extend_to_min = extend_to_hours * 60
    original_length = len(time_min)
    
    # Find the last time point with significant inflow
    inflow_end_time = max(time_min) if time_min else 0
    for i in range(len(inflow_rates)-1, -1, -1):
        if inflow_rates[i] > 0.001:  # 1 L/s threshold
            inflow_end_time = time_min[i]
            break
    
    # Extend time series if needed for emptying analysis
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
            # Outflow rate scales with wetted area (simplified approach)
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
            overflow.append(overflow_vol / dt)  # Convert back to rate
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
    
    # Calculate emptying time (time from peak to 5% of peak)
    emptying_time = 0
    if stored_volume:
        peak_volume = max(stored_volume)
        peak_idx = stored_volume.index(peak_volume)
        threshold = 0.05 * peak_volume
        
        for i in range(peak_idx, len(stored_volume)):
            if stored_volume[i] <= threshold:
                emptying_time = time_min[i] - time_min[peak_idx]
                break
        
        # If never reaches threshold, use the time to nearly empty
        if emptying_time == 0 and stored_volume[-1] < 0.1 * peak_volume:
            emptying_time = time_min[-1] - time_min[peak_idx]
    
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
    Scale single soakwell results to represent multiple soakwells
    Standalone version without streamlit dependencies
    """
    # Create a copy of the result
    scaled_result = dict(single_result)
    
    # Scale volume-related results by number of soakwells
    volume_keys = ['stored_volume', 'cumulative_inflow', 'cumulative_outflow', 'max_volume']
    for key in volume_keys:
        if key in scaled_result:
            if key == 'max_volume':
                scaled_result[key] = single_result[key] * num_soakwells
            else:
                scaled_result[key] = [v * num_soakwells for v in single_result[key]]
    
    # Scale flow rates by number of soakwells (restore to original system flow)
    flow_keys = ['inflow_rate', 'outflow_rate', 'overflow_rate']
    for key in flow_keys:
        if key in scaled_result:
            scaled_result[key] = [v * num_soakwells for v in single_result[key]]
    
    # Water level stays the same (per individual soakwell)
    # Time arrays stay the same
    
    # Add metadata
    scaled_result['num_soakwells'] = num_soakwells
    scaled_result['individual_max_volume'] = single_result['max_volume']
    scaled_result['system_type'] = 'multiple_soakwells'
    
    return scaled_result
