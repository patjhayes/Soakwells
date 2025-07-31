"""
Enhanced Soakwell Analysis with Ballast Storage Integration
Adds ballast storage overflow modeling to existing soakwell analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path

try:
    from ballast_storage_analysis import BallastStorageAnalyzer
    BALLAST_ANALYSIS_AVAILABLE = True
except ImportError:
    BALLAST_ANALYSIS_AVAILABLE = False
    # Note: Don't call st.warning here - it will be handled in the UI functions

def add_ballast_storage_ui():
    """Add ballast storage configuration to the Streamlit UI"""
    
    # Check if ballast analysis is available
    if not BALLAST_ANALYSIS_AVAILABLE:
        with st.expander("🚂 Rail Formation Ballast Storage", expanded=False):
            st.warning("⚠️ Ballast storage analysis not available - install requirements: pip install scipy beautifulsoup4 lxml")
            st.info("This feature requires additional packages for 12D HTML parsing and scientific computing.")
            return {'enable_ballast': False}
    
    with st.expander("🚂 Rail Formation Ballast Storage", expanded=False):
        st.markdown("""
        **Enhanced Flood Analysis:** Model soakwell overflow into rail formation ballast storage 
        for extreme events (1% AEP storms). Upload 12D stage-storage relationship to analyze 
        maximum flood elevations.
        """)
        
        enable_ballast = st.checkbox(
            "Enable ballast storage analysis", 
            value=False,
            help="Model overflow from soakwell into rail formation ballast void space"
        )
        
        ballast_config = {}
        
        if enable_ballast and BALLAST_ANALYSIS_AVAILABLE:
            
            # File upload for 12D stage-storage data
            st.subheader("12D Stage-Storage Data")
            uploaded_file = st.file_uploader(
                "Upload 12D Formation_Storage_Volumes.html file",
                type=['html', 'htm'],
                help="Upload the HTML output from 12D containing stage-storage relationship"
            )
            
            # Manual data entry as alternative
            with st.expander("Or enter stage-storage data manually"):
                manual_data = st.text_area(
                    "Stage-Storage Data (Height,Volume per line)",
                    placeholder="10.0,0\n10.5,150\n11.0,350\n11.5,600\n12.0,900",
                    help="Enter data as Height(m),Volume(m³) one pair per line"
                )
            
            # Configuration parameters
            col1, col2 = st.columns(2)
            
            with col1:
                soakwell_invert = st.number_input(
                    "Soakwell Invert Level (m AHD)", 
                    value=9.5, 
                    step=0.1,
                    help="Bottom level of soakwell in Australian Height Datum"
                )
                
                formation_level = st.number_input(
                    "Rail Formation Level (m AHD)", 
                    value=10.5, 
                    step=0.1,
                    help="Rail formation level (leave as default to auto-detect from 12D data)"
                )
            
            with col2:
                ballast_void_ratio = st.slider(
                    "Ballast Void Ratio", 
                    min_value=0.60, 
                    max_value=0.85, 
                    value=0.75,
                    step=0.05,
                    help="Void ratio of clean rail ballast (0.75 typical)"
                )
                
                effective_porosity = ballast_void_ratio / (1 + ballast_void_ratio)
                st.metric("Effective Porosity", f"{effective_porosity:.1%}")
            
            ballast_config = {
                'enable_ballast': enable_ballast,
                'uploaded_file': uploaded_file,
                'manual_data': manual_data,
                'soakwell_invert': soakwell_invert,
                'formation_level': formation_level,
                'ballast_void_ratio': ballast_void_ratio,
                'effective_porosity': effective_porosity
            }
            
            # Preview uploaded data
            if uploaded_file is not None:
                try:
                    # Save uploaded file temporarily
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Parse and preview
                    analyzer = BallastStorageAnalyzer()
                    stage_storage_df = analyzer.parse_12d_stage_storage_html(temp_path)
                    
                    st.success(f"✅ Successfully parsed {len(stage_storage_df)} stage-storage points")
                    
                    # Show preview
                    with st.expander("Preview Stage-Storage Data"):
                        st.dataframe(stage_storage_df.head(10))
                        
                        # Quick plot
                        fig, ax = plt.subplots(figsize=(8, 4))
                        ax.plot(stage_storage_df['Volume_m3'], stage_storage_df['Height_m'], 'b-o')
                        ax.set_xlabel('Volume (m³)')
                        ax.set_ylabel('Height (m)')
                        ax.set_title('12D Stage-Storage Relationship')
                        ax.grid(True, alpha=0.3)
                        st.pyplot(fig)
                    
                    # Clean up temp file
                    os.remove(temp_path)
                    
                except Exception as e:
                    st.error(f"❌ Error parsing 12D file: {str(e)}")
            
            elif manual_data:
                try:
                    # Parse manual data
                    lines = manual_data.strip().split('\n')
                    data = []
                    for line in lines:
                        if ',' in line:
                            height, volume = line.split(',')
                            data.append([float(height.strip()), float(volume.strip())])
                    
                    if data:
                        manual_df = pd.DataFrame(data, columns=['Height_m', 'Volume_m3'])
                        st.success(f"✅ Parsed {len(manual_df)} manual data points")
                        
                        with st.expander("Preview Manual Data"):
                            st.dataframe(manual_df)
                            
                except Exception as e:
                    st.error(f"❌ Error parsing manual data: {str(e)}")
        
        elif enable_ballast and not BALLAST_ANALYSIS_AVAILABLE:
            st.error("❌ Ballast analysis requires additional packages. Please install: pip install scipy beautifulsoup4")
            ballast_config['enable_ballast'] = False
        
        else:
            ballast_config['enable_ballast'] = False
    
    return ballast_config

def run_ballast_analysis(soakwell_results, hydrograph_data, soakwell_config, ballast_config):
    """
    Run the ballast storage analysis if enabled
    """
    if not ballast_config.get('enable_ballast', False) or not BALLAST_ANALYSIS_AVAILABLE:
        return None
    
    try:
        # Initialize analyzer
        analyzer = BallastStorageAnalyzer()
        analyzer.ballast_void_ratio = ballast_config['ballast_void_ratio']
        analyzer.effective_porosity = ballast_config['effective_porosity']
        
        # Load stage-storage data
        if ballast_config['uploaded_file'] is not None:
            # Use uploaded 12D file
            temp_path = f"temp_{ballast_config['uploaded_file'].name}"
            with open(temp_path, "wb") as f:
                f.write(ballast_config['uploaded_file'].getbuffer())
            
            analyzer.parse_12d_stage_storage_html(temp_path)
            os.remove(temp_path)  # Clean up
            
        elif ballast_config['manual_data']:
            # Use manual data
            lines = ballast_config['manual_data'].strip().split('\n')
            data = []
            for line in lines:
                if ',' in line:
                    height, volume = line.split(',')
                    data.append([float(height.strip()), float(volume.strip())])
            
            stage_storage_df = pd.DataFrame(data, columns=['Height_m', 'Volume_m3'])
            analyzer.stage_storage_data = stage_storage_df
        
        else:
            st.warning("⚠️ No stage-storage data provided for ballast analysis")
            return None
        
        # Adjust datum
        adjusted_data = analyzer.adjust_datum_to_soakwell(
            soakwell_invert_level=ballast_config['soakwell_invert'],
            formation_level=ballast_config['formation_level']
        )
        
        # Run combined analysis
        combined_results = analyzer.analyze_soakwell_ballast_system(
            soakwell_results=soakwell_results,
            hydrograph_data=hydrograph_data,
            soakwell_config=soakwell_config
        )
        
        # Add analyzer reference for reporting
        combined_results['analyzer'] = analyzer
        
        return combined_results
        
    except Exception as e:
        st.error(f"❌ Error in ballast analysis: {str(e)}")
        return None

def display_ballast_results(ballast_results, storm_name):
    """
    Display ballast storage analysis results in Streamlit
    """
    if ballast_results is None:
        return
    
    st.header("🚂 Ballast Storage Analysis Results")
    
    perf = ballast_results['performance']
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Max Water Level", 
            f"{perf['max_water_level_AHD']:.2f} m AHD",
            help="Peak flood level during storm event"
        )
    
    with col2:
        formation_flood = perf['max_height_above_formation']
        st.metric(
            "Formation Flooding", 
            f"{formation_flood:.2f} m" if formation_flood > 0 else "None",
            delta=f"{'Above' if formation_flood > 0 else 'Below'} track level",
            delta_color="inverse" if formation_flood > 0 else "normal"
        )
    
    with col3:
        st.metric(
            "Ballast Storage Used", 
            f"{perf['ballast_storage_utilized_percent']:.1f}%",
            help="Percentage of available ballast storage utilized"
        )
    
    with col4:
        overflow = perf['total_system_overflow_m3']
        st.metric(
            "System Overflow", 
            f"{overflow:.1f} m³" if overflow > 0.1 else "None",
            delta="System exceeded" if overflow > 0.1 else "Contained",
            delta_color="inverse" if overflow > 0.1 else "normal"
        )
    
    # Performance summary
    if perf['rail_formation_flooded']:
        st.error(f"⚠️ **Rail formation flooding detected:** Water rises {formation_flood:.2f}m above track level")
        st.info("💡 **Mitigation required:** Consider additional drainage, larger soakwells, or improved ballast drainage")
    else:
        st.success("✅ **No rail formation flooding:** System adequately manages design storm")
    
    # Time series plots
    st.subheader("System Performance Over Time")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
    
    time_hours = ballast_results['time_minutes'] / 60
    
    # Water levels
    ax1.plot(time_hours, ballast_results['water_level_AHD'], 'b-', linewidth=2, label='Water Level')
    ax1.axhline(y=ballast_results['analyzer'].soakwell_invert_level, color='k', linestyle='--', alpha=0.7, label='Soakwell Invert')
    formation_level = ballast_results['analyzer'].soakwell_invert_level + 1.0  # Approximate
    ax1.axhline(y=formation_level, color='r', linestyle='--', alpha=0.7, label='Formation Level')
    ax1.set_ylabel('Water Level (m AHD)')
    ax1.set_title('Water Level vs Time')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Storage volumes
    ax2.plot(time_hours, ballast_results['soakwell_volume'], 'g-', label='Soakwell Storage')
    ax2.plot(time_hours, ballast_results['ballast_volume'], 'orange', label='Ballast Storage')
    ax2.plot(time_hours, ballast_results['total_storage'], 'r-', linewidth=2, label='Total Storage')
    ax2.set_ylabel('Storage Volume (m³)')
    ax2.set_title('Storage Utilization')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Overflow rates
    ax3.plot(time_hours, ballast_results['overflow_to_ballast'], 'orange', label='Overflow to Ballast')
    ax3.plot(time_hours, ballast_results['overflow_from_system'], 'red', label='System Overflow')
    ax3.set_ylabel('Overflow Rate (m³/s)')
    ax3.set_xlabel('Time (hours)')
    ax3.set_title('Overflow Rates')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Stage-storage curve
    analyzer = ballast_results['analyzer']
    if analyzer.adjusted_stage_storage is not None:
        ax4.plot(analyzer.adjusted_stage_storage['Effective_Volume_m3'], 
                analyzer.adjusted_stage_storage['Height_Above_Soakwell_m'], 
                'b-o', label='Available Storage')
        ax4.axhline(y=0, color='k', linestyle='--', alpha=0.5, label='Soakwell Invert')
        max_used = perf['max_ballast_storage_m3']
        if max_used > 0:
            ax4.axvline(x=max_used, color='r', linestyle=':', alpha=0.7, label=f'Max Used ({max_used:.0f}m³)')
        ax4.set_xlabel('Effective Volume (m³)')
        ax4.set_ylabel('Height Above Soakwell (m)')
        ax4.set_title('Stage-Storage Relationship')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Data export option
    if st.button("📊 Export Ballast Analysis Data"):
        # Create comprehensive results DataFrame
        export_df = pd.DataFrame({
            'Time_minutes': ballast_results['time_minutes'],
            'Time_hours': ballast_results['time_minutes'] / 60,
            'Water_Level_AHD': ballast_results['water_level_AHD'],
            'Soakwell_Volume_m3': ballast_results['soakwell_volume'],
            'Ballast_Volume_m3': ballast_results['ballast_volume'],
            'Total_Storage_m3': ballast_results['total_storage'],
            'Overflow_to_Ballast_m3s': ballast_results['overflow_to_ballast'],
            'System_Overflow_m3s': ballast_results['overflow_from_system']
        })
        
        # Convert to CSV
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="Download Ballast Analysis Results (CSV)",
            data=csv,
            file_name=f"ballast_analysis_{storm_name.replace(' ', '_')}.csv",
            mime="text/csv"
        )

# Test function
def test_ballast_integration():
    """Test the ballast storage integration"""
    st.title("🧪 Ballast Storage Integration Test")
    
    # Test UI
    ballast_config = add_ballast_storage_ui()
    
    if ballast_config.get('enable_ballast', False):
        st.write("Ballast analysis enabled!")
        st.json(ballast_config)

if __name__ == "__main__":
    test_ballast_integration()
