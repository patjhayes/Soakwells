#!/usr/bin/env python3
"""
Soakwell Design Dashboard - Minimal Version for Streamlit Cloud
Streamlit-based dashboard for soakwell analysis with file upload
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import numpy as np

# Set page config
st.set_page_config(
    page_title="Soakwell Design Dashboard",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

def read_hydrograph_data_from_content(content):
    """Read hydrograph data from uploaded file content"""
    data = {
        'time_min': [],
        'cat1240_flow': [],
        'cat3_flow': [],
        'total_flow': []
    }
    
    lines = content.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    
    # Simple CSV parsing
    data_started = False
    for line in lines:
        if line.startswith('!') or 'Time' in line:
            continue
        
        if ',' in line:
            parts = line.split(',')
            try:
                time_val = float(parts[0])
                if len(parts) >= 3:
                    cat1 = float(parts[1])
                    cat2 = float(parts[2])
                elif len(parts) == 2:
                    cat1 = float(parts[1])
                    cat2 = 0.0
                else:
                    continue
                
                data['time_min'].append(time_val)
                data['cat1240_flow'].append(cat1)
                data['cat3_flow'].append(cat2)
                data['total_flow'].append(cat1 + cat2)
                
            except (ValueError, IndexError):
                continue
    
    return data

def simulate_soakwell_performance(hydrograph_data, diameter, ks=1e-5, Sr=1.0, max_height=None):
    """Simulate soakwell performance"""
    if max_height is None:
        max_height = diameter
    
    max_volume = math.pi * (diameter/2)**2 * max_height
    outflow_rate_base = ks * (math.pi * (diameter/2)**2 + math.pi * diameter * max_height) / Sr
    
    time_min = hydrograph_data['time_min']
    inflow_rates = hydrograph_data['total_flow']
    
    # Initialize arrays
    stored_volume = [0.0]
    outflow_rate = [0.0]
    overflow = [0.0]
    
    for i in range(1, len(time_min)):
        dt = (time_min[i] - time_min[i-1]) * 60  # Convert to seconds
        current_volume = stored_volume[i-1]
        
        # Calculate outflow based on current volume
        level_factor = min(current_volume / max_volume, 1.0) if max_volume > 0 else 0
        current_outflow_rate = outflow_rate_base * level_factor
        outflow_rate.append(current_outflow_rate)
        
        # Water balance
        volume_in = inflow_rates[i] * dt
        volume_out = current_outflow_rate * dt
        new_volume = current_volume + volume_in - volume_out
        
        # Check for overflow
        if new_volume > max_volume:
            overflow_vol = new_volume - max_volume
            overflow.append(overflow_vol / dt)
            new_volume = max_volume
        else:
            overflow.append(0.0)
        
        stored_volume.append(max(0.0, new_volume))
    
    return {
        'time_min': time_min,
        'time_hours': [t/60 for t in time_min],
        'inflow_rate': inflow_rates,
        'stored_volume': stored_volume,
        'outflow_rate': outflow_rate,
        'overflow_rate': overflow,
        'max_volume': max_volume,
        'diameter': diameter
    }

def create_performance_plots(results, scenario_name):
    """Create performance plots"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Flow Rates', 'Storage Volume', 'Water Level', 'Cumulative Analysis'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    time_hours = results['time_hours']
    
    # Plot 1: Flow rates
    fig.add_trace(
        go.Scatter(x=time_hours, y=results['inflow_rate'], 
                  name='Inflow', line=dict(color='blue', width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=time_hours, y=results['outflow_rate'], 
                  name='Outflow', line=dict(color='green', width=2)),
        row=1, col=1
    )
    
    # Plot 2: Storage volume
    fig.add_trace(
        go.Scatter(x=time_hours, y=results['stored_volume'], 
                  name='Storage', line=dict(color='purple', width=2)),
        row=1, col=2
    )
    
    # Add max capacity line
    fig.add_hline(y=results['max_volume'], line_dash="dash", line_color="red", 
                  annotation_text="Max Capacity", row=1, col=2)
    
    # Plot 3: Water level
    water_level = [vol / (math.pi * (results['diameter']/2)**2) for vol in results['stored_volume']]
    fig.add_trace(
        go.Scatter(x=time_hours, y=water_level, 
                  name='Water Level', line=dict(color='orange', width=2)),
        row=2, col=1
    )
    
    # Plot 4: Overflow
    fig.add_trace(
        go.Scatter(x=time_hours, y=results['overflow_rate'], 
                  name='Overflow', line=dict(color='red', width=2)),
        row=2, col=2
    )
    
    fig.update_layout(
        title_text=f"Soakwell Performance: {scenario_name}",
        height=800,
        showlegend=True
    )
    
    return fig

def main():
    """Main dashboard function"""
    
    st.title("🌧️ Soakwell Design Dashboard")
    st.markdown("Upload storm hydrograph files and analyze soakwell performance")
    
    # Sidebar parameters
    with st.sidebar:
        st.header("📁 File Upload")
        uploaded_files = st.file_uploader(
            "Upload .ts1 hydrograph files",
            type=['ts1', 'csv'],
            accept_multiple_files=True
        )
        
        st.header("⚙️ Soakwell Parameters")
        
        diameter = st.selectbox(
            "Diameter (m)",
            [0.6, 0.9, 1.2, 1.5, 1.8],
            index=2
        )
        
        depth = st.selectbox(
            "Depth (m)",
            [0.6, 0.9, 1.2, 1.5, 1.8],
            index=2
        )
        
        # Soil parameters
        st.subheader("Soil Properties")
        soil_type = st.selectbox(
            "Soil Type",
            ["Sandy Soil", "Medium Soil", "Clay Soil"],
            index=1
        )
        
        if soil_type == "Sandy Soil":
            ks = 1e-4
        elif soil_type == "Medium Soil":
            ks = 1e-5
        else:
            ks = 1e-6
        
        # Display specs
        specs = get_standard_soakwell_specs(diameter, depth)
        if specs['available']:
            st.info(f"""
            **Specifications:**
            - Capacity: {specs['capacity_L']:.0f} L
            - Weight: {specs['weight_kg']} kg
            - Price: ${specs['price_aud']:.0f} AUD
            """)
    
    # Main content
    if uploaded_files:
        st.header("📊 Analysis Results")
        
        hydrograph_data_dict = {}
        
        for uploaded_file in uploaded_files:
            try:
                content = uploaded_file.read().decode('utf-8')
                hydrograph_data = read_hydrograph_data_from_content(content)
                
                if len(hydrograph_data['time_min']) > 0:
                    hydrograph_data_dict[uploaded_file.name] = hydrograph_data
                    
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        
        if hydrograph_data_dict:
            # Display file summary
            st.subheader("📋 Uploaded Files Summary")
            file_summaries = []
            
            for filename, data in hydrograph_data_dict.items():
                duration = max(data['time_min'])
                peak_flow = max(data['total_flow'])
                
                file_summaries.append({
                    'File': filename,
                    'Duration (min)': f"{duration:.0f}",
                    'Peak Flow (m³/s)': f"{peak_flow:.4f}",
                    'Data Points': len(data['time_min'])
                })
            
            summary_df = pd.DataFrame(file_summaries)
            st.dataframe(summary_df, use_container_width=True)
            
            # Run analysis
            st.subheader("🎯 Performance Analysis")
            
            for filename, hydrograph_data in hydrograph_data_dict.items():
                with st.expander(f"📊 Analysis: {filename}"):
                    
                    # Run simulation
                    results = simulate_soakwell_performance(
                        hydrograph_data,
                        diameter=diameter,
                        ks=ks,
                        max_height=depth
                    )
                    
                    # Display metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        max_storage = max(results['stored_volume'])
                        st.metric("Peak Storage", f"{max_storage:.1f} m³")
                    
                    with col2:
                        max_overflow = max(results['overflow_rate'])
                        st.metric("Peak Overflow", f"{max_overflow:.4f} m³/s")
                    
                    with col3:
                        utilization = (max_storage / results['max_volume'] * 100) if results['max_volume'] > 0 else 0
                        st.metric("Storage Utilization", f"{utilization:.0f}%")
                    
                    with col4:
                        overflow_status = "No Overflow" if max_overflow == 0 else "Overflow!"
                        st.metric("Status", overflow_status)
                    
                    # Create and display plot
                    fig = create_performance_plots(results, filename)
                    st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("👆 Upload .ts1 files to start analysis")
        
        # Show example
        st.subheader("📄 Sample File Format")
        st.code("""
Time (min),Cat1240,Cat3
0.000,0.000,0.000
1.000,0.001,0.001
2.000,0.002,0.001
...
        """)

if __name__ == "__main__":
    main()
