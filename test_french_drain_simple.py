import numpy as np
import matplotlib.pyplot as plt
from french_drain_model import FrenchDrainModel

# Create a simple test hydrograph
time = np.linspace(0, 7200, 121)  # 2 hours in 60-second intervals
peak_flow = 0.01  # m³/s
flow = peak_flow * np.exp(-(time-1800)**2 / (2*600**2))  # Gaussian peak at 30 min

# Create hydrograph dictionary
hydrograph = {
    'time': time,
    'flow': flow
}

# Create French drain system (uses default parameters: 300mm pipe, 600x900mm trench, sand k=4.63e-5)
french_drain = FrenchDrainModel()

print("Testing French drain model...")
print(f"Peak inflow: {max(flow):.4f} m³/s")

# Run simulation
results = french_drain.simulate_french_drain_response(
    hydrograph, 
    pipe_slope=0.005, 
    length=100.0
)

print("\nSimulation Results:")
print(f"Max trench storage: {results['performance']['max_trench_storage_m3']:.2f} m³")
print(f"Max water level: {results['performance']['max_water_level_m']:.3f} m")
print(f"Infiltration efficiency: {results['performance']['infiltration_efficiency_percent']:.1f}%")
print(f"Total inflow: {results['performance']['total_inflow_m3']:.2f} m³")
print(f"Total infiltrated: {results['performance']['total_infiltrated_m3']:.2f} m³")

# Check if results are physically reasonable
storage = results['trench_volume']
water_level = results['trench_water_level']
infiltration = results['infiltration_outflow']

print(f"\nPhysical checks:")
print(f"Storage varies smoothly: {np.all(np.diff(storage) < 1.0)}")  # No sudden jumps > 1 m³
print(f"Water level is stable: {max(water_level) < 1.0}")  # Under 1m depth
print(f"Infiltration is reasonable: {max(infiltration) < 0.02}")  # Under 0.02 m³/s

# Check for erratic behavior
storage_diff = np.diff(storage[storage > 0])
if len(storage_diff) > 0:
    print(f"Max storage change: {max(abs(storage_diff)):.4f} m³")
    print(f"Erratic behavior (large changes): {np.any(abs(storage_diff) > 0.5)}")

print("\nTest completed successfully!")
