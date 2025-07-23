#!/usr/bin/env python3
"""
French Drain Integration for Soakwell Dashboard
Adds French drain modeling capabilities to the existing soakwell analysis dashboard
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

# Import French drain model with error handling
try:
    from french_drain_model import FrenchDrainModel
    FRENCH_DRAIN_MODEL_AVAILABLE = True
except ImportError as e:
    FRENCH_DRAIN_MODEL_AVAILABLE = False
    # Don't show error at import time - will handle gracefully in UI
except Exception as e:
    FRENCH_DRAIN_MODEL_AVAILABLE = False
    # Don't show error at import time - will handle gracefully in UI

def add_french_drain_sidebar():
    """Add French drain parameters to sidebar"""
    
    # Check if French drain model is available
    if not FRENCH_DRAIN_MODEL_AVAILABLE:
        return {'enabled': False, 'error': 'French drain model not available'}
    
    st.sidebar.markdown("---")
    st.sidebar.header("🚰 French Drain Analysis")
    
    enable_french_drain = st.sidebar.checkbox(
        "Enable French Drain Analysis",
        help="Compare with French drain infiltration system"
    )
    
    if enable_french_drain:
        st.sidebar.subheader("French Drain Parameters")
        
        # Pipe specifications
        pipe_diameter = st.sidebar.selectbox(
            "Pipe Diameter (mm)",
            [225, 300, 375, 450],
            index=1,
            help="Standard concrete pipe diameters"
        )
        
        pipe_slope = st.sidebar.slider(
            "Pipe Slope (%)",
            0.3, 2.0, 0.5, 0.1,
            help="Longitudinal gradient of pipe"
        ) / 100  # Convert to decimal
        
        # Trench geometry
        st.sidebar.subheader("Trench Geometry")
        
        trench_width = st.sidebar.number_input(
            "Trench Width (mm)",
            400, 1000, 600, 50,
            help="Width of excavated trench"
        )
        
        trench_depth = st.sidebar.number_input(
            "Trench Depth (mm)",
            600, 1500, 900, 50,
            help="Depth of excavated trench"
        )
        
        # System length
        system_length = st.sidebar.number_input(
            "French Drain Length (m)",
            10, 500, 100, 10,
            help="Total length of French drain system"
        )
        
        # Soil parameters (use same as soakwell)
        st.sidebar.info("📍 Using soil parameters from soakwell analysis above")
        
        return {
            'enabled': True,
            'pipe_diameter_mm': pipe_diameter,
            'pipe_diameter_m': pipe_diameter / 1000,
            'pipe_slope': pipe_slope,
            'trench_width_mm': trench_width,
            'trench_width_m': trench_width / 1000,
            'trench_depth_mm': trench_depth,
            'trench_depth_m': trench_depth / 1000,
            'system_length_m': system_length
        }
    
    return {'enabled': False}

def run_french_drain_analysis(hydrograph_data_dict, soil_params, french_drain_params):
    """
    Run French drain analysis for all uploaded scenarios
    
    Parameters:
    hydrograph_data_dict: Dictionary of storm scenarios
    soil_params: Soil parameters from soakwell analysis
    french_drain_params: French drain configuration
    
    Returns:
    dict: French drain analysis results
    """
    
    results = {}
    
    # Create custom French drain model with specified parameters
    drain = FrenchDrainModel()
    
    # Update model parameters
    drain.pipe_diameter = french_drain_params['pipe_diameter_m']
    drain.pipe_radius = drain.pipe_diameter / 2
    drain.pipe_area = math.pi * drain.pipe_radius**2
    
    drain.trench_width = french_drain_params['trench_width_m']
    drain.trench_depth = french_drain_params['trench_depth_m']
    drain.trench_area = drain.trench_width * drain.trench_depth
    
    # Use soil parameters from soakwell analysis
    drain.soil_k = soil_params['ks']
    
    # Recalculate effective storage volume
    drain.effective_storage_volume = drain.trench_area * drain.aggregate_porosity
    
    for filename, hydrograph_data in hydrograph_data_dict.items():
        
        # Convert soakwell hydrograph to French drain format
        drain_hydrograph = {
            'time': np.array([t * 60 for t in hydrograph_data['time_min']]),  # Convert to seconds
            'flow': np.array(hydrograph_data['total_flow'])
        }
        
        # Run French drain simulation
        try:
            result = drain.simulate_french_drain_response(
                drain_hydrograph,
                pipe_slope=french_drain_params['pipe_slope'],
                length=french_drain_params['system_length_m']
            )
            
            results[filename] = result
            
        except Exception as e:
            st.error(f"Error analyzing {filename} with French drain: {str(e)}")
            results[filename] = None
    
    return results

def create_french_drain_comparison_plots(soakwell_results, french_drain_results, scenario_name):
    """
    Create comparison plots between soakwell and French drain performance
    """
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Flow Comparison', 'Storage Comparison', 
                       'Efficiency Comparison', 'Cost Analysis'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Extract time data (use soakwell time as reference)
    time_hours = soakwell_results['time_hours']
    
    # Convert French drain time to hours for comparison
    fd_time_hours = french_drain_results['time_hours']
    
    # Plot 1: Flow comparison
    fig.add_trace(
        go.Scatter(x=time_hours, y=soakwell_results['inflow_rate'], 
                  name='Inflow', line=dict(color='blue', width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=time_hours, y=soakwell_results['outflow_rate'], 
                  name='Soakwell Outflow', line=dict(color='green', width=2, dash='solid')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=fd_time_hours, y=french_drain_results['infiltration_outflow'], 
                  name='French Drain Infiltration', line=dict(color='orange', width=2, dash='dash')),
        row=1, col=1
    )
    
    # Plot 2: Storage comparison
    # Soakwell storage
    fig.add_trace(
        go.Scatter(x=time_hours, y=soakwell_results['stored_volume'], 
                  name='Soakwell Storage', line=dict(color='purple', width=2)),
        row=1, col=2
    )
    
    # French drain storage
    fig.add_trace(
        go.Scatter(x=fd_time_hours, y=french_drain_results['trench_volume'], 
                  name='French Drain Storage', line=dict(color='brown', width=2, dash='dash')),
        row=1, col=2
    )
    
    # Plot 3: Efficiency metrics (bar chart)
    systems = ['Soakwell', 'French Drain']
    
    # Calculate efficiencies
    soakwell_efficiency = (soakwell_results['cumulative_outflow'][-1] / 
                          soakwell_results['cumulative_inflow'][-1] * 100) if soakwell_results['cumulative_inflow'][-1] > 0 else 0
    
    french_drain_efficiency = french_drain_results['performance']['infiltration_efficiency_percent']
    
    efficiencies = [soakwell_efficiency, french_drain_efficiency]
    
    fig.add_trace(
        go.Bar(x=systems, y=efficiencies, 
               name='Infiltration Efficiency (%)',
               marker_color=['green', 'orange'],
               text=[f'{e:.1f}%' for e in efficiencies],
               textposition='auto'),
        row=2, col=1
    )
    
    # Plot 4: Storage capacity comparison
    soakwell_max_storage = max(soakwell_results['stored_volume'])
    french_drain_max_storage = max(french_drain_results['trench_volume'])
    
    max_storages = [soakwell_max_storage, french_drain_max_storage]
    
    fig.add_trace(
        go.Bar(x=systems, y=max_storages, 
               name='Max Storage (m³)',
               marker_color=['purple', 'brown'],
               text=[f'{s:.1f} m³' for s in max_storages],
               textposition='auto'),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text=f"System Comparison: {scenario_name}",
        title_x=0.5,
        height=800,
        showlegend=True
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Time (hours)", row=1, col=1)
    fig.update_xaxes(title_text="Time (hours)", row=1, col=2)
    fig.update_yaxes(title_text="Flow Rate (m³/s)", row=1, col=1)
    fig.update_yaxes(title_text="Storage Volume (m³)", row=1, col=2)
    fig.update_yaxes(title_text="Efficiency (%)", row=2, col=1)
    fig.update_yaxes(title_text="Storage (m³)", row=2, col=2)
    
    return fig

def display_french_drain_results(french_drain_results, french_drain_params):
    """
    Display French drain results in the dashboard
    """
    
    st.header("🚰 French Drain Analysis Results")
    
    # System configuration summary
    st.subheader("🔧 System Configuration")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Pipe Diameter", f"{french_drain_params['pipe_diameter_mm']:.0f} mm")
        st.metric("Trench Width", f"{french_drain_params['trench_width_mm']:.0f} mm")
    
    with col2:
        st.metric("Pipe Slope", f"{french_drain_params['pipe_slope']*100:.1f} %")
        st.metric("Trench Depth", f"{french_drain_params['trench_depth_mm']:.0f} mm")
    
    with col3:
        st.metric("System Length", f"{french_drain_params['system_length_m']:.0f} m")
        
        # Calculate storage capacity
        drain = FrenchDrainModel()
        drain.trench_width = french_drain_params['trench_width_m']
        drain.trench_depth = french_drain_params['trench_depth_m']
        storage_capacity = (drain.trench_width * drain.trench_depth * 
                           drain.aggregate_porosity * french_drain_params['system_length_m'])
        st.metric("Storage Capacity", f"{storage_capacity:.1f} m³")
    
    # Performance summary table
    st.subheader("📊 Performance Summary")
    
    performance_data = []
    for scenario_name, result in french_drain_results.items():
        if result is not None:
            perf = result['performance']
            performance_data.append({
                'Scenario': scenario_name,
                'Infiltration Efficiency (%)': f"{perf['infiltration_efficiency_percent']:.1f}",
                'Total Infiltrated (m³)': f"{perf['total_infiltrated_m3']:.1f}",
                'Max Storage (m³)': f"{perf['max_trench_storage_m3']:.1f}",
                'Overflow Volume (m³)': f"{perf['total_overflow_m3']:.1f}",
                'Max Water Level (m)': f"{perf['max_water_level_m']:.2f}"
            })
    
    if performance_data:
        performance_df = pd.DataFrame(performance_data)
        st.dataframe(performance_df, use_container_width=True)
        
        # Individual scenario analysis
        st.subheader("📈 Detailed Scenario Analysis")
        
        for scenario_name, result in french_drain_results.items():
            if result is not None:
                with st.expander(f"📊 {scenario_name} - French Drain Performance"):
                    
                    # Key metrics
                    perf = result['performance']
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Infiltration Efficiency", f"{perf['infiltration_efficiency_percent']:.1f}%")
                    with col2:
                        st.metric("Peak Storage", f"{perf['max_trench_storage_m3']:.1f} m³")
                    with col3:
                        storage_utilization = (perf['max_trench_storage_m3'] / storage_capacity * 100) if storage_capacity > 0 else 0
                        st.metric("Storage Utilization", f"{storage_utilization:.0f}%")
                    with col4:
                        overflow_status = "No Overflow" if perf['total_overflow_m3'] == 0 else f"{perf['total_overflow_m3']:.1f} m³"
                        st.metric("Overflow", overflow_status)
                    
                    # Performance plot
                    fig = create_french_drain_performance_plot(result, scenario_name)
                    st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.warning("No French drain results available. Check for errors in the analysis.")

def create_french_drain_performance_plot(result, scenario_name):
    """Create performance plot for French drain"""
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Flow Analysis', 'Storage Volume', 
                       'Water Level', 'Cumulative Volumes'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    time_hours = result['time_hours']
    
    # Plot 1: Flow rates
    fig.add_trace(
        go.Scatter(x=time_hours, y=result['inflow'], 
                  name='Inflow', line=dict(color='blue', width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=time_hours, y=result['pipe_flow'], 
                  name='Pipe Flow', line=dict(color='green', width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=time_hours, y=result['infiltration_outflow'], 
                  name='Infiltration', line=dict(color='orange', width=2)),
        row=1, col=1
    )
    
    if max(result['pipe_overflow']) > 0:
        fig.add_trace(
            go.Scatter(x=time_hours, y=result['pipe_overflow'], 
                      name='Overflow', line=dict(color='red', width=2)),
            row=1, col=1
        )
    
    # Plot 2: Storage volume
    fig.add_trace(
        go.Scatter(x=time_hours, y=result['trench_volume'], 
                  name='Stored Volume', line=dict(color='purple', width=2)),
        row=1, col=2
    )
    
    # Plot 3: Water level
    fig.add_trace(
        go.Scatter(x=time_hours, y=result['trench_water_level'], 
                  name='Water Level', line=dict(color='brown', width=2)),
        row=2, col=1
    )
    
    # Plot 4: Cumulative volumes
    cumulative_inflow = np.cumsum(result['inflow']) * np.gradient(result['time'])
    cumulative_infiltration = np.cumsum(result['infiltration_outflow']) * np.gradient(result['time'])
    
    fig.add_trace(
        go.Scatter(x=time_hours, y=cumulative_inflow, 
                  name='Cumulative Inflow', line=dict(color='blue', width=2)),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=time_hours, y=cumulative_infiltration, 
                  name='Cumulative Infiltration', line=dict(color='green', width=2)),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text=f"French Drain Performance: {scenario_name}",
        title_x=0.5,
        height=700,
        showlegend=True
    )
    
    # Update axes
    fig.update_xaxes(title_text="Time (hours)")
    fig.update_yaxes(title_text="Flow Rate (m³/s)", row=1, col=1)
    fig.update_yaxes(title_text="Volume (m³)", row=1, col=2)
    fig.update_yaxes(title_text="Water Level (m)", row=2, col=1)
    fig.update_yaxes(title_text="Cumulative Volume (m³)", row=2, col=2)
    
    return fig

def generate_comparison_report(soakwell_results, french_drain_results, soil_params, config_params):
    """
    Generate comprehensive comparison report between soakwell and French drain systems
    """
    
    st.markdown("---")
    st.header("📋 System Comparison Report")
    
    # Cost comparison (simplified)
    st.subheader("💰 Cost Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Soakwell System:**")
        # Estimate soakwell costs (from existing code)
        # This would use the configuration from the main dashboard
        st.markdown("- Material costs from manufacturer specs")
        st.markdown("- Excavation requirements")
        st.markdown("- Installation complexity")
    
    with col2:
        st.markdown("**French Drain System:**")
        length = config_params['system_length_m']
        
        # Cost estimation for French drain
        pipe_cost_per_m = 50  # AUD per meter for 300mm concrete pipe
        excavation_cost_per_m = 80  # AUD per meter (depends on depth/width)
        aggregate_cost_per_m = 30  # AUD per meter for gravel bedding
        installation_cost_per_m = 40  # AUD per meter for installation
        
        total_cost_per_m = pipe_cost_per_m + excavation_cost_per_m + aggregate_cost_per_m + installation_cost_per_m
        total_system_cost = total_cost_per_m * length
        
        st.metric("Cost per meter", f"${total_cost_per_m:.0f} AUD")
        st.metric("Total system cost", f"${total_system_cost:.0f} AUD")
        st.markdown(f"- Pipe: ${pipe_cost_per_m}/m")
        st.markdown(f"- Excavation: ${excavation_cost_per_m}/m") 
        st.markdown(f"- Aggregate: ${aggregate_cost_per_m}/m")
        st.markdown(f"- Installation: ${installation_cost_per_m}/m")
    
    # Performance comparison summary
    st.subheader("⚡ Performance Summary")
    
    # Create comparison table for key metrics
    comparison_data = []
    
    for scenario_name in soakwell_results.keys():
        if scenario_name in french_drain_results and french_drain_results[scenario_name] is not None:
            
            # Soakwell metrics
            sw_result = soakwell_results[scenario_name]
            sw_efficiency = (sw_result['cumulative_outflow'][-1] / sw_result['cumulative_inflow'][-1] * 100) if sw_result['cumulative_inflow'][-1] > 0 else 0
            sw_max_storage = max(sw_result['stored_volume'])
            sw_overflow = max(sw_result['overflow_rate'])
            
            # French drain metrics
            fd_result = french_drain_results[scenario_name]
            fd_efficiency = fd_result['performance']['infiltration_efficiency_percent']
            fd_max_storage = fd_result['performance']['max_trench_storage_m3']
            fd_overflow = fd_result['performance']['total_overflow_m3']
            
            comparison_data.append({
                'Scenario': scenario_name,
                'Soakwell Efficiency (%)': f"{sw_efficiency:.1f}",
                'French Drain Efficiency (%)': f"{fd_efficiency:.1f}",
                'Soakwell Max Storage (m³)': f"{sw_max_storage:.1f}",
                'French Drain Max Storage (m³)': f"{fd_max_storage:.1f}",
                'Soakwell Overflow': "Yes" if sw_overflow > 0 else "No",
                'French Drain Overflow': "Yes" if fd_overflow > 0 else "No"
            })
    
    if comparison_data:
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Recommendations
        st.subheader("💡 Design Recommendations")
        
        avg_sw_efficiency = np.mean([float(row['Soakwell Efficiency (%)']) for row in comparison_data])
        avg_fd_efficiency = np.mean([float(row['French Drain Efficiency (%)']) for row in comparison_data])
        
        if avg_fd_efficiency > avg_sw_efficiency + 5:  # 5% threshold
            st.success("🏆 **French Drain Recommended**: Higher average infiltration efficiency across scenarios")
            st.markdown("**Advantages:**")
            st.markdown("- Better handling of peak flows")
            st.markdown("- Continuous infiltration along length")
            st.markdown("- Lower maintenance requirements")
            
        elif avg_sw_efficiency > avg_fd_efficiency + 5:
            st.success("🏆 **Soakwell System Recommended**: Higher average infiltration efficiency")
            st.markdown("**Advantages:**")
            st.markdown("- Concentrated infiltration")
            st.markdown("- Standard sizing available")
            st.markdown("- Predictable performance")
            
        else:
            st.info("⚖️ **Similar Performance**: Both systems show comparable efficiency")
            st.markdown("**Consider:**")
            st.markdown("- Site constraints and available space")
            st.markdown("- Installation complexity")
            st.markdown("- Long-term maintenance requirements")
            st.markdown("- Total system cost")
    
    else:
        st.warning("Unable to generate comparison - insufficient data from both systems")

# Function to be called from main dashboard
def integrate_french_drain_analysis(hydrograph_data_dict, soil_params):
    """
    Main integration function to be called from the soakwell dashboard
    """
    
    # Add French drain sidebar controls
    french_drain_params = add_french_drain_sidebar()
    
    if french_drain_params['enabled']:
        
        # Run French drain analysis
        st.info("🔄 Running French drain analysis...")
        french_drain_results = run_french_drain_analysis(
            hydrograph_data_dict, 
            soil_params, 
            french_drain_params
        )
        
        if french_drain_results:
            # Display results
            display_french_drain_results(french_drain_results, french_drain_params)
            
            return french_drain_results
        else:
            st.error("French drain analysis failed")
            return None
    
    return None
