"""
Engineering Report Generator for Soakwell and French Drain Analysis
Generates step-by-step calculation reports for worst-case storm scenarios
"""

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def generate_calculation_report(soakwell_results, french_drain_results, storm_name, config):
    """
    Generate a comprehensive engineering calculation report
    
    Parameters:
    soakwell_results: Results from soakwell simulation
    french_drain_results: Results from French drain simulation  
    storm_name: Name of the analyzed storm
    config: Configuration parameters used
    
    Returns:
    str: HTML report content
    """
    
    # Report header
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_report = f"""
    <style>
    .report-container {{
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
    }}
    .report-header {{
        text-align: center;
        border-bottom: 3px solid #2E86AB;
        padding-bottom: 20px;
        margin-bottom: 30px;
    }}
    .section-header {{
        background-color: #2E86AB;
        color: white;
        padding: 10px 15px;
        margin: 20px 0 10px 0;
        border-radius: 5px;
        font-weight: bold;
    }}
    .calculation-box {{
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }}
    .result-box {{
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }}
    .warning-box {{
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }}
    .parameter-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
    }}
    .parameter-table th, .parameter-table td {{
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }}
    .parameter-table th {{
        background-color: #f2f2f2;
        font-weight: bold;
    }}
    </style>
    
    <div class="report-container">
        <div class="report-header">
            <h1>INFILTRATION SYSTEM ANALYSIS REPORT</h1>
            <h2>Soakwell vs French Drain Performance</h2>
            <p><strong>Storm Event:</strong> {storm_name}</p>
            <p><strong>Report Generated:</strong> {report_date}</p>
            <p><strong>Project:</strong> North Fremantle Pedestrian Infrastructure</p>
        </div>
    """
    
    # Storm characteristics
    if soakwell_results:
        total_volume = soakwell_results['mass_balance']['total_inflow_m3']
        peak_inflow = max(soakwell_results['inflow_rate'])
        duration_hours = max(soakwell_results['time_min']) / 60
    elif french_drain_results:
        total_volume = french_drain_results['performance']['total_inflow_m3']
        peak_inflow = max(french_drain_results['inflow'])
        duration_hours = max(french_drain_results['time']) / 3600
    else:
        total_volume = peak_inflow = duration_hours = 0
        
    html_report += f"""
        <div class="section-header">1. STORM EVENT CHARACTERISTICS</div>
        <div class="calculation-box">
            <table class="parameter-table">
                <tr><th>Parameter</th><th>Value</th><th>Unit</th></tr>
                <tr><td>Storm Duration</td><td>{duration_hours:.1f}</td><td>hours</td></tr>
                <tr><td>Peak Inflow Rate</td><td>{peak_inflow*1000:.1f}</td><td>L/s</td></tr>
                <tr><td>Total Runoff Volume</td><td>{total_volume:.1f}</td><td>m³</td></tr>
                <tr><td>Average Intensity</td><td>{total_volume/(duration_hours*3600)*1000:.1f}</td><td>L/s</td></tr>
            </table>
        </div>
    """
    
    # Soakwell Analysis
    if soakwell_results:
        diameter = config.get('soakwell_diameter', 2.0)
        ks = config.get('ks', 1e-5)
        
        # Soakwell geometry calculations
        radius = diameter / 2
        area = np.pi * radius**2
        max_volume = soakwell_results['max_volume']
        max_height = max_volume / area
        
        # Performance metrics
        max_stored = max(soakwell_results['stored_volume'])
        max_level = max(soakwell_results['water_level'])
        total_overflow = soakwell_results['mass_balance']['total_overflow_m3']
        infiltration_efficiency = ((total_volume - total_overflow) / total_volume * 100) if total_volume > 0 else 0
        
        html_report += f"""
            <div class="section-header">2. SOAKWELL ANALYSIS</div>
            
            <div class="calculation-box">
                <h4>2.1 Geometry Calculations</h4>
                <p><strong>Given:</strong></p>
                <ul>
                    <li>Diameter (D) = {diameter:.1f} m</li>
                    <li>Soil permeability (Ks) = {ks:.1e} m/s</li>
                </ul>
                
                <p><strong>Calculations:</strong></p>
                <ul>
                    <li>Radius (r) = D/2 = {diameter:.1f}/2 = {radius:.1f} m</li>
                    <li>Base Area (A) = π × r² = π × {radius:.1f}² = {area:.2f} m²</li>
                    <li>Maximum Height = {max_height:.2f} m</li>
                    <li>Maximum Volume = A × H = {area:.2f} × {max_height:.2f} = {max_volume:.1f} m³</li>
                </ul>
            </div>
            
            <div class="calculation-box">
                <h4>2.2 Infiltration Rate Calculation</h4>
                <p><strong>Using Darcy's Law (cylindrical flow):</strong></p>
                <p>Q = 2π × Ks × L × (h/ln(R/r))</p>
                <p>Where:</p>
                <ul>
                    <li>Ks = {ks:.1e} m/s (soil permeability)</li>
                    <li>L = depth of water (variable)</li>
                    <li>R/r ratio ≈ 10 (assumed)</li>
                </ul>
                <p>Maximum infiltration rate ≈ {max(soakwell_results['outflow_rate'])*1000:.1f} L/s</p>
            </div>
            
            <div class="result-box">
                <h4>2.3 Soakwell Performance Results</h4>
                <table class="parameter-table">
                    <tr><th>Performance Metric</th><th>Value</th><th>Unit</th></tr>
                    <tr><td>Maximum Storage Used</td><td>{max_stored:.1f}</td><td>m³</td></tr>
                    <tr><td>Maximum Water Level</td><td>{max_level:.2f}</td><td>m</td></tr>
                    <tr><td>Storage Utilization</td><td>{max_stored/max_volume*100:.1f}</td><td>%</td></tr>
                    <tr><td>Total Overflow</td><td>{total_overflow:.1f}</td><td>m³</td></tr>
                    <tr><td>Infiltration Efficiency</td><td>{infiltration_efficiency:.1f}</td><td>%</td></tr>
                    <tr><td>Mass Balance Error</td><td>{soakwell_results['mass_balance']['mass_balance_error_percent']:.2f}</td><td>%</td></tr>
                </table>
            </div>
        """
        
        if total_overflow > 0.1:
            html_report += f"""
                <div class="warning-box">
                    <h4>⚠️ Soakwell Overflow Warning</h4>
                    <p>The soakwell overflows {total_overflow:.1f} m³ during this storm event. 
                    Consider increasing the diameter or depth, or use multiple soakwells.</p>
                </div>
            """
    
    # French Drain Analysis  
    if french_drain_results:
        pipe_diameter = 0.30  # m
        trench_width = 0.60  # m
        trench_depth = 0.90  # m
        length = config.get('french_drain_length', 100.0)
        soil_k = 4.63e-5  # m/s
        
        # Performance metrics
        max_storage = french_drain_results['performance']['max_trench_storage_m3']
        max_water_level = french_drain_results['performance']['max_water_level_m']
        total_infiltrated = french_drain_results['performance']['total_infiltrated_m3']
        total_overflow = french_drain_results['performance']['total_overflow_m3']
        pipe_capacity = french_drain_results['performance'].get('pipe_capacity_m3s', 0.08)
        
        html_report += f"""
            <div class="section-header">3. FRENCH DRAIN ANALYSIS</div>
            
            <div class="calculation-box">
                <h4>3.1 System Geometry</h4>
                <table class="parameter-table">
                    <tr><th>Component</th><th>Dimension</th><th>Unit</th></tr>
                    <tr><td>Pipe Diameter</td><td>{pipe_diameter*1000:.0f}</td><td>mm</td></tr>
                    <tr><td>Trench Width</td><td>{trench_width*1000:.0f}</td><td>mm</td></tr>
                    <tr><td>Trench Depth</td><td>{trench_depth*1000:.0f}</td><td>mm</td></tr>
                    <tr><td>System Length</td><td>{length:.0f}</td><td>m</td></tr>
                    <tr><td>Soil Permeability</td><td>{soil_k:.1e}</td><td>m/s</td></tr>
                </table>
            </div>
            
            <div class="calculation-box">
                <h4>3.2 Capacity Calculations</h4>
                <p><strong>Pipe Flow Capacity (Manning's Equation):</strong></p>
                <p>Q = (1/n) × A × R^(2/3) × S^(1/2)</p>
                <ul>
                    <li>Pipe area = π × ({pipe_diameter:.2f}/2)² = {np.pi*(pipe_diameter/2)**2:.4f} m²</li>
                    <li>Manning's n = 0.013 (concrete pipe)</li>
                    <li>Slope = 0.005 (0.5%)</li>
                    <li>Pipe capacity ≈ {pipe_capacity*1000:.0f} L/s</li>
                </ul>
                
                <p><strong>Trench Storage Capacity:</strong></p>
                <ul>
                    <li>Trench volume = {trench_width:.1f} × {trench_depth:.1f} × {length:.0f} = {trench_width*trench_depth*length:.0f} m³</li>
                    <li>Aggregate porosity = 35%</li>
                    <li>Effective storage = {trench_width*trench_depth*length*0.35:.0f} m³</li>
                </ul>
                
                <p><strong>Infiltration Rate (Darcy's Law):</strong></p>
                <ul>
                    <li>Base area = {trench_width:.1f} × {length:.0f} = {trench_width*length:.0f} m²</li>
                    <li>Max infiltration ≈ {soil_k:.1e} × {trench_width*length:.0f} = {soil_k*trench_width*length*1000:.1f} L/s</li>
                </ul>
            </div>
            
            <div class="result-box">
                <h4>3.3 French Drain Performance Results</h4>
                <table class="parameter-table">
                    <tr><th>Performance Metric</th><th>Value</th><th>Unit</th></tr>
                    <tr><td>Maximum Storage Used</td><td>{max_storage:.1f}</td><td>m³</td></tr>
                    <tr><td>Maximum Water Level</td><td>{max_water_level*1000:.0f}</td><td>mm</td></tr>
                    <tr><td>Peak Pipe Utilization</td><td>{max(french_drain_results['pipe_flow'])/pipe_capacity*100:.1f}</td><td>%</td></tr>
                    <tr><td>Total Infiltrated</td><td>{total_infiltrated:.1f}</td><td>m³</td></tr>
                    <tr><td>Total Overflow</td><td>{total_overflow:.1f}</td><td>m³</td></tr>
                    <tr><td>Infiltration Efficiency</td><td>{french_drain_results['performance']['infiltration_efficiency_percent']:.1f}</td><td>%</td></tr>
                    <tr><td>Mass Balance Error</td><td>{french_drain_results['performance']['mass_balance_error_percent']:.2f}</td><td>%</td></tr>
                </table>
            </div>
        """
        
        if total_overflow > 0.1:
            html_report += f"""
                <div class="warning-box">
                    <h4>⚠️ French Drain Overflow Warning</h4>
                    <p>The French drain system overflows {total_overflow:.1f} m³ during this storm event. 
                    Consider increasing the length, trench size, or pipe capacity.</p>
                </div>
            """
    
    # Comparison section
    if soakwell_results and french_drain_results:
        sw_efficiency = ((total_volume - soakwell_results['mass_balance']['total_overflow_m3']) / total_volume * 100)
        fd_efficiency = french_drain_results['performance']['infiltration_efficiency_percent']
        
        html_report += f"""
            <div class="section-header">4. COMPARATIVE ANALYSIS</div>
            
            <div class="calculation-box">
                <h4>4.1 Performance Comparison</h4>
                <table class="parameter-table">
                    <tr><th>Metric</th><th>Soakwell</th><th>French Drain</th><th>Better Option</th></tr>
                    <tr><td>Infiltration Efficiency</td><td>{sw_efficiency:.1f}%</td><td>{fd_efficiency:.1f}%</td><td>{'Soakwell' if sw_efficiency > fd_efficiency else 'French Drain'}</td></tr>
                    <tr><td>Total Overflow</td><td>{soakwell_results['mass_balance']['total_overflow_m3']:.1f} m³</td><td>{total_overflow:.1f} m³</td><td>{'Soakwell' if soakwell_results['mass_balance']['total_overflow_m3'] < total_overflow else 'French Drain'}</td></tr>
                    <tr><td>Max Storage Used</td><td>{max(soakwell_results['stored_volume']):.1f} m³</td><td>{max_storage:.1f} m³</td><td>{'Soakwell' if max(soakwell_results['stored_volume']) < max_storage else 'French Drain'}</td></tr>
                    <tr><td>Mass Balance Error</td><td>{soakwell_results['mass_balance']['mass_balance_error_percent']:.2f}%</td><td>{french_drain_results['performance']['mass_balance_error_percent']:.2f}%</td><td>{'Soakwell' if abs(soakwell_results['mass_balance']['mass_balance_error_percent']) < abs(french_drain_results['performance']['mass_balance_error_percent']) else 'French Drain'}</td></tr>
                </table>
            </div>
            
            <div class="result-box">
                <h4>4.2 Engineering Recommendations</h4>
        """
        
        if sw_efficiency > fd_efficiency and soakwell_results['mass_balance']['total_overflow_m3'] < total_overflow:
            html_report += "<p><strong>Recommendation:</strong> Soakwell system provides better overall performance for this storm event.</p>"
        elif fd_efficiency > sw_efficiency and total_overflow < soakwell_results['mass_balance']['total_overflow_m3']:
            html_report += "<p><strong>Recommendation:</strong> French drain system provides better overall performance for this storm event.</p>"
        else:
            html_report += "<p><strong>Recommendation:</strong> Both systems show similar performance. Consider other factors like cost, maintenance, and site constraints.</p>"
            
        html_report += """
                <p><strong>Additional Considerations:</strong></p>
                <ul>
                    <li>Soakwells require less linear space but more depth</li>
                    <li>French drains provide linear infiltration along their length</li>
                    <li>Maintenance requirements differ between systems</li>
                    <li>Local soil conditions may favor one approach</li>
                </ul>
            </div>
        """
    
    html_report += f"""
        <div class="section-header">5. TECHNICAL NOTES</div>
        <div class="calculation-box">
            <h4>5.1 Mass Balance Verification</h4>
            <p>Mass balance errors should be close to 0% for accurate simulations:</p>
            <ul>
    """
    
    if soakwell_results:
        mb_error = soakwell_results['mass_balance']['mass_balance_error_percent']
        status = "✅ Acceptable" if abs(mb_error) < 1.0 else "⚠️ Review Required"
        html_report += f"<li>Soakwell mass balance error: {mb_error:.2f}% - {status}</li>"
        
    if french_drain_results:
        mb_error = french_drain_results['performance']['mass_balance_error_percent']
        status = "✅ Acceptable" if abs(mb_error) < 1.0 else "⚠️ Review Required"
        html_report += f"<li>French drain mass balance error: {mb_error:.2f}% - {status}</li>"
    
    html_report += f"""
            </ul>
            
            <h4>5.2 Model Assumptions</h4>
            <ul>
                <li>Soil permeability is uniform and constant</li>
                <li>Water table is deep (no groundwater interference)</li>
                <li>No clogging or reduction in permeability over time</li>
                <li>Steady-state infiltration rates</li>
                <li>Perfect hydraulic connections</li>
            </ul>
            
            <h4>5.3 Design Standards</h4>
            <ul>
                <li>Australian Standard AS/NZS 3500.3 for drainage systems</li>
                <li>Local council requirements for stormwater management</li>
                <li>Factor of safety should be applied to final design</li>
            </ul>
        </div>
        
        <div class="section-header">Report Generated by Soakwell Analysis Tool</div>
        <p style="text-align: center; color: #666; font-size: 0.9em;">
            This report is for preliminary design purposes only. 
            Detailed site investigation and professional engineering review required for final design.
        </p>
    </div>
    """
    
    return html_report

def add_report_button_to_sidebar():
    """Add report generation button to sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Engineering Report")
    
    if st.sidebar.button("Generate Calculation Report", key="generate_report_btn"):
        return True
    else:
        return False

def display_mass_balance_summary(soakwell_results=None, french_drain_results=None):
    """Display mass balance summary in the main interface"""
    st.subheader("🔍 Mass Balance Verification")
    
    col1, col2 = st.columns(2)
    
    if soakwell_results and 'mass_balance' in soakwell_results:
        with col1:
            st.markdown("**Soakwell Mass Balance**")
            mb = soakwell_results['mass_balance']
            
            df_sw = pd.DataFrame({
                'Component': ['Total Inflow', 'Total Outflow', 'Total Overflow', 'Final Stored', 'Balance Error'],
                'Volume (m³)': [
                    mb['total_inflow_m3'],
                    mb['total_outflow_m3'], 
                    mb['total_overflow_m3'],
                    mb['final_stored_m3'],
                    mb['mass_balance_error_m3']
                ],
                'Percentage': [
                    100.0,
                    mb['total_outflow_m3']/mb['total_inflow_m3']*100,
                    mb['total_overflow_m3']/mb['total_inflow_m3']*100,
                    mb['final_stored_m3']/mb['total_inflow_m3']*100,
                    mb['mass_balance_error_percent']
                ]
            })
            
            st.dataframe(df_sw, use_container_width=True)
            
            if abs(mb['mass_balance_error_percent']) < 1.0:
                st.success(f"✅ Mass balance error: {mb['mass_balance_error_percent']:.2f}%")
            else:
                st.warning(f"⚠️ Mass balance error: {mb['mass_balance_error_percent']:.2f}%")
    
    if french_drain_results and 'performance' in french_drain_results:
        with col2:
            st.markdown("**French Drain Mass Balance**")
            perf = french_drain_results['performance']
            
            df_fd = pd.DataFrame({
                'Component': ['Total Inflow', 'Total Infiltrated', 'Total Overflow', 'Final Stored', 'Balance Error'],
                'Volume (m³)': [
                    perf['total_inflow_m3'],
                    perf['total_infiltrated_m3'],
                    perf['total_overflow_m3'], 
                    perf['final_stored_m3'],
                    perf['mass_balance_error_m3']
                ],
                'Percentage': [
                    100.0,
                    perf['total_infiltrated_m3']/perf['total_inflow_m3']*100,
                    perf['total_overflow_m3']/perf['total_inflow_m3']*100,
                    perf['final_stored_m3']/perf['total_inflow_m3']*100,
                    perf['mass_balance_error_percent']
                ]
            })
            
            st.dataframe(df_fd, use_container_width=True)
            
            if abs(perf['mass_balance_error_percent']) < 1.0:
                st.success(f"✅ Mass balance error: {perf['mass_balance_error_percent']:.2f}%")
            else:
                st.warning(f"⚠️ Mass balance error: {perf['mass_balance_error_percent']:.2f}%")
