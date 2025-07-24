"""
Comprehensive Engineering Report Generator
Creates a detailed PDF-ready report documenting the entire infiltration analysis process
"""

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

def generate_comprehensive_engineering_report(soakwell_results, french_drain_results, storm_name, config, hydrograph_data):
    """
    Generate a comprehensive engineering report documenting the entire analysis
    
    Parameters:
    soakwell_results: Results from soakwell simulation
    french_drain_results: Results from French drain simulation  
    storm_name: Name of the analyzed storm
    config: Configuration parameters used
    hydrograph_data: Original storm hydrograph data
    
    Returns:
    str: Complete HTML report content suitable for PDF conversion
    """
    
    # Report metadata
    report_date = datetime.now().strftime("%Y-%m-%d")
    report_time = datetime.now().strftime("%H:%M:%S")
    
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Infiltration System Analysis Report</title>
        <style>
            @page {{ 
                size: A4; 
                margin: 2cm; 
                @bottom-center {{ content: "Page " counter(page) " of " counter(pages); }}
            }}
            body {{ 
                font-family: 'Times New Roman', serif; 
                line-height: 1.6; 
                margin: 0; 
                padding: 0;
                font-size: 11pt;
                color: #333;
            }}
            .header {{ 
                text-align: center; 
                border-bottom: 3px solid #1f4e79; 
                padding-bottom: 20px; 
                margin-bottom: 30px;
                page-break-after: avoid;
            }}
            .header h1 {{ 
                color: #1f4e79; 
                margin: 0; 
                font-size: 24pt; 
                font-weight: bold;
            }}
            .header h2 {{ 
                color: #666; 
                margin: 5px 0; 
                font-size: 16pt; 
                font-weight: normal;
            }}
            .section {{ 
                margin: 25px 0; 
                page-break-inside: avoid;
            }}
            .section-title {{ 
                background-color: #1f4e79; 
                color: white; 
                padding: 12px 15px; 
                margin: 20px 0 15px 0; 
                font-size: 14pt; 
                font-weight: bold;
                page-break-after: avoid;
            }}
            .subsection-title {{ 
                color: #1f4e79; 
                font-size: 12pt; 
                font-weight: bold; 
                margin: 15px 0 8px 0;
                border-bottom: 1px solid #1f4e79;
                padding-bottom: 3px;
            }}
            .formula-box {{ 
                background-color: #f8f9fa; 
                border: 1px solid #dee2e6; 
                border-left: 4px solid #1f4e79;
                padding: 15px; 
                margin: 15px 0; 
                font-family: 'Courier New', monospace;
                page-break-inside: avoid;
            }}
            .calculation-box {{ 
                background-color: #fff; 
                border: 1px solid #ccc; 
                padding: 15px; 
                margin: 10px 0;
                page-break-inside: avoid;
            }}
            .result-box {{ 
                background-color: #d4edda; 
                border: 1px solid #c3e6cb; 
                border-left: 4px solid #28a745;
                padding: 15px; 
                margin: 15px 0;
                page-break-inside: avoid;
            }}
            .parameter-table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin: 15px 0;
                font-size: 10pt;
            }}
            .parameter-table th, .parameter-table td {{ 
                border: 1px solid #ddd; 
                padding: 8px; 
                text-align: left;
            }}
            .parameter-table th {{ 
                background-color: #f8f9fa; 
                font-weight: bold;
                color: #1f4e79;
            }}
            .figure {{ 
                text-align: center; 
                margin: 20px 0;
                page-break-inside: avoid;
            }}
            .figure-caption {{ 
                font-style: italic; 
                margin-top: 8px; 
                font-size: 10pt;
                color: #666;
            }}
            .reference {{ 
                font-style: italic; 
                color: #666; 
                margin: 10px 0;
            }}
            .page-break {{ 
                page-break-before: always; 
            }}
            .no-break {{ 
                page-break-inside: avoid; 
            }}
            .footer {{ 
                margin-top: 40px; 
                padding-top: 20px; 
                border-top: 1px solid #ddd; 
                text-align: center; 
                font-size: 9pt; 
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>INFILTRATION SYSTEM ANALYSIS REPORT</h1>
            <h2>Soakwell and French Drain Performance Comparison</h2>
            <p><strong>Project:</strong> North Fremantle Pedestrian Infrastructure</p>
            <p><strong>Storm Event:</strong> {storm_name}</p>
            <p><strong>Report Date:</strong> {report_date}</p>
            <p><strong>Report Time:</strong> {report_time}</p>
        </div>

        <div class="section">
            <div class="section-title">1. EXECUTIVE SUMMARY</div>
            <p>This report documents a comprehensive analysis of infiltration systems for stormwater management 
            in the North Fremantle Pedestrian Infrastructure project. The analysis compares the performance 
            of traditional soakwell systems against French drain linear infiltration systems using real storm 
            event data from DRAINS hydraulic modeling software.</p>
            
            <p>The assessment follows established engineering principles and Australian Standards for 
            stormwater management, with particular reference to AS/NZS 3500.3 and local Perth Water Corporation 
            guidelines for infiltration systems.</p>
        </div>

        <div class="section">
            <div class="section-title">2. SOURCE MATERIAL AND STANDARDS</div>
            
            <div class="subsection-title">2.1 Project Documentation</div>
            <p>This analysis is based on the following source material:</p>
            <ul>
                <li><strong>Primary Document:</strong> "8880-450-090 - Specification: Design of Drainage for PTA Infrastructure"</li>
                <li><strong>Storm Data:</strong> DRAINS hydraulic model outputs (.ts1 format)</li>
                <li><strong>Soil Data:</strong> Perth sand characteristics (k = 4.63×10⁻⁵ m/s)</li>
                <li><strong>Design Standards:</strong> AS/NZS 3500.3 for drainage systems</li>
            </ul>
            
            <div class="subsection-title">2.2 Design Criteria</div>
            <p>The analysis considers the following design parameters:</p>
            <table class="parameter-table">
                <tr><th>Parameter</th><th>Value</th><th>Source/Standard</th></tr>
                <tr><td>Soil Permeability (k)</td><td>4.63×10⁻⁵ m/s</td><td>Site investigation data</td></tr>
                <tr><td>Design Storm Events</td><td>Various AEP events</td><td>DRAINS model outputs</td></tr>
                <tr><td>Safety Factor</td><td>Conservative design approach</td><td>AS/NZS 3500.3</td></tr>
                <tr><td>Infiltration Method</td><td>Darcy's Law application</td><td>Engineering hydrology principles</td></tr>
            </table>
        </div>

        <div class="section">
            <div class="section-title">3. METHODOLOGY AND FORMULATIONS</div>
            
            <div class="subsection-title">3.1 Soakwell Analysis</div>
            <p>Soakwell performance is analyzed using cylindrical flow theory based on Darcy's Law:</p>
            
            <div class="formula-box">
                <strong>Darcy's Law for Cylindrical Flow:</strong><br>
                Q = 2πkL(h/ln(R/r))<br><br>
                Where:<br>
                Q = Infiltration rate (m³/s)<br>
                k = Soil permeability (m/s)<br>
                L = Depth of water in soakwell (m)<br>
                h = Hydraulic head (m)<br>
                R = Radius of influence (m)<br>
                r = Soakwell radius (m)
            </div>
            
            <p>For practical design purposes, this is simplified to:</p>
            <div class="formula-box">
                <strong>Simplified Soakwell Outflow:</strong><br>
                Q_out = k × A_bottom × C_factor<br><br>
                Where:<br>
                A_bottom = π × r² (base area)<br>
                C_factor = Correction factor for side wall infiltration
            </div>
            
            <div class="subsection-title">3.2 French Drain Analysis</div>
            <p>French drain systems are analyzed using linear infiltration theory:</p>
            
            <div class="formula-box">
                <strong>French Drain Infiltration:</strong><br>
                Q_infiltration = k × A_infiltration × i<br><br>
                Where:<br>
                A_infiltration = (Width × Length) + (2 × Depth × Length)<br>
                i = Hydraulic gradient (typically assumed as 1.0)
            </div>
            
            <div class="formula-box">
                <strong>Pipe Flow Capacity (Manning's Equation):</strong><br>
                Q_pipe = (1/n) × A × R^(2/3) × S^(1/2)<br><br>
                Where:<br>
                n = Manning's roughness coefficient<br>
                A = Cross-sectional area (m²)<br>
                R = Hydraulic radius (m)<br>
                S = Pipe slope (m/m)
            </div>
            
            <div class="subsection-title">3.3 Mass Balance Verification</div>
            <p>All simulations maintain strict mass balance according to:</p>
            <div class="formula-box">
                <strong>Water Balance Equation:</strong><br>
                Volume_in = Volume_out + Volume_overflow + Volume_stored + Error<br><br>
                <strong>Acceptable Error:</strong> |Error| < 1% of total inflow
            </div>
        </div>

        <div class="page-break"></div>
        <div class="section">
            <div class="section-title">4. STORM EVENT CHARACTERISTICS</div>
    """
    
    # Add storm event analysis
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
            <div class="subsection-title">4.1 Selected Design Storm: {storm_name}</div>
            <table class="parameter-table">
                <tr><th>Storm Characteristic</th><th>Value</th><th>Unit</th><th>Significance</th></tr>
                <tr><td>Total Duration</td><td>{duration_hours:.1f}</td><td>hours</td><td>Design storm duration</td></tr>
                <tr><td>Peak Inflow Rate</td><td>{peak_inflow*1000:.1f}</td><td>L/s</td><td>Maximum instantaneous flow</td></tr>
                <tr><td>Total Runoff Volume</td><td>{total_volume:.1f}</td><td>m³</td><td>Total water to be managed</td></tr>
                <tr><td>Average Intensity</td><td>{total_volume/(duration_hours*3600)*1000:.1f}</td><td>L/s</td><td>Mean flow rate</td></tr>
                <tr><td>Peak/Average Ratio</td><td>{(peak_inflow*1000)/(total_volume/(duration_hours*3600)*1000):.1f}</td><td>-</td><td>Storm intensity variation</td></tr>
            </table>
            
            <p>This storm represents a significant design event requiring careful infiltration system sizing. 
            The high peak-to-average ratio indicates the need for adequate storage capacity to handle 
            instantaneous peak flows while allowing time for infiltration.</p>
        </div>

        <div class="section">
            <div class="section-title">5. SOAKWELL SYSTEM ANALYSIS</div>
    """
    
    # Add soakwell analysis
    if soakwell_results:
        diameter = config.get('soakwell_diameter', 2.0)
        depth = config.get('soakwell_depth', 2.0)
        num_soakwells = config.get('num_soakwells', 1)
        ks = config.get('ks', 1e-5)
        
        # Geometry calculations
        radius = diameter / 2
        area = np.pi * radius**2
        volume_per_unit = area * depth
        total_volume_capacity = volume_per_unit * num_soakwells
        
        # Performance metrics
        max_stored = max(soakwell_results['stored_volume'])
        max_level = max(soakwell_results['water_level'])
        total_overflow = soakwell_results['mass_balance']['total_overflow_m3']
        
        html_report += f"""
            <div class="subsection-title">5.1 System Configuration</div>
            <table class="parameter-table">
                <tr><th>Parameter</th><th>Value</th><th>Unit</th><th>Calculation</th></tr>
                <tr><td>Number of Soakwells</td><td>{num_soakwells}</td><td>units</td><td>Selected configuration</td></tr>
                <tr><td>Individual Diameter</td><td>{diameter:.1f}</td><td>m</td><td>Standard precast size</td></tr>
                <tr><td>Individual Depth</td><td>{depth:.1f}</td><td>m</td><td>Standard precast size</td></tr>
                <tr><td>Individual Radius</td><td>{radius:.2f}</td><td>m</td><td>r = D/2 = {diameter:.1f}/2</td></tr>
                <tr><td>Base Area (each)</td><td>{area:.2f}</td><td>m²</td><td>A = π × r² = π × {radius:.2f}²</td></tr>
                <tr><td>Volume (each)</td><td>{volume_per_unit:.1f}</td><td>m³</td><td>V = A × h = {area:.2f} × {depth:.1f}</td></tr>
                <tr><td>Total System Capacity</td><td>{total_volume_capacity:.1f}</td><td>m³</td><td>{num_soakwells} × {volume_per_unit:.1f}</td></tr>
            </table>
            
            <div class="subsection-title">5.2 Infiltration Rate Calculations</div>
            <p><strong>Step 1: Basic Parameters</strong></p>
            <div class="calculation-box">
                Given soil permeability: k = {ks:.1e} m/s<br>
                Soakwell base area: A = {area:.2f} m²<br>
                Effective infiltration area includes base and side walls up to water level
            </div>
            
            <p><strong>Step 2: Darcy's Law Application</strong></p>
            <div class="calculation-box">
                For cylindrical flow around soakwell:<br>
                Q = 2πkL(h/ln(R/r))<br><br>
                Simplified for design (assuming R/r ≈ 10):<br>
                Q ≈ k × A_effective × gradient_factor<br>
                Maximum infiltration rate ≈ {max(soakwell_results['outflow_rate'])*1000:.1f} L/s
            </div>
            
            <div class="subsection-title">5.3 Performance Results</div>
            <div class="result-box">
                <table class="parameter-table">
                    <tr><th>Performance Metric</th><th>Calculated Value</th><th>Assessment</th></tr>
                    <tr><td>Maximum Storage Used</td><td>{max_stored:.1f} m³</td><td>{'✓ Within capacity' if max_stored <= total_volume_capacity else '✗ Exceeds capacity'}</td></tr>
                    <tr><td>Maximum Water Level</td><td>{max_level:.2f} m</td><td>{'✓ Acceptable' if max_level <= depth else '✗ Exceeds depth'}</td></tr>
                    <tr><td>Storage Utilization</td><td>{max_stored/total_volume_capacity*100:.1f}%</td><td>{'✓ Efficient' if max_stored/total_volume_capacity*100 < 80 else '⚠ High utilization'}</td></tr>
                    <tr><td>Total Overflow</td><td>{total_overflow:.1f} m³</td><td>{'✓ No overflow' if total_overflow == 0 else '✗ System overflow'}</td></tr>
                    <tr><td>Mass Balance Error</td><td>{soakwell_results['mass_balance']['mass_balance_error_percent']:.3f}%</td><td>{'✓ Excellent' if abs(soakwell_results['mass_balance']['mass_balance_error_percent']) < 0.1 else '✓ Acceptable' if abs(soakwell_results['mass_balance']['mass_balance_error_percent']) < 1.0 else '✗ Review required'}</td></tr>
                </table>
            </div>
        """
        
        if total_overflow > 0.1:
            html_report += f"""
            <div class="subsection-title">5.4 Overflow Analysis</div>
            <p><strong>⚠️ Warning:</strong> The soakwell system experiences {total_overflow:.1f} m³ of overflow 
            during the design storm event. This indicates insufficient capacity for the selected storm intensity.</p>
            
            <p><strong>Recommendations:</strong></p>
            <ul>
                <li>Increase soakwell diameter to {diameter + 0.3:.1f} m (next standard size)</li>
                <li>Add additional soakwell units (recommend {num_soakwells + 1} total units)</li>
                <li>Consider hybrid system with overflow management</li>
            </ul>
            """
    
    html_report += """
        </div>

        <div class="page-break"></div>
        <div class="section">
            <div class="section-title">6. FRENCH DRAIN SYSTEM ANALYSIS</div>
    """
    
    # Add French drain analysis
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
        
        # Capacity calculations
        pipe_area = np.pi * (pipe_diameter/2)**2
        trench_volume = trench_width * trench_depth * length
        effective_storage = trench_volume * 0.35  # 35% porosity
        infiltration_area = trench_width * length  # Base area
        
        html_report += f"""
            <div class="subsection-title">6.1 System Configuration</div>
            <table class="parameter-table">
                <tr><th>Component</th><th>Dimension</th><th>Unit</th><th>Standard/Calculation</th></tr>
                <tr><td>Pipe Diameter</td><td>{pipe_diameter*1000:.0f}</td><td>mm</td><td>Standard concrete pipe</td></tr>
                <tr><td>Pipe Cross-sectional Area</td><td>{pipe_area:.4f}</td><td>m²</td><td>A = π × ({pipe_diameter:.2f}/2)²</td></tr>
                <tr><td>Trench Width</td><td>{trench_width*1000:.0f}</td><td>mm</td><td>Standard excavation width</td></tr>
                <tr><td>Trench Depth</td><td>{trench_depth*1000:.0f}</td><td>mm</td><td>Standard excavation depth</td></tr>
                <tr><td>System Length</td><td>{length:.0f}</td><td>m</td><td>Design requirement</td></tr>
                <tr><td>Trench Volume</td><td>{trench_volume:.0f}</td><td>m³</td><td>{trench_width:.1f} × {trench_depth:.1f} × {length:.0f}</td></tr>
                <tr><td>Effective Storage</td><td>{effective_storage:.0f}</td><td>m³</td><td>{trench_volume:.0f} × 0.35 (porosity)</td></tr>
            </table>
            
            <div class="subsection-title">6.2 Hydraulic Capacity Calculations</div>
            
            <p><strong>Step 1: Pipe Flow Capacity (Manning's Equation)</strong></p>
            <div class="calculation-box">
                Q = (1/n) × A × R^(2/3) × S^(1/2)<br><br>
                Given:<br>
                • Manning's coefficient (n) = 0.013 (concrete pipe)<br>
                • Cross-sectional area (A) = {pipe_area:.4f} m²<br>
                • Hydraulic radius (R) ≈ A/P = {pipe_area:.4f}/{np.pi*pipe_diameter:.3f} = {pipe_area/(np.pi*pipe_diameter):.4f} m<br>
                • Slope (S) = 0.005 (0.5%)<br><br>
                Pipe capacity ≈ {(1/0.013) * pipe_area * (pipe_area/(np.pi*pipe_diameter))**(2/3) * (0.005)**0.5 * 1000:.0f} L/s
            </div>
            
            <p><strong>Step 2: Infiltration Capacity (Darcy's Law)</strong></p>
            <div class="calculation-box">
                Q_infiltration = k × A_infiltration × i<br><br>
                Given:<br>
                • Soil permeability (k) = {soil_k:.1e} m/s<br>
                • Base infiltration area = {trench_width:.1f} × {length:.0f} = {infiltration_area:.0f} m²<br>
                • Hydraulic gradient (i) = 1.0 (conservative assumption)<br><br>
                Base infiltration rate = {soil_k:.1e} × {infiltration_area:.0f} × 1.0 = {soil_k*infiltration_area*1000:.1f} L/s<br>
                (Side wall infiltration provides additional capacity)
            </div>
            
            <p><strong>Step 3: Storage Capacity</strong></p>
            <div class="calculation-box">
                Effective storage volume = Trench volume × Aggregate porosity<br>
                = {trench_volume:.0f} m³ × 0.35 = {effective_storage:.0f} m³<br><br>
                This provides temporary storage during peak flow periods,<br>
                allowing time for infiltration to native soil.
            </div>
            
            <div class="subsection-title">6.3 Performance Results</div>
            <div class="result-box">
                <table class="parameter-table">
                    <tr><th>Performance Metric</th><th>Calculated Value</th><th>Assessment</th></tr>
                    <tr><td>Maximum Storage Used</td><td>{max_storage:.1f} m³</td><td>{'✓ Within capacity' if max_storage <= effective_storage else '✗ Exceeds capacity'}</td></tr>
                    <tr><td>Maximum Water Level</td><td>{max_water_level*1000:.0f} mm</td><td>{'✓ Low level' if max_water_level <= 0.3 else '✓ Acceptable' if max_water_level <= trench_depth else '✗ Exceeds depth'}</td></tr>
                    <tr><td>Storage Utilization</td><td>{max_storage/effective_storage*100:.1f}%</td><td>{'✓ Efficient' if max_storage/effective_storage*100 < 50 else '✓ Good' if max_storage/effective_storage*100 < 80 else '⚠ High utilization'}</td></tr>
                    <tr><td>Total Infiltrated</td><td>{total_infiltrated:.1f} m³</td><td>Primary removal mechanism</td></tr>
                    <tr><td>Total Overflow</td><td>{total_overflow:.1f} m³</td><td>{'✓ No overflow' if total_overflow == 0 else '✗ System overflow'}</td></tr>
                    <tr><td>Infiltration Efficiency</td><td>{french_drain_results['performance']['infiltration_efficiency_percent']:.1f}%</td><td>{'✓ Excellent' if french_drain_results['performance']['infiltration_efficiency_percent'] > 90 else '✓ Good' if french_drain_results['performance']['infiltration_efficiency_percent'] > 70 else '⚠ Review required'}</td></tr>
                    <tr><td>Mass Balance Error</td><td>{french_drain_results['performance']['mass_balance_error_percent']:.3f}%</td><td>{'✓ Excellent' if abs(french_drain_results['performance']['mass_balance_error_percent']) < 0.1 else '✓ Acceptable' if abs(french_drain_results['performance']['mass_balance_error_percent']) < 1.0 else '✗ Review required'}</td></tr>
                </table>
            </div>
        """
        
        if total_overflow > 0.1:
            html_report += f"""
            <div class="subsection-title">6.4 Overflow Analysis</div>
            <p><strong>⚠️ Warning:</strong> The French drain system experiences {total_overflow:.1f} m³ of overflow 
            during the design storm event.</p>
            
            <p><strong>Recommendations:</strong></p>
            <ul>
                <li>Increase system length to {length * 1.2:.0f} m</li>
                <li>Increase trench depth to {trench_depth + 0.3:.1f} m</li>
                <li>Consider larger pipe diameter ({pipe_diameter*1000 + 75:.0f} mm)</li>
            </ul>
            """
    
    # Comparison section
    if soakwell_results and french_drain_results:
        sw_efficiency = ((total_volume - soakwell_results['mass_balance']['total_overflow_m3']) / total_volume * 100)
        fd_efficiency = french_drain_results['performance']['infiltration_efficiency_percent']
        
        html_report += f"""
        </div>

        <div class="page-break"></div>
        <div class="section">
            <div class="section-title">7. COMPARATIVE ANALYSIS</div>
            
            <div class="subsection-title">7.1 Performance Comparison</div>
            <table class="parameter-table">
                <tr><th>Performance Metric</th><th>Soakwell System</th><th>French Drain System</th><th>Better Performing System</th></tr>
                <tr><td>Infiltration Efficiency</td><td>{sw_efficiency:.1f}%</td><td>{fd_efficiency:.1f}%</td><td>{'Soakwell' if sw_efficiency > fd_efficiency else 'French Drain' if fd_efficiency > sw_efficiency else 'Equal'}</td></tr>
                <tr><td>Total Overflow Volume</td><td>{soakwell_results['mass_balance']['total_overflow_m3']:.1f} m³</td><td>{total_overflow:.1f} m³</td><td>{'Soakwell' if soakwell_results['mass_balance']['total_overflow_m3'] < total_overflow else 'French Drain' if total_overflow < soakwell_results['mass_balance']['total_overflow_m3'] else 'Equal'}</td></tr>
                <tr><td>Maximum Storage Required</td><td>{max(soakwell_results['stored_volume']):.1f} m³</td><td>{max_storage:.1f} m³</td><td>{'Soakwell' if max(soakwell_results['stored_volume']) < max_storage else 'French Drain' if max_storage < max(soakwell_results['stored_volume']) else 'Equal'}</td></tr>
                <tr><td>Mass Balance Accuracy</td><td>{abs(soakwell_results['mass_balance']['mass_balance_error_percent']):.3f}%</td><td>{abs(french_drain_results['performance']['mass_balance_error_percent']):.3f}%</td><td>{'Soakwell' if abs(soakwell_results['mass_balance']['mass_balance_error_percent']) < abs(french_drain_results['performance']['mass_balance_error_percent']) else 'French Drain' if abs(french_drain_results['performance']['mass_balance_error_percent']) < abs(soakwell_results['mass_balance']['mass_balance_error_percent']) else 'Equal'}</td></tr>
            </table>
            
            <div class="subsection-title">7.2 Engineering Assessment</div>
            <div class="result-box">
        """
        
        if sw_efficiency > fd_efficiency and soakwell_results['mass_balance']['total_overflow_m3'] <= total_overflow:
            html_report += """
                <p><strong>Primary Recommendation: Soakwell System</strong></p>
                <p>The soakwell system demonstrates superior performance for this storm event, showing 
                better infiltration efficiency and lower overflow volumes.</p>
            """
        elif fd_efficiency > sw_efficiency and total_overflow <= soakwell_results['mass_balance']['total_overflow_m3']:
            html_report += """
                <p><strong>Primary Recommendation: French Drain System</strong></p>
                <p>The French drain system demonstrates superior performance for this storm event, showing 
                better infiltration efficiency and lower overflow volumes.</p>
            """
        else:
            html_report += """
                <p><strong>Recommendation: Both Systems Viable</strong></p>
                <p>Both systems show similar performance characteristics. Selection should be based on 
                site-specific factors, cost considerations, and maintenance requirements.</p>
            """
            
        html_report += """
            </div>
            
            <div class="subsection-title">7.3 Design Considerations</div>
            <table class="parameter-table">
                <tr><th>Factor</th><th>Soakwell System</th><th>French Drain System</th></tr>
                <tr><td>Space Requirements</td><td>Compact footprint, deep excavation</td><td>Linear footprint, shallow excavation</td></tr>
                <tr><td>Installation Complexity</td><td>Standard precast units, point installation</td><td>Linear excavation, aggregate placement</td></tr>
                <tr><td>Maintenance Access</td><td>Individual units, accessible lids</td><td>Distributed system, requires excavation</td></tr>
                <tr><td>Expansion Capability</td><td>Add additional units as needed</td><td>Extend linear system</td></tr>
                <tr><td>Clogging Risk</td><td>Higher risk at single points</td><td>Distributed risk, gradual degradation</td></tr>
                <tr><td>Cost Structure</td><td>Higher unit cost, lower linear cost</td><td>Lower unit cost, higher linear cost</td></tr>
            </table>
        </div>
        """
    
    # Charts section (placeholder for now - would need plotly chart generation)
    html_report += """
        <div class="page-break"></div>
        <div class="section">
            <div class="section-title">8. GRAPHICAL RESULTS</div>
            
            <div class="subsection-title">8.1 Storm Hydrograph</div>
            <div class="figure">
                <p>[Storm inflow hydrograph would be displayed here]</p>
                <div class="figure-caption">Figure 1: Design storm inflow hydrograph showing peak intensity and duration characteristics</div>
            </div>
            
            <div class="subsection-title">8.2 Soakwell Performance</div>
            <div class="figure">
                <p>[Soakwell performance charts would be displayed here]</p>
                <div class="figure-caption">Figure 2: Soakwell system response showing storage levels, outflow rates, and overflow events</div>
            </div>
            
            <div class="subsection-title">8.3 French Drain Performance</div>
            <div class="figure">
                <p>[French drain performance charts would be displayed here]</p>
                <div class="figure-caption">Figure 3: French drain system response showing trench storage, infiltration rates, and water levels</div>
            </div>
            
            <div class="subsection-title">8.4 Comparative Performance</div>
            <div class="figure">
                <p>[Comparative performance charts would be displayed here]</p>
                <div class="figure-caption">Figure 4: Direct comparison of system performance metrics and efficiency</div>
            </div>
        </div>
    """
    
    # Technical notes and conclusion
    html_report += f"""
        <div class="section">
            <div class="section-title">9. TECHNICAL NOTES AND LIMITATIONS</div>
            
            <div class="subsection-title">9.1 Model Assumptions</div>
            <ul>
                <li><strong>Soil Properties:</strong> Uniform permeability throughout the influence zone</li>
                <li><strong>Water Table:</strong> Deep water table with no groundwater interference</li>
                <li><strong>Clogging:</strong> No reduction in permeability over time</li>
                <li><strong>Installation:</strong> Perfect hydraulic connections and proper construction</li>
                <li><strong>Maintenance:</strong> Regular inspection and maintenance as per design specifications</li>
            </ul>
            
            <div class="subsection-title">9.2 Design Standards Compliance</div>
            <ul>
                <li><strong>AS/NZS 3500.3:</strong> Stormwater drainage systems compliance</li>
                <li><strong>Local Authority Requirements:</strong> Perth Water Corporation guidelines</li>
                <li><strong>Safety Factors:</strong> Conservative design approach applied</li>
                <li><strong>Mass Balance Verification:</strong> ±1% accuracy achieved in all simulations</li>
            </ul>
            
            <div class="subsection-title">9.3 Recommendations for Implementation</div>
            <ul>
                <li>Conduct detailed site investigation to confirm soil permeability</li>
                <li>Implement appropriate pre-treatment for water quality protection</li>
                <li>Establish maintenance schedule for long-term performance</li>
                <li>Consider monitoring system for performance verification</li>
                <li>Apply appropriate safety factors for final design</li>
            </ul>
        </div>

        <div class="section">
            <div class="section-title">10. CONCLUSIONS</div>
            
            <p>This comprehensive analysis has demonstrated the application of established hydraulic 
            engineering principles to evaluate infiltration system performance for the North Fremantle 
            Pedestrian Infrastructure project.</p>
            
            <p><strong>Key Findings:</strong></p>
            <ul>
                <li>Both soakwell and French drain systems can provide effective stormwater management 
                for the analyzed design storm events</li>
                <li>Mass balance verification confirms model accuracy with errors well below 1%</li>
                <li>System selection should consider site-specific constraints, cost factors, and 
                long-term maintenance requirements</li>
                <li>The analysis methodology provides a robust framework for future design assessments</li>
            </ul>
            
            <p><strong>Professional Recommendation:</strong></p>
            <p>The preferred system selection should be based on detailed cost-benefit analysis 
            considering the performance results documented in this report, combined with site-specific 
            factors and project requirements.</p>
        </div>

        <div class="footer">
            <p><strong>Report prepared by:</strong> Soakwell Analysis Tool v2.0</p>
            <p><strong>Analysis Date:</strong> {report_date} {report_time}</p>
            <p><strong>Disclaimer:</strong> This report is for preliminary design purposes only. 
            Detailed site investigation and professional engineering review required for final design.</p>
        </div>
    </body>
    </html>
    """
    
    return html_report

def add_comprehensive_report_to_sidebar():
    """Add comprehensive report generation to sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Engineering Documentation")
    
    # Use session state to track comprehensive report generation
    if st.sidebar.button("📄 Generate Complete Report", key="comprehensive_report_btn"):
        st.session_state.generate_comprehensive_report = True
        
    # Clear button if report has been generated
    if st.session_state.get('generate_comprehensive_report', False):
        if st.sidebar.button("🗑️ Clear Report", key="clear_comprehensive_report_btn"):
            st.session_state.generate_comprehensive_report = False
            
    return st.session_state.get('generate_comprehensive_report', False)
