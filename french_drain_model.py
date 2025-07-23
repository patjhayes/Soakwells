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
        Calculate water flow from pipe to trench through perforations
        
        Parameters:
        pipe_flow_rate: Current flow in pipe (m³/s)
        pipe_water_level: Water level in pipe (m from pipe bottom)
        trench_water_level: Water level in trench (m from trench bottom)
        
        Returns:
        float: Perforation inflow rate (m³/s per meter length)
        """
        
        # Only flow out if pipe water level > trench water level
        if pipe_water_level <= trench_water_level:
            return 0.0
        
        # Head difference
        head_diff = pipe_water_level - trench_water_level
        
        # Perforation area per unit length (assume evenly distributed)
        pipe_circumference = math.pi * self.pipe_diameter
        perforation_area = pipe_circumference * self.perforation_ratio * 1.0  # m² per meter
        
        # Orifice flow equation: Q = Cd * A * sqrt(2*g*h)
        Cd = 0.6  # Discharge coefficient for sharp-edged orifices
        g = 9.81  # m/s²
        
        perforation_flow = Cd * perforation_area * math.sqrt(2 * g * head_diff)
        
        return perforation_flow
    
    def simulate_french_drain_response(self, inflow_hydrograph, pipe_slope=0.005, length=100.0, dt=60.0):
        """
        Simulate French drain system response to inflow hydrograph
        
        Parameters:
        inflow_hydrograph: dict with 'time' and 'flow' arrays (time in seconds, flow in m³/s)
        pipe_slope: Longitudinal slope of pipe (m/m)
        length: Length of French drain (m)
        dt: Time step (seconds)
        
        Returns:
        dict: Simulation results
        """
        
        time = np.array(inflow_hydrograph['time'])
        inflow = np.array(inflow_hydrograph['flow'])
        
        # Initialize arrays
        n_steps = len(time)
        
        # State variables
        pipe_flow = np.zeros(n_steps)  # Flow in pipe (m³/s)
        trench_volume = np.zeros(n_steps)  # Stored volume in trench (m³)
        trench_water_level = np.zeros(n_steps)  # Water level in trench (m)
        
        # Output variables
        perforation_outflow = np.zeros(n_steps)  # Flow from pipe to trench (m³/s)
        infiltration_outflow = np.zeros(n_steps)  # Flow from trench to soil (m³/s)
        pipe_overflow = np.zeros(n_steps)  # Overflow from pipe (m³/s)
        
        # Pipe characteristics
        pipe_props = self.calculate_pipe_capacity(pipe_slope)
        max_pipe_flow = pipe_props['flow_capacity_full']
        
        # Simulation loop
        for i in range(1, n_steps):
            dt_actual = time[i] - time[i-1]
            
            # Current inflow to system
            current_inflow = inflow[i]  # m³/s total inflow
            
            # French drain inflow strategy:
            # 1. Inflow enters trench directly (not pipe)
            # 2. Pipe serves as overflow/conveyance when trench is full
            # 3. Perforation flow is from trench to pipe (not pipe to trench)
            
            # Calculate current trench water level from previous timestep
            if trench_volume[i-1] > 0:
                trench_water_level[i-1] = min(
                    trench_volume[i-1] / (self.trench_width * length * self.aggregate_porosity),
                    self.trench_depth
                )
            else:
                trench_water_level[i-1] = 0.0
            
            # Infiltration from trench to native soil (always occurring if water present)
            infiltration_outflow[i] = self.calculate_infiltration_rate(
                trench_water_level[i-1]
            ) * length  # Scale by length
            
            # Direct inflow to trench (main French drain mechanism)
            direct_trench_inflow = current_inflow  # All inflow goes to trench initially
            
            # Check if trench has capacity for direct inflow
            max_trench_volume = self.trench_width * length * self.trench_depth * self.aggregate_porosity
            
            # Try to accommodate inflow in trench
            potential_volume = trench_volume[i-1] + (direct_trench_inflow - infiltration_outflow[i]) * dt_actual
            
            if potential_volume <= max_trench_volume:
                # Trench can handle all inflow
                trench_volume[i] = max(0.0, potential_volume)
                pipe_flow[i] = 0.0  # No pipe flow needed
                pipe_overflow[i] = 0.0
                perforation_outflow[i] = 0.0
                
            else:
                # Trench is full/overflowing - excess goes to pipe
                trench_volume[i] = max_trench_volume
                excess_flow = (potential_volume - max_trench_volume) / dt_actual
                
                # Pipe handles excess flow
                pipe_props = self.calculate_pipe_capacity(pipe_slope)
                max_pipe_flow = pipe_props['flow_capacity_full']
                
                if excess_flow <= max_pipe_flow:
                    pipe_flow[i] = excess_flow
                    pipe_overflow[i] = 0.0
                else:
                    pipe_flow[i] = max_pipe_flow
                    pipe_overflow[i] = excess_flow - max_pipe_flow
                
                # When pipe is active, some flow may be from trench to pipe
                perforation_outflow[i] = min(excess_flow, max_pipe_flow)
            
            # Update trench water level for this timestep
            trench_water_level[i] = min(
                trench_volume[i] / (self.trench_width * length * self.aggregate_porosity),
                self.trench_depth
            )
        
        # Calculate performance metrics
        total_inflow_volume = np.trapz(inflow, time)
        total_infiltrated = np.trapz(infiltration_outflow, time)
        total_overflow = np.trapz(pipe_overflow, time)
        
        infiltration_efficiency = (total_infiltrated / total_inflow_volume * 100) if total_inflow_volume > 0 else 0
        
        return {
            'time': time,
            'time_hours': time / 3600,
            'inflow': inflow,
            'pipe_flow': pipe_flow,
            'trench_volume': trench_volume,
            'trench_water_level': trench_water_level,
            'perforation_outflow': perforation_outflow,
            'infiltration_outflow': infiltration_outflow,
            'pipe_overflow': pipe_overflow,
            'performance': {
                'total_inflow_m3': total_inflow_volume,
                'total_infiltrated_m3': total_infiltrated,
                'total_overflow_m3': total_overflow,
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
    
    def create_design_storm(self, intensity_mm_hr=20, duration_hours=2, shape='triangular'):
        """
        Create a design storm hydrograph for testing
        
        Parameters:
        intensity_mm_hr: Peak rainfall intensity (mm/hr)
        duration_hours: Storm duration (hours)
        shape: Storm shape ('triangular', 'uniform', 'chicago')
        
        Returns:
        dict: Storm hydrograph
        """
        
        # More realistic catchment area per unit length of drain
        # For a French drain, assume contributing width of about 10-20m
        contributing_width_m = 15  # meters on each side of drain
        catchment_area_per_m = contributing_width_m * 1.0  # m² per meter of drain
        drain_length = 100  # Default length for calculations
        total_catchment_area_m2 = catchment_area_per_m * drain_length
        
        runoff_coefficient = 0.7  # More conservative for mixed surfaces
        
        # Time array (30-second intervals for better resolution)
        dt = 30  # seconds
        time = np.arange(0, duration_hours * 3600 + dt, dt)
        n_steps = len(time)
        
        # Convert intensity to flow rate
        peak_intensity_ms = intensity_mm_hr / (1000 * 3600)  # mm/hr to m/s
        peak_flow = peak_intensity_ms * total_catchment_area_m2 * runoff_coefficient  # m³/s
        
        # Create hydrograph shape
        if shape == 'triangular':
            # Triangular storm with peak at 40% of duration (more realistic)
            peak_time = duration_hours * 0.4 * 3600  # seconds
            flow = np.zeros(n_steps)
            
            for i, t in enumerate(time):
                if t <= peak_time:
                    # Rising limb
                    flow[i] = peak_flow * (t / peak_time)
                else:
                    # Falling limb (longer recession)
                    remaining_time = duration_hours * 3600 - peak_time
                    flow[i] = peak_flow * (1 - (t - peak_time) / remaining_time)
                flow[i] = max(0, flow[i])
                
        elif shape == 'uniform':
            # Uniform storm at 60% of peak (more realistic than 50%)
            flow = np.full(n_steps, peak_flow * 0.6)
            
        elif shape == 'chicago':
            # Improved Chicago storm distribution
            a = intensity_mm_hr  # mm/hr
            b = 15  # Storm parameter (minutes)
            r = 0.7  # Rainfall distribution parameter
            
            flow = np.zeros(n_steps)
            total_duration_min = duration_hours * 60
            
            for i, t in enumerate(time):
                t_min = t / 60  # Convert to minutes
                if t_min <= total_duration_min and t_min > 0:
                    # Chicago storm equation
                    intensity_mmhr = a * ((t_min + b) / (t_min + b))**(-r)
                    intensity_ms = intensity_mmhr / (1000 * 3600)
                    flow[i] = intensity_ms * total_catchment_area_m2 * runoff_coefficient
                else:
                    flow[i] = 0
        
        return {
            'time': time,
            'flow': flow,
            'peak_intensity_mm_hr': intensity_mm_hr,
            'duration_hours': duration_hours,
            'catchment_area_m2': total_catchment_area_m2,
            'runoff_coefficient': runoff_coefficient,
            'peak_flow_m3s': peak_flow,
            'contributing_width_m': contributing_width_m
        }
            'peak_flow_m3s': peak_flow,
            'contributing_width_m': contributing_width_m
        }
            
        elif shape == 'chicago':
            # Chicago storm distribution
            a = peak_intensity_ms * 60  # Convert to mm/min
            b = 10  # Storm parameter
            r = 0.67  # Rainfall distribution parameter
            
            flow = np.zeros(n_steps)
            total_duration_min = duration_hours * 60
            
            for i, t in enumerate(time):
                t_min = t / 60  # Convert to minutes
                if t_min <= total_duration_min:
                    # Chicago storm equation
                    intensity = a * ((t_min + b) ** (r - 1)) / (t_min + b) ** r
                    flow[i] = intensity / 1000 / 60 * catchment_area_m2 * runoff_coefficient  # Convert mm/min to m³/s
        
        return {
            'time': time,
            'flow': flow,
            'peak_intensity_mm_hr': intensity_mm_hr,
            'duration_hours': duration_hours,
            'catchment_area_m2': catchment_area_m2,
            'runoff_coefficient': runoff_coefficient
        }
    
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
    Demonstration of French drain modeling
    """
    
    print("French Drain Infiltration Model")
    print("="*50)
    
    # Initialize model
    drain = FrenchDrainModel()
    
    # Display system properties
    print("\nSystem Configuration:")
    print(f"- Pipe: {drain.pipe_diameter*1000:.0f}mm diameter concrete")
    print(f"- Trench: {drain.trench_width*1000:.0f}mm wide × {drain.trench_depth*1000:.0f}mm deep")
    print(f"- Aggregate: 40mm single sized (porosity = {drain.aggregate_porosity:.2f})")
    print(f"- Soil permeability: {drain.soil_k:.2e} m/s")
    print(f"- Effective storage: {drain.effective_storage_volume:.3f} m³/m length")
    
    # Create design storm
    print(f"\nGenerating design storm...")
    storm = drain.create_design_storm(
        intensity_mm_hr=25,  # 25mm/hr peak intensity
        duration_hours=2,    # 2-hour duration
        shape='triangular'   # Triangular distribution
    )
    
    print(f"Storm characteristics:")
    print(f"- Peak intensity: {storm['peak_intensity_mm_hr']} mm/hr")
    print(f"- Duration: {storm['duration_hours']} hours")
    print(f"- Catchment area: {storm['catchment_area_m2']} m²")
    print(f"- Runoff coefficient: {storm['runoff_coefficient']}")
    print(f"- Peak flow: {max(storm['flow']):.4f} m³/s")
    
    # Run simulation
    print(f"\nRunning French drain simulation...")
    results = drain.simulate_french_drain_response(
        storm, 
        pipe_slope=0.005,  # 0.5% gradient
        length=100.0       # 100m length
    )
    
    # Display results
    drain.plot_results(results)
    
    return drain, results

if __name__ == "__main__":
    drain_model, simulation_results = main()
