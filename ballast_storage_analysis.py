"""
Ballast Storage Analysis Module
Handles overflow from soakwells into rail formation ballast storage
Integrates 12D stage-storage relationships with soakwell hydraulic modeling
"""

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
from scipy import interpolate
import os

class BallastStorageAnalyzer:
    """
    Analyzes soakwell overflow into rail formation ballast storage using 12D stage-storage data
    """
    
    def __init__(self):
        self.stage_storage_data = None
        self.adjusted_stage_storage = None
        self.soakwell_invert_level = None
        self.ballast_void_ratio = 0.75  # Default for clean rail ballast
        self.effective_porosity = self.ballast_void_ratio / (1 + self.ballast_void_ratio)
        
    def parse_12d_stage_storage_html(self, html_file_path: str) -> pd.DataFrame:
        """
        Parse 12D Formation_Storage_Volumes.html file to extract stage-storage relationship
        
        Parameters:
        html_file_path: Path to 12D HTML output file
        
        Returns:
        DataFrame with columns: Height_m, Volume_m3, Area_m2
        """
        try:
            with open(html_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find the table containing stage-storage data
            tables = soup.find_all('table')
            
            stage_storage_table = None
            for table in tables:
                # Look for table headers that indicate stage-storage data
                headers = table.find_all('th')
                header_text = [th.get_text().strip().lower() for th in headers]
                
                if any('height' in h or 'level' in h or 'elevation' in h for h in header_text) and \
                   any('volume' in h or 'storage' in h for h in header_text):
                    stage_storage_table = table
                    break
            
            if not stage_storage_table:
                raise ValueError("Could not find stage-storage table in HTML file")
            
            # Extract data from table
            rows = stage_storage_table.find_all('tr')
            headers = [th.get_text().strip() for th in rows[0].find_all(['th', 'td'])]
            
            data = []
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:  # Need at least height and volume
                    row_data = []
                    for cell in cells:
                        text = cell.get_text().strip()
                        # Try to convert to float, handle various number formats
                        try:
                            # Remove commas and convert to float
                            value = float(text.replace(',', '').replace(' ', ''))
                            row_data.append(value)
                        except ValueError:
                            # If conversion fails, keep as string
                            row_data.append(text)
                    
                    if len(row_data) >= 2 and all(isinstance(x, (int, float)) for x in row_data[:2]):
                        data.append(row_data)
            
            # Create DataFrame
            df_columns = ['Height_m', 'Volume_m3']
            if len(data[0]) > 2:
                df_columns.append('Area_m2')
            
            df = pd.DataFrame(data, columns=df_columns[:len(data[0])])
            
            # Sort by height to ensure proper interpolation
            df = df.sort_values('Height_m').reset_index(drop=True)
            
            print(f"✅ Successfully parsed {len(df)} stage-storage points from 12D HTML file")
            print(f"Height range: {df['Height_m'].min():.2f} to {df['Height_m'].max():.2f} m")
            print(f"Volume range: {df['Volume_m3'].min():.1f} to {df['Volume_m3'].max():.1f} m³")
            
            self.stage_storage_data = df
            return df
            
        except Exception as e:
            print(f"❌ Error parsing 12D HTML file: {str(e)}")
            raise
    
    def adjust_datum_to_soakwell(self, soakwell_invert_level: float, 
                                formation_level: float = None) -> pd.DataFrame:
        """
        Adjust the 12D stage-storage height datum to match soakwell invert level
        
        Parameters:
        soakwell_invert_level: Bottom level of soakwell (m AHD)
        formation_level: Rail formation level (m AHD), if None will estimate from data
        
        Returns:
        Adjusted DataFrame with heights relative to soakwell invert
        """
        if self.stage_storage_data is None:
            raise ValueError("Must parse stage-storage data first")
        
        self.soakwell_invert_level = soakwell_invert_level
        
        # If formation level not provided, use the minimum height from 12D data
        if formation_level is None:
            formation_level = self.stage_storage_data['Height_m'].min()
            print(f"ℹ️  Using formation level from 12D data: {formation_level:.2f} m")
        
        # Calculate height adjustment
        height_adjustment = soakwell_invert_level - formation_level
        
        # Adjust heights
        adjusted_df = self.stage_storage_data.copy()
        adjusted_df['Height_Adjusted_m'] = adjusted_df['Height_m'] + height_adjustment
        adjusted_df['Height_Above_Soakwell_m'] = adjusted_df['Height_Adjusted_m'] - soakwell_invert_level
        
        # Apply ballast void ratio to volumes
        adjusted_df['Effective_Volume_m3'] = adjusted_df['Volume_m3'] * self.effective_porosity
        
        print(f"✅ Adjusted datum by {height_adjustment:.2f} m")
        print(f"📊 Effective storage (accounting for {self.effective_porosity:.1%} porosity):")
        print(f"   Maximum effective volume: {adjusted_df['Effective_Volume_m3'].max():.1f} m³")
        
        self.adjusted_stage_storage = adjusted_df
        return adjusted_df
    
    def create_storage_interpolator(self) -> interpolate.interp1d:
        """
        Create interpolation function for stage-storage relationship
        
        Returns:
        Scipy interpolation function: height_above_soakwell -> effective_volume
        """
        if self.adjusted_stage_storage is None:
            raise ValueError("Must adjust datum first")
        
        heights = self.adjusted_stage_storage['Height_Above_Soakwell_m'].values
        volumes = self.adjusted_stage_storage['Effective_Volume_m3'].values
        
        # Create interpolator with extrapolation for safety
        interpolator = interpolate.interp1d(heights, volumes, 
                                          kind='linear', 
                                          bounds_error=False, 
                                          fill_value=(0, volumes[-1]))
        
        return interpolator
    
    def analyze_soakwell_ballast_system(self, soakwell_results: Dict, 
                                      hydrograph_data: pd.DataFrame,
                                      soakwell_config: Dict) -> Dict:
        """
        Analyze combined soakwell + ballast storage system performance
        
        Parameters:
        soakwell_results: Standard soakwell analysis results
        hydrograph_data: Storm hydrograph (.ts1 format)
        soakwell_config: Soakwell configuration parameters
        
        Returns:
        Combined system analysis results
        """
        if self.adjusted_stage_storage is None:
            raise ValueError("Must set up stage-storage relationship first")
        
        # Extract soakwell parameters
        soakwell_capacity = soakwell_config.get('soakwell_diameter', 2.0)**2 * np.pi/4 * soakwell_config.get('soakwell_depth', 2.0)
        soakwell_top_level = self.soakwell_invert_level + soakwell_config.get('soakwell_depth', 2.0)
        
        # Get storage interpolator
        storage_interpolator = self.create_storage_interpolator()
        
        # Initialize tracking arrays
        time_steps = len(hydrograph_data)
        dt_seconds = 300  # 5-minute time steps
        
        # System state variables
        soakwell_volume = np.zeros(time_steps)
        ballast_volume = np.zeros(time_steps)
        total_storage = np.zeros(time_steps)
        water_level = np.zeros(time_steps)
        overflow_to_ballast = np.zeros(time_steps)
        overflow_from_system = np.zeros(time_steps)
        
        # Get inflow data
        if hasattr(hydrograph_data, 'iloc'):
            inflow_rates = hydrograph_data.iloc[:, 1].values  # m³/s
        else:
            inflow_rates = np.array(hydrograph_data)
        
        # Simulation parameters
        ks = soakwell_config.get('ks', 1e-5)  # Soil permeability
        soakwell_area = np.pi * (soakwell_config.get('soakwell_diameter', 2.0)/2)**2
        
        # Run time-step simulation
        for i in range(time_steps):
            # Inflow volume for this time step
            inflow_volume = inflow_rates[i] * dt_seconds if i < len(inflow_rates) else 0
            
            # Previous state
            prev_soakwell_vol = soakwell_volume[i-1] if i > 0 else 0
            prev_ballast_vol = ballast_volume[i-1] if i > 0 else 0
            
            # Calculate infiltration from soakwell
            if prev_soakwell_vol > 0:
                water_depth = prev_soakwell_vol / soakwell_area
                infiltration_rate = ks * soakwell_area * 2  # Base + sides approximation
                infiltration_volume = min(infiltration_rate * dt_seconds, prev_soakwell_vol)
            else:
                infiltration_volume = 0
            
            # Update soakwell volume
            new_soakwell_vol = prev_soakwell_vol + inflow_volume - infiltration_volume
            
            # Check for soakwell overflow
            if new_soakwell_vol > soakwell_capacity:
                overflow_vol = new_soakwell_vol - soakwell_capacity
                new_soakwell_vol = soakwell_capacity
                
                # Add overflow to ballast storage
                new_ballast_vol = prev_ballast_vol + overflow_vol
                overflow_to_ballast[i] = overflow_vol
            else:
                new_ballast_vol = prev_ballast_vol
                overflow_to_ballast[i] = 0
            
            # Calculate water level in system
            soakwell_level = new_soakwell_vol / soakwell_area
            
            if new_ballast_vol > 0:
                # Find height in ballast storage using interpolation
                try:
                    # Solve for height: storage_interpolator(height) = new_ballast_vol
                    heights = self.adjusted_stage_storage['Height_Above_Soakwell_m'].values
                    volumes = self.adjusted_stage_storage['Effective_Volume_m3'].values
                    
                    if new_ballast_vol <= volumes[-1]:
                        ballast_height = np.interp(new_ballast_vol, volumes, heights)
                    else:
                        # Extrapolate beyond available data
                        ballast_height = heights[-1]
                        overflow_from_system[i] = new_ballast_vol - volumes[-1]
                        new_ballast_vol = volumes[-1]
                    
                    water_level[i] = self.soakwell_invert_level + max(soakwell_level, ballast_height)
                except:
                    water_level[i] = self.soakwell_invert_level + soakwell_level
            else:
                water_level[i] = self.soakwell_invert_level + soakwell_level
            
            # Store results
            soakwell_volume[i] = new_soakwell_vol
            ballast_volume[i] = new_ballast_vol
            total_storage[i] = new_soakwell_vol + new_ballast_vol
        
        # Calculate performance metrics
        max_water_level = np.max(water_level)
        max_ballast_storage = np.max(ballast_volume)
        total_overflow = np.sum(overflow_from_system) * dt_seconds / 60  # Convert to m³
        max_height_above_formation = max_water_level - (self.soakwell_invert_level + soakwell_config.get('soakwell_depth', 2.0))
        
        results = {
            'time_minutes': np.arange(time_steps) * dt_seconds / 60,
            'soakwell_volume': soakwell_volume,
            'ballast_volume': ballast_volume,
            'total_storage': total_storage,
            'water_level_AHD': water_level,
            'overflow_to_ballast': overflow_to_ballast,
            'overflow_from_system': overflow_from_system,
            'performance': {
                'max_water_level_AHD': max_water_level,
                'max_water_level_above_invert': max_water_level - self.soakwell_invert_level,
                'max_height_above_formation': max_height_above_formation,
                'max_ballast_storage_m3': max_ballast_storage,
                'total_system_overflow_m3': total_overflow,
                'ballast_storage_utilized_percent': (max_ballast_storage / self.adjusted_stage_storage['Effective_Volume_m3'].max()) * 100,
                'rail_formation_flooded': max_height_above_formation > 0
            }
        }
        
        return results
    
    def plot_stage_storage_curve(self, save_path: str = None):
        """Plot the stage-storage relationship"""
        if self.adjusted_stage_storage is None:
            raise ValueError("Must adjust datum first")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Original 12D data
        ax1.plot(self.stage_storage_data['Volume_m3'], self.stage_storage_data['Height_m'], 
                'b-o', label='Original 12D Data')
        ax1.set_xlabel('Volume (m³)')
        ax1.set_ylabel('Height (m AHD)')
        ax1.set_title('Original 12D Stage-Storage')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Adjusted data with ballast porosity
        ax2.plot(self.adjusted_stage_storage['Effective_Volume_m3'], 
                self.adjusted_stage_storage['Height_Above_Soakwell_m'], 
                'r-o', label=f'Effective Storage ({self.effective_porosity:.1%} porosity)')
        ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5, label='Soakwell Invert')
        ax2.set_xlabel('Effective Volume (m³)')
        ax2.set_ylabel('Height Above Soakwell Invert (m)')
        ax2.set_title('Adjusted Stage-Storage for Ballast')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Stage-storage plot saved to: {save_path}")
        
        return fig
    
    def generate_ballast_analysis_report(self, results: Dict, storm_name: str) -> str:
        """
        Generate HTML report section for ballast storage analysis
        """
        perf = results['performance']
        
        report_html = f"""
        <div class="section">
            <div class="section-title">BALLAST STORAGE ANALYSIS</div>
            
            <div class="subsection-title">System Configuration</div>
            <p>This analysis models soakwell overflow into the void space of rail formation ballast, 
            providing additional flood storage during extreme events.</p>
            
            <table class="parameter-table">
                <tr><th>Parameter</th><th>Value</th><th>Unit</th><th>Notes</th></tr>
                <tr><td>Ballast Void Ratio</td><td>{self.ballast_void_ratio:.2f}</td><td>-</td><td>Clean rail ballast</td></tr>
                <tr><td>Effective Porosity</td><td>{self.effective_porosity:.1%}</td><td>-</td><td>Available for water storage</td></tr>
                <tr><td>Soakwell Invert Level</td><td>{self.soakwell_invert_level:.2f}</td><td>m AHD</td><td>Bottom of soakwell</td></tr>
                <tr><td>Max Available Ballast Storage</td><td>{self.adjusted_stage_storage['Effective_Volume_m3'].max():.1f}</td><td>m³</td><td>From 12D analysis</td></tr>
            </table>
            
            <div class="subsection-title">Performance Results - {storm_name}</div>
            <div class="result-box">
                <table class="parameter-table">
                    <tr><th>Performance Metric</th><th>Value</th><th>Assessment</th></tr>
                    <tr><td>Maximum Water Level</td><td>{perf['max_water_level_AHD']:.2f} m AHD</td><td>Peak flood level</td></tr>
                    <tr><td>Height Above Soakwell Invert</td><td>{perf['max_water_level_above_invert']:.2f} m</td><td>Total system head</td></tr>
                    <tr><td>Height Above Formation</td><td>{perf['max_height_above_formation']:.2f} m</td><td>{'⚠️ Formation flooding' if perf['rail_formation_flooded'] else '✅ No formation flood'}</td></tr>
                    <tr><td>Maximum Ballast Storage Used</td><td>{perf['max_ballast_storage_m3']:.1f} m³</td><td>{perf['ballast_storage_utilized_percent']:.1f}% of available</td></tr>
                    <tr><td>System Overflow</td><td>{perf['total_system_overflow_m3']:.1f} m³</td><td>{'❌ System exceeded' if perf['total_system_overflow_m3'] > 0.1 else '✅ Contained'}</td></tr>
                </table>
            </div>
            
            <div class="subsection-title">Design Implications</div>
            <ul>
                <li><strong>Flood Management:</strong> {'Rail formation experiences flooding up to ' + f"{perf['max_height_above_formation']:.2f}m above track level" if perf['rail_formation_flooded'] else 'No flooding of rail formation during design event'}</li>
                <li><strong>Ballast Utilization:</strong> Ballast storage provides {perf['ballast_storage_utilized_percent']:.1f}% additional capacity</li>
                <li><strong>System Adequacy:</strong> {'System overflow indicates need for additional drainage measures' if perf['total_system_overflow_m3'] > 0.1 else 'Combined system adequately manages design storm'}</li>
                <li><strong>Maintenance:</strong> Post-flood ballast cleaning and tamping will be required if formation flooding occurs</li>
            </ul>
        </div>
        """
        
        return report_html


def test_ballast_analyzer():
    """Test function for ballast storage analyzer"""
    # Create test instance
    analyzer = BallastStorageAnalyzer()
    
    # Create sample 12D-style stage-storage data for testing
    test_data = pd.DataFrame({
        'Height_m': [10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0],
        'Volume_m3': [0, 150, 350, 600, 900, 1250, 1650],
        'Area_m2': [300, 300, 300, 300, 300, 300, 300]
    })
    
    print("🧪 Testing Ballast Storage Analyzer")
    print(f"Test data: {len(test_data)} stage-storage points")
    
    # Simulate the parsing step
    analyzer.stage_storage_data = test_data
    
    # Adjust datum
    adjusted_data = analyzer.adjust_datum_to_soakwell(soakwell_invert_level=9.5)
    print(f"✅ Datum adjustment complete")
    
    # Test interpolator
    interpolator = analyzer.create_storage_interpolator()
    test_height = 1.0  # 1m above soakwell
    test_volume = interpolator(test_height)
    print(f"✅ Interpolator test: {test_height}m height → {test_volume:.1f}m³ storage")
    
    return analyzer

if __name__ == "__main__":
    test_ballast_analyzer()
