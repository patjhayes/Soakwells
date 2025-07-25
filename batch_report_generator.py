#!/usr/bin/env python3
"""
Batch Report Generator
Generates comprehensive engineering reports for multiple pre-defined configurations
"""

import os
import sys
from datetime import datetime

# Import the standalone report generator functions
try:
    from standalone_report_generator import (
        get_storm_files, load_storm_data, run_soakwell_analysis, 
        run_french_drain_analysis, save_report, IMPORTS_AVAILABLE
    )
    from lightweight_report_generator import generate_comprehensive_engineering_report_lightweight
except ImportError as e:
    # Try fallback
    try:
        from standalone_report_generator import (
            get_storm_files, load_storm_data, run_soakwell_analysis, 
            run_french_drain_analysis, save_report, IMPORTS_AVAILABLE
        )
        from comprehensive_report_generator import generate_comprehensive_engineering_report
        generate_comprehensive_engineering_report_lightweight = generate_comprehensive_engineering_report
    except ImportError as e2:
        print(f"Error importing required modules: {e}")
        sys.exit(1)

def get_standard_configurations():
    """Get a set of standard engineering configurations for comparison"""
    return [
        {
            'name': 'Standard Single 2m Soakwell',
            'soakwell_diameter': 2.0,
            'soakwell_depth': 2.0,
            'num_soakwells': 1,
            'ks': 4.63e-5,  # Perth sand
            'Sr': 1.0,
            'french_drain_length': 100.0,
            'french_drain_enabled': True
        },
        {
            'name': 'Multiple 1.5m Soakwells (3 units)',
            'soakwell_diameter': 1.5,
            'soakwell_depth': 1.8,
            'num_soakwells': 3,
            'ks': 4.63e-5,  # Perth sand
            'Sr': 1.0,
            'french_drain_length': 100.0,
            'french_drain_enabled': True
        },
        {
            'name': 'Large Single 2.5m Soakwell',
            'soakwell_diameter': 2.5,
            'soakwell_depth': 2.5,
            'num_soakwells': 1,
            'ks': 4.63e-5,  # Perth sand
            'Sr': 1.0,
            'french_drain_length': 100.0,
            'french_drain_enabled': True
        },
        {
            'name': 'Conservative Clay Soil Design',
            'soakwell_diameter': 3.0,
            'soakwell_depth': 3.0,
            'num_soakwells': 2,
            'ks': 1e-6,     # Clay soil (low permeability)
            'Sr': 1.0,
            'french_drain_length': 150.0,
            'french_drain_enabled': True
        }
    ]

def select_critical_storms(storm_files, max_storms=3):
    """Select the most critical storm files for analysis"""
    
    # Priority storm patterns (adjust based on your specific storms)
    priority_patterns = [
        '10% AEP, 1 hour burst',      # Short intense storm
        '10% AEP, 4.5 hour burst',    # Medium duration storm  
        '10% AEP, 24 hour burst',     # Long duration storm
        '10% AEP, 2 hour burst',      # Alternative medium storm
        '10% AEP, 6 hour burst'       # Alternative long storm
    ]
    
    selected_storms = []
    
    # Try to find storms matching priority patterns
    for pattern in priority_patterns:
        for storm_file in storm_files:
            if pattern in storm_file and storm_file not in selected_storms:
                selected_storms.append(storm_file)
                break
        if len(selected_storms) >= max_storms:
            break
    
    # If we don't have enough storms, add the first few available
    if len(selected_storms) < max_storms:
        for storm_file in storm_files:
            if storm_file not in selected_storms:
                selected_storms.append(storm_file)
                if len(selected_storms) >= max_storms:
                    break
    
    return selected_storms

def generate_batch_reports():
    """Generate reports for all standard configurations and critical storms"""
    
    print("🌧️ Batch Engineering Report Generator")
    print("=" * 50)
    
    if not IMPORTS_AVAILABLE:
        print("❌ Error: Required modules not available")
        return
    
    # Get storm files
    storm_files = get_storm_files()
    if not storm_files:
        print("❌ No storm files found in DRAINS directory")
        return
    
    print(f"📁 Found {len(storm_files)} storm files")
    
    # Select critical storms for analysis
    selected_storms = select_critical_storms(storm_files, max_storms=3)
    print(f"🎯 Selected {len(selected_storms)} critical storms for analysis:")
    for storm in selected_storms:
        print(f"   • {os.path.basename(storm)}")
    
    # Get standard configurations
    configurations = get_standard_configurations()
    print(f"⚙️  Analyzing {len(configurations)} standard configurations:")
    for config in configurations:
        print(f"   • {config['name']}")
    
    # Calculate total combinations
    total_combinations = len(selected_storms) * len(configurations)
    print(f"\n🔢 Total combinations to analyze: {total_combinations}")
    
    proceed = input("\nProceed with batch analysis? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Analysis cancelled")
        return
    
    # Create reports directory
    reports_dir = "batch_engineering_reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Generate reports
    current_combination = 0
    successful_reports = 0
    failed_reports = 0
    
    print(f"\n🚀 Starting batch analysis...")
    
    for config in configurations:
        print(f"\n📊 Configuration: {config['name']}")
        print("-" * 40)
        
        for storm_file in selected_storms:
            current_combination += 1
            storm_name = os.path.basename(storm_file).replace('.ts1', '')
            
            print(f"[{current_combination}/{total_combinations}] Processing: {storm_name}")
            
            try:
                # Load storm data
                hydrograph_data = load_storm_data(storm_file)
                if hydrograph_data is None:
                    print(f"   ❌ Failed to load storm data")
                    failed_reports += 1
                    continue
                
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
                soakwell_results = run_soakwell_analysis(analysis_hydrograph, config)
                if soakwell_results is None:
                    print(f"   ❌ Soakwell analysis failed")
                    failed_reports += 1
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
                            if key != 'mass_balance_error_percent':
                                mb[key] = mb[key] * config['num_soakwells']
                    
                    # Update max volume
                    soakwell_results['max_volume'] = soakwell_results['max_volume'] * config['num_soakwells']
                
                # Run French drain analysis
                french_drain_results = None
                if config['french_drain_enabled']:
                    french_drain_results = run_french_drain_analysis(hydrograph_data, config)
                
                # Generate comprehensive report
                html_report = generate_comprehensive_engineering_report_lightweight(
                    soakwell_results=soakwell_results,
                    french_drain_results=french_drain_results,
                    storm_name=storm_name,
                    config=config,
                    hydrograph_data=hydrograph_data
                )
                
                # Create custom filename for batch reports
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                config_safe = config['name'].replace(' ', '_').replace('(', '').replace(')', '').replace(',', '')
                storm_safe = storm_name.replace(' ', '_').replace(',', '').replace('%', 'pct')
                filename = f"{config_safe}_{storm_safe}_{timestamp}.html"
                filepath = os.path.join(reports_dir, filename)
                
                # Save report
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_report)
                
                print(f"   ✅ Report saved: {filename}")
                successful_reports += 1
                
                # Quick performance summary
                max_storage = max(soakwell_results['stored_volume'])
                mass_balance_error = soakwell_results['mass_balance']['mass_balance_error_percent']
                emptying_time = soakwell_results['emptying_time_minutes'] / 60
                
                print(f"      Max storage: {max_storage:.1f} m³, Error: {mass_balance_error:.3f}%, Emptying: {emptying_time:.1f}h")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                failed_reports += 1
                continue
    
    # Generate summary report
    summary_file = os.path.join(reports_dir, f"Batch_Analysis_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(summary_file, 'w') as f:
        f.write(f"Batch Engineering Report Analysis Summary\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"=" * 50 + "\n\n")
        f.write(f"Configurations Analyzed: {len(configurations)}\n")
        for config in configurations:
            f.write(f"  • {config['name']}\n")
        f.write(f"\nStorms Analyzed: {len(selected_storms)}\n")
        for storm in selected_storms:
            f.write(f"  • {os.path.basename(storm)}\n")
        f.write(f"\nResults:\n")
        f.write(f"  • Total combinations: {total_combinations}\n")
        f.write(f"  • Successful reports: {successful_reports}\n")
        f.write(f"  • Failed reports: {failed_reports}\n")
        f.write(f"  • Success rate: {successful_reports/total_combinations*100:.1f}%\n")
        f.write(f"\nAll reports saved in: {os.path.abspath(reports_dir)}\n")
    
    print(f"\n🎉 Batch analysis complete!")
    print(f"📊 Results: {successful_reports}/{total_combinations} successful reports")
    print(f"📁 Reports saved in: {os.path.abspath(reports_dir)}")
    print(f"📋 Summary saved: {summary_file}")

if __name__ == "__main__":
    try:
        generate_batch_reports()
    except KeyboardInterrupt:
        print("\n\n🛑 Batch analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
