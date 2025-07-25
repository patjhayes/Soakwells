#!/usr/bin/env python3
"""
Standalone Comprehensive Engineering Report Generator
Creates complete infiltration system analysis reports without requiring the dashboard environment
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime
import math

# Import necessary analysis functions
try:
    from core_soakwell_analysis import simulate_soakwell_performance, read_hydrograph_data_from_content, scale_multiple_soakwell_results
    from lightweight_report_generator import generate_comprehensive_engineering_report_lightweight
    IMPORTS_AVAILABLE = True
except ImportError as e:
    # Try fallback to the full comprehensive report generator
    try:
        from core_soakwell_analysis import simulate_soakwell_performance, read_hydrograph_data_from_content, scale_multiple_soakwell_results
        from comprehensive_report_generator import generate_comprehensive_engineering_report
        generate_comprehensive_engineering_report_lightweight = generate_comprehensive_engineering_report
        IMPORTS_AVAILABLE = True
    except ImportError as e2:
        print(f"Warning: Some imports failed: {e}")
        print("Please ensure all required modules are available")
        IMPORTS_AVAILABLE = False

def get_default_configuration():
    """Get default configuration for analysis"""
    return {
        'soakwell_diameter': 2.0,
        'soakwell_depth': 2.0,
        'num_soakwells': 1,
        'ks': 4.63e-5,  # Perth sand permeability
        'Sr': 1.0,
        'french_drain_length': 100.0,
        'french_drain_enabled': True
    }

def get_storm_files():
    """Get available storm files from DRAINS directory"""
    drains_dir = "DRAINS"
    if not os.path.exists(drains_dir):
        print(f"Warning: DRAINS directory not found at {drains_dir}")
        return []
    
    storm_files = []
    for file in os.listdir(drains_dir):
        if file.endswith('.ts1'):
            storm_files.append(os.path.join(drains_dir, file))
    
    return storm_files

def load_storm_data(storm_file):
    """Load storm data from .ts1 file"""
    try:
        with open(storm_file, 'r') as f:
            content = f.read()
        
        # Use the dashboard function to parse the content
        hydrograph_data = read_hydrograph_data_from_content(content)
        return hydrograph_data
    except Exception as e:
        print(f"Error loading storm file {storm_file}: {e}")
        return None

def run_soakwell_analysis(hydrograph_data, config):
    """Run soakwell analysis with extended duration"""
    try:
        result = simulate_soakwell_performance(
            hydrograph_data,
            diameter=config['soakwell_diameter'],
            ks=config['ks'],
            Sr=config['Sr'],
            max_height=config['soakwell_depth'],
            extend_to_hours=72  # Extended for emptying time analysis
        )
        
        # Add mass balance calculation
        total_inflow = result['cumulative_inflow'][-1]
        total_outflow = result['cumulative_outflow'][-1]
        total_overflow = sum(result['overflow_rate'][i] * 5 * 60 for i in range(len(result['overflow_rate'])))  # Convert to volume
        final_stored = result['stored_volume'][-1]
        
        mass_balance_error = total_inflow - (total_outflow + total_overflow + final_stored)
        mass_balance_error_percent = (mass_balance_error / total_inflow * 100) if total_inflow > 0 else 0
        
        result['mass_balance'] = {
            'total_inflow_m3': total_inflow,
            'total_outflow_m3': total_outflow,
            'total_overflow_m3': total_overflow,
            'final_stored_m3': final_stored,
            'mass_balance_error_m3': mass_balance_error,
            'mass_balance_error_percent': mass_balance_error_percent
        }
        
        # Calculate emptying time
        emptying_time = 0
        peak_volume = max(result['stored_volume'])
        peak_idx = result['stored_volume'].index(peak_volume)
        
        # Find when volume drops to 5% of peak after peak
        threshold = 0.05 * peak_volume
        for i in range(peak_idx, len(result['stored_volume'])):
            if result['stored_volume'][i] <= threshold:
                emptying_time = result['time_min'][i] - result['time_min'][peak_idx]
                break
        
        result['emptying_time_minutes'] = emptying_time
        
        return result
    except Exception as e:
        print(f"Error in soakwell analysis: {e}")
        return None

def run_french_drain_analysis(hydrograph_data, config):
    """Run French drain analysis with extended duration"""
    try:
        # Create a mock French drain configuration
        fd_config = {
            'pipe_diameter': 0.30,  # 300mm
            'trench_width': 0.60,   # 600mm
            'trench_depth': 0.90,   # 900mm
            'length': config['french_drain_length'],
            'soil_k': config['ks'],
            'pipe_slope': 0.005,    # 0.5%
            'aggregate_porosity': 0.35
        }
        
        # French drain analysis temporarily disabled
        print("French drain analysis currently disabled - focusing on soakwell analysis only")
        return None
    except Exception as e:
        print(f"Error in French drain analysis: {e}")
        return None

def select_design_storm(storm_files):
    """Interactive storm selection"""
    if not storm_files:
        print("No storm files found!")
        return None
    
    print("\nAvailable Storm Files:")
    print("=" * 50)
    
    for i, storm_file in enumerate(storm_files, 1):
        filename = os.path.basename(storm_file)
        print(f"{i:2d}. {filename}")
    
    while True:
        try:
            choice = input(f"\nSelect storm file (1-{len(storm_files)}), or 'all' for comprehensive analysis: ").strip()
            
            if choice.lower() == 'all':
                return storm_files
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(storm_files):
                return [storm_files[choice_num - 1]]
            else:
                print(f"Please enter a number between 1 and {len(storm_files)}")
        except ValueError:
            print("Please enter a valid number or 'all'")

def configure_analysis():
    """Interactive configuration setup"""
    print("\nAnalysis Configuration")
    print("=" * 30)
    
    config = get_default_configuration()
    
    # Display current configuration
    print("\nCurrent Configuration:")
    print(f"• Soakwell Diameter: {config['soakwell_diameter']:.1f} m")
    print(f"• Soakwell Depth: {config['soakwell_depth']:.1f} m")
    print(f"• Number of Soakwells: {config['num_soakwells']}")
    print(f"• Soil Permeability (ks): {config['ks']:.2e} m/s")
    print(f"• French Drain Length: {config['french_drain_length']:.0f} m")
    
    modify = input("\nModify configuration? (y/n): ").strip().lower()
    
    if modify == 'y':
        print("\nEnter new values (press Enter to keep current value):")
        
        # Soakwell diameter
        diameter_input = input(f"Soakwell Diameter [{config['soakwell_diameter']:.1f} m]: ").strip()
        if diameter_input:
            try:
                config['soakwell_diameter'] = float(diameter_input)
            except ValueError:
                print("Invalid input, using default")
        
        # Soakwell depth
        depth_input = input(f"Soakwell Depth [{config['soakwell_depth']:.1f} m]: ").strip()
        if depth_input:
            try:
                config['soakwell_depth'] = float(depth_input)
            except ValueError:
                print("Invalid input, using default")
        
        # Number of soakwells
        num_input = input(f"Number of Soakwells [{config['num_soakwells']}]: ").strip()
        if num_input:
            try:
                config['num_soakwells'] = int(num_input)
            except ValueError:
                print("Invalid input, using default")
        
        # Soil permeability
        ks_input = input(f"Soil Permeability (ks) [{config['ks']:.2e} m/s]: ").strip()
        if ks_input:
            try:
                config['ks'] = float(ks_input)
            except ValueError:
                print("Invalid input, using default")
        
        # French drain length
        length_input = input(f"French Drain Length [{config['french_drain_length']:.0f} m]: ").strip()
        if length_input:
            try:
                config['french_drain_length'] = float(length_input)
            except ValueError:
                print("Invalid input, using default")
    
    return config

def save_report(html_content, storm_name, config):
    """Save the HTML report to file"""
    # Create reports directory if it doesn't exist
    reports_dir = "engineering_reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    storm_safe = storm_name.replace(' ', '_').replace(',', '').replace('%', 'pct')
    filename = f"Infiltration_Analysis_{storm_safe}_{timestamp}.html"
    filepath = os.path.join(reports_dir, filename)
    
    # Save the file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Report saved: {filepath}")
    print(f"📁 Report directory: {os.path.abspath(reports_dir)}")
    
    # Also save a summary
    summary_file = os.path.join(reports_dir, f"Analysis_Summary_{timestamp}.txt")
    with open(summary_file, 'w') as f:
        f.write(f"Infiltration System Analysis Summary\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Storm: {storm_name}\n\n")
        f.write(f"Configuration:\n")
        for key, value in config.items():
            f.write(f"  {key}: {value}\n")
        f.write(f"\nFull report: {filename}\n")
    
    return filepath

def main():
    """Main execution function"""
    print("🌧️ Standalone Engineering Report Generator")
    print("=" * 50)
    
    if not IMPORTS_AVAILABLE:
        print("❌ Error: Required modules not available")
        print("Please ensure the dashboard and analysis modules are installed")
        return
    
    # Get storm files
    storm_files = get_storm_files()
    if not storm_files:
        print("❌ No storm files found in DRAINS directory")
        return
    
    # Select storm(s) to analyze
    selected_storms = select_design_storm(storm_files)
    if not selected_storms:
        print("❌ No storm selected")
        return
    
    # Configure analysis
    config = configure_analysis()
    
    print(f"\n🔧 Starting analysis of {len(selected_storms)} storm(s)...")
    
    # Process each storm
    for storm_file in selected_storms:
        storm_name = os.path.basename(storm_file).replace('.ts1', '')
        print(f"\n📊 Analyzing: {storm_name}")
        
        # Load storm data
        hydrograph_data = load_storm_data(storm_file)
        if hydrograph_data is None:
            print(f"❌ Failed to load storm data: {storm_file}")
            continue
        
        print(f"   ✅ Loaded {len(hydrograph_data['time_min'])} data points")
        
        # Scale hydrograph for multiple soakwells if needed
        if config['num_soakwells'] > 1:
            scaled_hydrograph = {
                'time_min': hydrograph_data['time_min'],
                'total_flow': [flow / config['num_soakwells'] for flow in hydrograph_data['total_flow']],
                'cat1240_flow': hydrograph_data.get('cat1240_flow', [flow / config['num_soakwells'] for flow in hydrograph_data['total_flow']]),
                'cat3_flow': hydrograph_data.get('cat3_flow', [0.0] * len(hydrograph_data['total_flow']))
            }
            analysis_hydrograph = scaled_hydrograph
        else:
            analysis_hydrograph = hydrograph_data
        
        # Run soakwell analysis
        print("   🔄 Running soakwell analysis...")
        soakwell_results = run_soakwell_analysis(analysis_hydrograph, config)
        if soakwell_results is None:
            print("   ❌ Soakwell analysis failed")
            continue
        
        # Scale results back for multiple soakwells
        if config['num_soakwells'] > 1:
            # Scale volume-related results
            for key in ['stored_volume', 'cumulative_inflow', 'cumulative_outflow']:
                if key in soakwell_results:
                    soakwell_results[key] = [v * config['num_soakwells'] for v in soakwell_results[key]]
            
            # Scale flow rates
            for key in ['inflow_rate', 'outflow_rate', 'overflow_rate']:
                if key in soakwell_results:
                    soakwell_results[key] = [v * config['num_soakwells'] for v in soakwell_results[key]]
            
            # Update mass balance
            if 'mass_balance' in soakwell_results:
                mb = soakwell_results['mass_balance']
                for key in mb:
                    if key != 'mass_balance_error_percent':  # Keep percentage as is
                        mb[key] = mb[key] * config['num_soakwells']
            
            # Update max volume
            soakwell_results['max_volume'] = soakwell_results['max_volume'] * config['num_soakwells']
        
        print(f"   ✅ Soakwell analysis complete")
        print(f"      - Max storage: {max(soakwell_results['stored_volume']):.1f} m³")
        print(f"      - Mass balance error: {soakwell_results['mass_balance']['mass_balance_error_percent']:.3f}%")
        print(f"      - Emptying time: {soakwell_results['emptying_time_minutes']/60:.1f} hours")
        
        # Run French drain analysis
        french_drain_results = None
        if config['french_drain_enabled']:
            print("   🔄 Running French drain analysis...")
            french_drain_results = run_french_drain_analysis(hydrograph_data, config)
            if french_drain_results:
                print(f"   ✅ French drain analysis complete")
                perf = french_drain_results.get('performance', {})
                print(f"      - Max storage: {perf.get('max_trench_storage_m3', 0):.1f} m³")
                print(f"      - Infiltration efficiency: {perf.get('infiltration_efficiency_percent', 0):.1f}%")
            else:
                print("   ⚠️  French drain analysis failed, proceeding with soakwell only")
        
        # Generate comprehensive report
        print("   📝 Generating comprehensive report...")
        try:
            html_report = generate_comprehensive_engineering_report_lightweight(
                soakwell_results=soakwell_results,
                french_drain_results=french_drain_results,
                storm_name=storm_name,
                config=config,
                hydrograph_data=hydrograph_data
            )
            
            # Save report
            report_path = save_report(html_report, storm_name, config)
            print(f"   ✅ Report generated successfully")
            
        except Exception as e:
            print(f"   ❌ Report generation failed: {e}")
            continue
    
    print(f"\n🎉 Analysis complete!")
    print(f"📁 Check the 'engineering_reports' directory for all generated reports")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
