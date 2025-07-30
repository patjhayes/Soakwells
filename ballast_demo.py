"""
Demonstration: Ballast Storage Integration with Soakwell Analysis
Shows how to use the new ballast storage features for rail formation flood analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Try to import ballast analysis modules
try:
    from ballast_storage_analysis import BallastStorageAnalyzer
    from ballast_integration import add_ballast_storage_ui, run_ballast_analysis, display_ballast_results
    BALLAST_AVAILABLE = True
    print("✅ Ballast storage analysis modules loaded successfully")
except ImportError as e:
    BALLAST_AVAILABLE = False
    print(f"⚠️ Ballast storage analysis not available: {e}")
    print("Install required packages: pip install scipy beautifulsoup4 lxml")

def create_sample_12d_html():
    """Create a sample 12D HTML file for demonstration"""
    
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Formation Storage Volumes - 12d Model</title>
    </head>
    <body>
        <h1>North Fremantle Pedestrian Infrastructure</h1>
        <h2>Formation Storage Volume Analysis</h2>
        
        <table border="1">
            <tr>
                <th>Height (m AHD)</th>
                <th>Volume (m³)</th>
                <th>Area (m²)</th>
            </tr>
            <tr><td>10.00</td><td>0</td><td>500</td></tr>
            <tr><td>10.25</td><td>125</td><td>500</td></tr>
            <tr><td>10.50</td><td>250</td><td>500</td></tr>
            <tr><td>10.75</td><td>400</td><td>533</td></tr>
            <tr><td>11.00</td><td>575</td><td>583</td></tr>
            <tr><td>11.25</td><td>775</td><td>633</td></tr>
            <tr><td>11.50</td><td>1000</td><td>683</td></tr>
            <tr><td>11.75</td><td>1250</td><td>733</td></tr>
            <tr><td>12.00</td><td>1525</td><td>783</td></tr>
            <tr><td>12.25</td><td>1825</td><td>833</td></tr>
            <tr><td>12.50</td><td>2150</td><td>883</td></tr>
        </table>
        
        <p>Analysis completed: 12d Model Civil v15</p>
        <p>Project: 528009 - North Fremantle Pedestrian</p>
    </body>
    </html>
    """
    
    with open("sample_formation_storage.html", "w") as f:
        f.write(sample_html)
    
    print("✅ Sample 12D HTML file created: sample_formation_storage.html")
    return "sample_formation_storage.html"

def create_sample_ts1_data():
    """Create sample .ts1 storm data for 1% AEP event"""
    
    # Create a realistic storm hydrograph for 1% AEP event
    time_minutes = np.arange(0, 720, 5)  # 12 hours, 5-minute intervals
    
    # Double-peaked storm typical of Perth
    peak1_time = 60  # First peak at 1 hour
    peak2_time = 180  # Second peak at 3 hours
    peak1_intensity = 0.15  # m³/s
    peak2_intensity = 0.25  # m³/s (main peak)
    
    # Generate hydrograph using gamma distribution-like shape
    flow_rates = np.zeros_like(time_minutes, dtype=float)
    
    for i, t in enumerate(time_minutes):
        # First peak
        if t <= peak1_time * 2:
            flow1 = peak1_intensity * np.exp(-((t - peak1_time) / 30)**2)
        else:
            flow1 = 0
        
        # Second peak (main event)
        if t >= peak1_time and t <= peak2_time * 2:
            flow2 = peak2_intensity * np.exp(-((t - peak2_time) / 45)**2)
        else:
            flow2 = 0
        
        # Background flow
        background = 0.01 * np.exp(-(t / 200)**1.5)
        
        flow_rates[i] = max(flow1 + flow2 + background, 0)
    
    # Create DataFrame in .ts1 format
    ts1_data = pd.DataFrame({
        'Time_min': time_minutes,
        'Flow_m3s': flow_rates
    })
    
    # Add typical .ts1 metadata as comments (8 lines)
    metadata = [
        "# North Fremantle ILSAX Catchments 1% AEP Storm Event",
        "# Generated for ballast storage demonstration",
        "# Duration: 12 hours, Interval: 5 minutes", 
        "# Peak flow: 0.25 m³/s",
        "# Total volume: 58.3 m³",
        "# Storm pattern: Double-peaked Perth design storm",
        "# Analysis date: 2025-07-30",
        "# Format: Time(min), Flow(m³/s)"
    ]
    
    # Write .ts1 file
    with open("demo_1percent_AEP.ts1", "w") as f:
        for line in metadata:
            f.write(line + "\n")
        f.write("Time_min,Flow_m3s\n")  # Header line (9th line)
        for _, row in ts1_data.iterrows():
            f.write(f"{row['Time_min']:.1f},{row['Flow_m3s']:.6f}\n")
    
    print("✅ Sample 1% AEP storm file created: demo_1percent_AEP.ts1")
    print(f"   Peak flow: {flow_rates.max():.3f} m³/s")
    print(f"   Total volume: {np.sum(flow_rates) * 5 * 60:.1f} m³")
    
    return ts1_data

def demonstrate_ballast_analysis():
    """Complete demonstration of ballast storage analysis"""
    
    if not BALLAST_AVAILABLE:
        print("❌ Cannot run demonstration - ballast analysis modules not available")
        return
    
    print("\n🚂 BALLAST STORAGE ANALYSIS DEMONSTRATION")
    print("=" * 60)
    
    # Step 1: Create sample data
    print("\n1️⃣ Creating sample data...")
    html_file = create_sample_12d_html()
    ts1_data = create_sample_ts1_data()
    
    # Step 2: Initialize ballast analyzer
    print("\n2️⃣ Setting up ballast analyzer...")
    analyzer = BallastStorageAnalyzer()
    analyzer.ballast_void_ratio = 0.75
    analyzer.effective_porosity = analyzer.ballast_void_ratio / (1 + analyzer.ballast_void_ratio)
    
    # Step 3: Parse 12D data
    print("\n3️⃣ Parsing 12D stage-storage data...")
    stage_storage_df = analyzer.parse_12d_stage_storage_html(html_file)
    print(f"   Parsed {len(stage_storage_df)} data points")
    print(f"   Storage range: {stage_storage_df['Volume_m3'].min():.0f} to {stage_storage_df['Volume_m3'].max():.0f} m³")
    
    # Step 4: Adjust datum
    print("\n4️⃣ Adjusting datum to soakwell level...")
    soakwell_invert = 9.8  # m AHD
    adjusted_data = analyzer.adjust_datum_to_soakwell(soakwell_invert_level=soakwell_invert)
    print(f"   Soakwell invert: {soakwell_invert:.1f} m AHD")
    print(f"   Max effective storage: {adjusted_data['Effective_Volume_m3'].max():.0f} m³")
    
    # Step 5: Configure soakwell system
    print("\n5️⃣ Configuring soakwell system...")
    soakwell_config = {
        'soakwell_diameter': 2.0,  # m
        'soakwell_depth': 2.5,     # m
        'num_soakwells': 1,
        'ks': 4.63e-5              # m/s (Perth sand)
    }
    
    soakwell_capacity = np.pi * (soakwell_config['soakwell_diameter']/2)**2 * soakwell_config['soakwell_depth']
    print(f"   Soakwell capacity: {soakwell_capacity:.1f} m³")
    
    # Step 6: Create mock soakwell results (for demonstration)
    print("\n6️⃣ Running ballast analysis...")
    mock_soakwell_results = {
        'stored_volume': [0],  # Will be calculated in ballast analysis
        'water_level': [0],
        'overflow_rate': [0],
        'mass_balance': {'mass_balance_error_percent': 0.05}
    }
    
    # Run combined analysis
    ballast_results = analyzer.analyze_soakwell_ballast_system(
        soakwell_results=mock_soakwell_results,
        hydrograph_data=ts1_data,
        soakwell_config=soakwell_config
    )
    
    # Step 7: Display results
    print("\n7️⃣ Analysis Results:")
    perf = ballast_results['performance']
    print(f"   Max water level: {perf['max_water_level_AHD']:.2f} m AHD")
    print(f"   Formation flooding: {perf['max_height_above_formation']:.2f} m {'(FLOODED!)' if perf['rail_formation_flooded'] else '(Safe)'}")
    print(f"   Ballast storage used: {perf['ballast_storage_utilized_percent']:.1f}%")
    print(f"   System overflow: {perf['total_system_overflow_m3']:.1f} m³")
    
    # Step 8: Generate plots
    print("\n8️⃣ Generating analysis plots...")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    time_hours = ballast_results['time_minutes'] / 60
    
    # Storm hydrograph
    ax1.plot(time_hours, ts1_data['Flow_m3s'] * 1000, 'b-', linewidth=2)
    ax1.set_xlabel('Time (hours)')
    ax1.set_ylabel('Inflow Rate (L/s)')
    ax1.set_title('1% AEP Design Storm')
    ax1.grid(True, alpha=0.3)
    
    # Water levels
    ax2.plot(time_hours, ballast_results['water_level_AHD'], 'r-', linewidth=2, label='Water Level')
    ax2.axhline(y=soakwell_invert, color='k', linestyle='--', alpha=0.7, label='Soakwell Invert')
    ax2.axhline(y=soakwell_invert + 2.5, color='orange', linestyle='--', alpha=0.7, label='Formation Level')
    ax2.set_xlabel('Time (hours)')
    ax2.set_ylabel('Water Level (m AHD)')
    ax2.set_title('System Water Levels')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Storage volumes
    ax3.plot(time_hours, ballast_results['soakwell_volume'], 'g-', label='Soakwell', linewidth=2)
    ax3.plot(time_hours, ballast_results['ballast_volume'], 'orange', label='Ballast', linewidth=2)
    ax3.plot(time_hours, ballast_results['total_storage'], 'r-', label='Total', linewidth=2)
    ax3.set_xlabel('Time (hours)')
    ax3.set_ylabel('Storage Volume (m³)')
    ax3.set_title('Storage Utilization')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Stage-storage curve
    ax4.plot(adjusted_data['Effective_Volume_m3'], adjusted_data['Height_Above_Soakwell_m'], 'b-o', label='Available')
    max_ballast = perf['max_ballast_storage_m3']
    if max_ballast > 0:
        ax4.axvline(x=max_ballast, color='r', linestyle=':', label=f'Max Used ({max_ballast:.0f}m³)')
    ax4.axhline(y=0, color='k', linestyle='--', alpha=0.5, label='Soakwell Invert')
    ax4.set_xlabel('Effective Volume (m³)')
    ax4.set_ylabel('Height Above Soakwell (m)')
    ax4.set_title('Ballast Stage-Storage')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('ballast_analysis_demo.png', dpi=300, bbox_inches='tight')
    print("   Plot saved: ballast_analysis_demo.png")
    
    # Step 9: Generate report section
    print("\n9️⃣ Generating report section...")
    report_html = analyzer.generate_ballast_analysis_report(ballast_results, "1% AEP Demo Storm")
    
    with open("ballast_report_section.html", "w") as f:
        f.write(f"""
        <!DOCTYPE html>
        <html>
        <head><title>Ballast Analysis Report</title></head>
        <body>
        {report_html}
        </body>
        </html>
        """)
    
    print("   Report section saved: ballast_report_section.html")
    
    # Cleanup
    import os
    for temp_file in [html_file]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    print("\n✅ DEMONSTRATION COMPLETE!")
    print(f"🎯 Key Finding: {'Rail formation flooding detected!' if perf['rail_formation_flooded'] else 'System adequately contains 1% AEP storm'}")
    
    return ballast_results

def usage_instructions():
    """Print usage instructions for the ballast storage system"""
    
    print("\n📋 BALLAST STORAGE ANALYSIS USAGE GUIDE")
    print("=" * 50)
    
    print("""
🎯 PURPOSE:
   Model soakwell overflow into rail formation ballast during extreme events
   Determine maximum flood elevations for rare storms (1% AEP)
   Assess rail formation flooding risk

📁 REQUIRED FILES:
   1. 12D HTML file: Formation_Storage_Volumes.html (stage-storage relationship)
   2. Storm data: .ts1 files for extreme events (1% AEP recommended)

🔧 SETUP PROCESS:
   1. Install additional packages: pip install -r requirements_ballast.txt
   2. Import ballast modules in your dashboard
   3. Add ballast UI components to Streamlit interface
   4. Configure soakwell invert level and formation parameters

💻 INTEGRATION WITH EXISTING SYSTEM:
   # In your soakwell_dashboard.py:
   from ballast_integration import add_ballast_storage_ui, run_ballast_analysis
   
   # Add to UI:
   ballast_config = add_ballast_storage_ui()
   
   # Run analysis:
   if ballast_config['enable_ballast']:
       ballast_results = run_ballast_analysis(soakwell_results, hydrograph_data, 
                                            soakwell_config, ballast_config)

📊 OUTPUT ANALYSIS:
   - Maximum water level (m AHD)
   - Rail formation flooding depth
   - Ballast storage utilization percentage
   - System overflow volume
   - Time-series plots of system performance

⚠️ DESIGN IMPLICATIONS:
   - Formation flooding indicates need for enhanced drainage
   - Results inform rail operational procedures during floods
   - Post-flood ballast maintenance requirements identified

🔗 REPORT INTEGRATION:
   Ballast analysis automatically included in comprehensive engineering reports
   Professional documentation suitable for rail infrastructure design reviews
    """)

if __name__ == "__main__":
    print("🚂 Ballast Storage Analysis for Soakwell Systems")
    print("North Fremantle Pedestrian Infrastructure Project\n")
    
    # Show usage instructions
    usage_instructions()
    
    # Run demonstration if modules available
    if BALLAST_AVAILABLE:
        print(f"\n{'='*60}")
        user_input = input("Run demonstration? (y/n): ").lower().strip()
        if user_input in ['y', 'yes']:
            demonstrate_ballast_analysis()
    else:
        print(f"\n{'='*60}")
        print("To run demonstration, install required packages:")
        print("pip install scipy beautifulsoup4 lxml")
