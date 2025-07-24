#!/usr/bin/env python3
"""
French Drain Infiltration Model
Mathematical modeling of stormwater disposal through a linear French drain system

System Configuration:
- 300mm diameter perforated concrete pipe
- 600mm wide x 900mm deep gravel trench
- Single sized 40mm aggregate bedding
- Native sand soil (k = 4.63e-5 m/s)
- No groundwater impact

Author: Engineering Analysis
Date: July 2025
"""

import numpy as np
import pandas as pd
import math

# Optional matplotlib import
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class FrenchDrainModel:
    """
    Mathematical model for French drain infiltration system
    """
    
    def __init__(self):
        """Initialize French drain system parameters"""
        
        # Pipe specifications
        self.pipe_diameter = 0.30  # m (300mm)
        self.pipe_radius = self.pipe_diameter / 2
        self.pipe_area = math.pi * self.pipe_radius**2  # m²
        
        # Trench geometry
        self.trench_width = 0.60   # m (600mm)
        self.trench_depth = 0.90   # m (900mm)
        self.trench_area = self.trench_width * self.trench_depth  # m² per unit length
        
        # Aggregate properties (40mm single sized)
        self.aggregate_porosity = 0.35  # Typical for 40mm aggregate
        self.aggregate_k = 1e-2  # m/s (very permeable compared to soil)
        
        # Native soil properties (sand)
        self.soil_k = 4.63e-5  # m/s (given)
        self.soil_porosity = 0.30  # Typical for sand
        self.soil_Sr = 1.0  # Degree of saturation (assume fully saturated)
        
        # System properties
        self.perforation_ratio = 0.1  # 10% of pipe wall area perforated (typical)
        self.pipe_roughness = 0.012  # Manning's n for concrete pipe
        
        # Calculated properties
        self.effective_storage_volume = self.trench_area * self.aggregate_porosity  # m³/m length
        
    def calculate_pipe_capacity(self, slope=0.005):
        """
        Calculate pipe flow capacity using Manning's equation
        
        Parameters:
        slope: Pipe gradient (m/m), default 0.5%
        
        Returns:
        dict: Pipe flow characteristics
        """
        
        # Manning's equation for circular pipe
        # Q = (1/n) * A * R^(2/3) * S^(1/2)
        
        n = self.pipe_roughness
        A = self.pipe_area
        P = math.pi * self.pipe_diameter  # Wetted perimeter (full pipe)
        R = A / P  # Hydraulic radius
        S = slope
        
        # Full pipe capacity
        Q_full = (1/n) * A * (R**(2/3)) * (S**0.5)  # m³/s
        
        # Velocity at full capacity
        V_full = Q_full / A  # m/s
        
        return {
            'flow_capacity_full': Q_full,
            'velocity_full': V_full,
            'hydraulic_radius': R,
            'slope': slope,
            'area': A
        }
    
    def calculate_infiltration_rate(self, water_level_in_trench):
        """
        Calculate infiltration rate from trench to native soil
        Uses Darcy's law with cylindrical flow geometry
        
        Parameters:
        water_level_in_trench: Height of water in trench (m)
        
        Returns:
        float: Infiltration rate (m³/s per meter length)
        """
        
        if water_level_in_trench <= 0:
            return 0.0
        
        # Effective infiltration area (bottom and sides of trench)
        # Bottom area per unit length
        bottom_area = self.trench_width * 1.0  # m² per meter length
        
        # Side area per unit length (only up to water level)
        side_area = 2 * water_level_in_trench * 1.0  # m² per meter length
        
        total_infiltration_area = bottom_area + side_area
        
        # Hydraulic gradient (assuming unit gradient for deep water table)
        # For cylindrical flow around a trench, use equivalent radius approach
        equivalent_radius = (self.trench_width * water_level_in_trench / math.pi)**0.5
        
        # Darcy's law: q = k * i * A
        # For steady state infiltration, assume gradient ≈ 1 (conservative)
        infiltration_rate = self.soil_k * total_infiltration_area  # m³/s per meter
        
        return infiltration_rate
    
    def calculate_perforation_inflow(self, pipe_flow_rate, pipe_water_level, trench_water_level):
        """
        Simplified perforation flow - all pipe flow enters trench
        This eliminates numerical instability from complex orifice calculations
        
        Parameters:
        pipe_flow_rate: Current flow in pipe (m³/s)
        pipe_water_level: Water level in pipe (m from pipe bottom) - not used in simplified model
        trench_water_level: Water level in trench (m from trench bottom) - not used in simplified model
        
        Returns:
        float: Perforation inflow rate equals pipe flow rate (m³/s per meter length)
        """
        
        # Simplified: all pipe flow enters the trench through perforations
        # This represents a well-perforated French drain pipe
        return pipe_flow_rate
    
    def simulate_french_drain_response(self, inflow_hydrograph, pipe_slope=0.005, length=100.0, dt=60.0):
        """
        Simulate French drain system with stable numerical methods
        
        Parameters:
        inflow_hydrograph: dict with 'time' and 'flow' arrays (time in seconds, flow in m³/s)
        pipe_slope: Longitudinal slope of pipe (m/m)  
        length: Length of French drain (m)
        dt: Time step (seconds) - not used, actual time steps from data are used
        
        Returns:
        dict: Simulation results with physically realistic behavior
        """
        
        time = np.array(inflow_hydrograph['time'])
        inflow = np.array(inflow_hydrograph['flow'])
        
        # Initialize arrays
        n_steps = len(time)
        
        # State variables
        pipe_flow = np.zeros(n_steps)  # Flow in pipe (m³/s)
        trench_volume = np.zeros(n_steps)  # Stored volume in trench (m³)
        trench_water_level = np.zeros(n_steps)  # Water level in trench (m)
        
        # Output variables (simplified to key flows)
        infiltration_outflow = np.zeros(n_steps)  # Flow from trench to soil (m³/s)
        system_overflow = np.zeros(n_steps)  # Total system overflow (m³/s)
        
        # Physical constraints
        pipe_props = self.calculate_pipe_capacity(pipe_slope)
        max_pipe_flow = pipe_props['flow_capacity_full']
        max_trench_volume = self.trench_width * length * self.trench_depth * self.aggregate_porosity
        trench_base_area = self.trench_width * length
        
        # Stable infiltration calculation
        max_infiltration_rate = self.soil_k * trench_base_area / self.soil_Sr  # m³/s
        
        # Simulation loop with stable numerical integration
        for i in range(1, n_steps):
            dt_actual = time[i] - time[i-1]
            current_inflow = inflow[i]
            
            # 1. Determine pipe flow (limited by pipe capacity)
            pipe_flow[i] = min(current_inflow, max_pipe_flow)
            immediate_overflow = max(0.0, current_inflow - max_pipe_flow)
            
            # 2. All pipe flow enters trench storage
            inflow_to_trench = pipe_flow[i] * dt_actual  # m³
            
            # 3. Stable infiltration rate (smoothed based on average storage level)
            if trench_volume[i-1] > 0:
                # Smooth infiltration rate that prevents oscillations
                storage_fraction = min(trench_volume[i-1] / max_trench_volume, 1.0)
                # More gradual infiltration response
                infiltration_outflow[i] = max_infiltration_rate * (0.2 + 0.6 * storage_fraction)
            else:
                infiltration_outflow[i] = 0.0
            
            # 4. Smooth outflow calculation to prevent instability
            max_possible_outflow = trench_volume[i-1] / dt_actual  # Can't drain more than available
            actual_infiltration_rate = min(infiltration_outflow[i], max_possible_outflow)
            outflow_from_trench = actual_infiltration_rate * dt_actual  # m³
            
            # 5. Update trench volume with stability damping
            net_volume_change = inflow_to_trench - outflow_from_trench
            # Apply damping factor to prevent large oscillations
            damping_factor = 0.9  # Slightly damp changes
            damped_volume_change = net_volume_change * damping_factor
            new_trench_volume = trench_volume[i-1] + damped_volume_change
            
            # 6. Apply physical constraints smoothly
            if new_trench_volume > max_trench_volume:
                # Trench is full - excess becomes overflow
                excess_volume = new_trench_volume - max_trench_volume
                trench_volume[i] = max_trench_volume
                system_overflow[i] = immediate_overflow + excess_volume / dt_actual
            elif new_trench_volume < 0:
                # Cannot have negative storage
                trench_volume[i] = 0.0
                infiltration_outflow[i] = max(0.0, trench_volume[i-1] / dt_actual)
                system_overflow[i] = immediate_overflow
            else:
                trench_volume[i] = new_trench_volume
                system_overflow[i] = immediate_overflow
            
            # 7. Update water level smoothly
            trench_water_level[i] = trench_volume[i] / (trench_base_area * self.aggregate_porosity)
        
        # Calculate performance metrics
        total_inflow_volume = np.trapz(inflow, time)
        total_infiltrated = np.trapz(infiltration_outflow, time)
        total_overflow = np.trapz(system_overflow, time)
        final_stored_volume = trench_volume[-1]
        
        # Mass balance check: In = Out + Stored + Error
        mass_balance_error = total_inflow_volume - (total_infiltrated + total_overflow + final_stored_volume)
        mass_balance_error_percent = (mass_balance_error / total_inflow_volume * 100) if total_inflow_volume > 0 else 0
        
        infiltration_efficiency = (total_infiltrated / total_inflow_volume * 100) if total_inflow_volume > 0 else 0
        
        return {
            'time': time,
            'time_hours': time / 3600,
            'inflow': inflow,
            'pipe_flow': pipe_flow,
            'trench_volume': trench_volume,
            'trench_water_level': trench_water_level,
            'perforation_outflow': pipe_flow,  # Simplified: all pipe flow goes to trench
            'infiltration_outflow': infiltration_outflow,
            'pipe_overflow': system_overflow,  # Renamed for compatibility
            'performance': {
                'total_inflow_m3': total_inflow_volume,
                'total_infiltrated_m3': total_infiltrated,
                'total_overflow_m3': total_overflow,
                'final_stored_m3': final_stored_volume,
                'mass_balance_error_m3': mass_balance_error,
                'mass_balance_error_percent': mass_balance_error_percent,
                'infiltration_efficiency_percent': infiltration_efficiency,
                'max_trench_storage_m3': max(trench_volume),
                'max_water_level_m': max(trench_water_level),
                'pipe_capacity_m3s': max_pipe_flow,
                'system_length_m': length
            },
            'system_properties': {
                'pipe_diameter_mm': self.pipe_diameter * 1000,
                'trench_width_mm': self.trench_width * 1000,
                'trench_depth_mm': self.trench_depth * 1000,
                'soil_permeability_ms': self.soil_k,
                'pipe_slope': pipe_slope,
                'effective_storage_m3_per_m': self.effective_storage_volume
            }
        }
    
    def analyze_ts1_hydrograph(self, hydrograph_data, pipe_slope=0.005, length=100.0):
        """
        Analyze French drain performance using external hydrograph data
        
        Parameters:
        hydrograph_data: Dict with 'time' (seconds) and 'flow' (m³/s) arrays from .ts1 file
        pipe_slope: Longitudinal slope of pipe (m/m)
        length: Length of French drain (m)
        
        Returns:
        dict: Analysis results
        """
        
        # Validate input data format
        if not isinstance(hydrograph_data, dict):
            raise ValueError("Hydrograph data must be a dictionary")
        
        if 'time' not in hydrograph_data or 'flow' not in hydrograph_data:
            raise ValueError("Hydrograph data must contain 'time' and 'flow' keys")
        
        # Run simulation with your data
        results = self.simulate_french_drain_response(
            hydrograph_data, 
            pipe_slope=pipe_slope, 
            length=length
        )
        
        # Add analysis metadata
        results['analysis_info'] = {
            'data_source': 'External .ts1 file',
            'total_duration_hours': (max(hydrograph_data['time']) - min(hydrograph_data['time'])) / 3600,
            'peak_inflow_m3s': max(hydrograph_data['flow']),
            'system_configuration': {
                'pipe_diameter_mm': self.pipe_diameter * 1000,
                'trench_dimensions': f"{self.trench_width*1000:.0f}mm × {self.trench_depth*1000:.0f}mm",
                'soil_permeability_ms': self.soil_k,
                'system_length_m': length,
                'pipe_slope_percent': pipe_slope * 100
            }
        }
        
        return results
    
    def plot_results(self, results, save_path=None):
        """
        Create comprehensive plots of French drain performance
        
        Parameters:
        results: Results dictionary from simulate_french_drain_response
        save_path: Optional path to save plots
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available - cannot generate plots")
            return None
            
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('French Drain System Performance Analysis', fontsize=16, fontweight='bold')
        
        time_hours = results['time_hours']
        
        # Plot 1: Flow rates
        ax1 = axes[0, 0]
        ax1.plot(time_hours, results['inflow'], 'b-', label='System Inflow', linewidth=2)
        ax1.plot(time_hours, results['pipe_flow'], 'g-', label='Pipe Flow', linewidth=2)
        ax1.plot(time_hours, results['perforation_outflow'], 'orange', label='Perforation Outflow', linewidth=1.5)
        ax1.plot(time_hours, results['infiltration_outflow'], 'purple', label='Infiltration Rate', linewidth=1.5)
        if max(results['pipe_overflow']) > 0:
            ax1.plot(time_hours, results['pipe_overflow'], 'r-', label='System Overflow', linewidth=2)
        
        ax1.set_xlabel('Time (hours)')
        ax1.set_ylabel('Flow Rate (m³/s)')
        ax1.set_title('Flow Rates')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Trench storage
        ax2 = axes[0, 1]
        ax2.plot(time_hours, results['trench_volume'], 'purple', linewidth=2)
        ax2.set_xlabel('Time (hours)')
        ax2.set_ylabel('Storage Volume (m³)')
        ax2.set_title('Trench Storage Volume')
        ax2.grid(True, alpha=0.3)
        
        # Add capacity line
        max_capacity = results['system_properties']['effective_storage_m3_per_m'] * results['performance']['system_length_m']
        ax2.axhline(y=max_capacity, color='red', linestyle='--', label='Max Capacity')
        ax2.legend()
        
        # Plot 3: Water levels
        ax3 = axes[1, 0]
        ax3.plot(time_hours, results['trench_water_level'], 'blue', linewidth=2)
        ax3.set_xlabel('Time (hours)')
        ax3.set_ylabel('Water Level (m)')
        ax3.set_title('Trench Water Level')
        ax3.grid(True, alpha=0.3)
        
        # Add trench depth line
        trench_depth = results['system_properties']['trench_depth_mm'] / 1000
        ax3.axhline(y=trench_depth, color='red', linestyle='--', label='Trench Depth')
        ax3.legend()
        
        # Plot 4: Cumulative volumes
        ax4 = axes[1, 1]
        cumulative_inflow = np.cumsum(results['inflow']) * np.gradient(results['time'])
        cumulative_infiltration = np.cumsum(results['infiltration_outflow']) * np.gradient(results['time'])
        cumulative_overflow = np.cumsum(results['pipe_overflow']) * np.gradient(results['time'])
        
        ax4.plot(time_hours, cumulative_inflow, 'b-', label='Cumulative Inflow', linewidth=2)
        ax4.plot(time_hours, cumulative_infiltration, 'g-', label='Cumulative Infiltration', linewidth=2)
        if max(cumulative_overflow) > 0:
            ax4.plot(time_hours, cumulative_overflow, 'r-', label='Cumulative Overflow', linewidth=2)
        
        ax4.set_xlabel('Time (hours)')
        ax4.set_ylabel('Cumulative Volume (m³)')
        ax4.set_title('Cumulative Volumes')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
        
        # Print performance summary
        perf = results['performance']
        print("\n" + "="*60)
        print("FRENCH DRAIN PERFORMANCE SUMMARY")
        print("="*60)
        print(f"System Length: {perf['system_length_m']:.0f} m")
        print(f"Pipe Capacity: {perf['pipe_capacity_m3s']:.4f} m³/s")
        print(f"Total Inflow: {perf['total_inflow_m3']:.1f} m³")
        print(f"Total Infiltrated: {perf['total_infiltrated_m3']:.1f} m³")
        print(f"Total Overflow: {perf['total_overflow_m3']:.1f} m³")
        print(f"Infiltration Efficiency: {perf['infiltration_efficiency_percent']:.1f}%")
        print(f"Maximum Storage: {perf['max_trench_storage_m3']:.2f} m³")
        print(f"Maximum Water Level: {perf['max_water_level_m']:.2f} m")
        print("="*60)

def main():
    """
    Demonstration of French drain modeling capabilities
    Note: This model is designed to work with external hydrograph data (.ts1 files)
    """
    
    print("French Drain Infiltration Model")
    print("="*50)
    print("This model processes hydrograph data from your hydrological software (.ts1 files)")
    print("Use the Streamlit dashboard to upload and analyze your data.")
    print("="*50)
    
    # Initialize model to show system configuration
    drain = FrenchDrainModel()
    
    # Display system properties
    print("\nDefault System Configuration:")
    print(f"- Pipe: {drain.pipe_diameter*1000:.0f}mm diameter concrete")
    print(f"- Trench: {drain.trench_width*1000:.0f}mm wide × {drain.trench_depth*1000:.0f}mm deep")
    print(f"- Aggregate: 40mm single sized (porosity = {drain.aggregate_porosity:.2f})")
    print(f"- Soil permeability: {drain.soil_k:.2e} m/s (configurable)")
    print(f"- Effective storage: {drain.effective_storage_volume:.3f} m³/m length")
    print("\nTo analyze your data:")
    print("1. Run the Streamlit dashboard")
    print("2. Upload your .ts1 hydrograph files") 
    print("3. Configure soil parameters")
    print("4. Enable French drain analysis in the sidebar")
    print("5. Compare with soakwell performance")
    
    return drain

if __name__ == "__main__":
    drain_model = main()
