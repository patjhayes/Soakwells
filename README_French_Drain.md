# French Drain Integration for Soakwell Dashboard

## Overview

This integration adds French drain modeling capabilities to your existing soakwell analysis dashboard. It allows you to compare the performance of traditional soakwell systems with linear French drain infiltration systems using the same hydrograph data.

## Mathematical Model

The French drain model simulates:

### 1. System Geometry
- **Pipe**: 300mm diameter perforated concrete pipe (configurable)
- **Trench**: 600mm wide × 900mm deep gravel-filled trench (configurable)
- **Aggregate**: Single-sized 40mm aggregate with 35% porosity
- **Length**: User-configurable system length (typically 50-200m)

### 2. Hydraulic Analysis
- **Pipe Flow**: Manning's equation for flow capacity
- **Perforation Flow**: Orifice equation for water transfer from pipe to gravel
- **Infiltration**: Darcy's law for seepage into native soil
- **Storage**: Volume balance in aggregate-filled trench

### 3. Key Equations

**Pipe Capacity (Manning's Equation):**
```
Q = (1/n) × A × R^(2/3) × S^(1/2)
```
Where:
- Q = Flow capacity (m³/s)
- n = Manning's roughness coefficient (0.012 for concrete)
- A = Pipe cross-sectional area (m²)
- R = Hydraulic radius (m)
- S = Pipe slope (m/m)

**Infiltration Rate (Darcy's Law):**
```
q = k × i × A
```
Where:
- q = Infiltration rate (m³/s)
- k = Soil hydraulic conductivity (m/s)
- i = Hydraulic gradient (assumed ≈ 1.0)
- A = Infiltration area (bottom + sides of trench)

**Perforation Flow (Orifice Equation):**
```
Q = Cd × A × √(2gh)
```
Where:
- Cd = Discharge coefficient (0.6)
- A = Perforation area (m²)
- g = Gravitational acceleration (9.81 m/s²)
- h = Head difference between pipe and trench (m)

## Files Structure

### Core Files
- `french_drain_model.py` - Main mathematical model and simulation engine
- `french_drain_integration.py` - Dashboard integration and UI components
- `french_drain_demo.py` - Standalone demonstration script

### Integration Points
- Added to `soakwell_dashboard.py` for seamless comparison
- Uses existing hydrograph data (.ts1 files)
- Shares soil parameters (hydraulic conductivity, moderation factor)

## Usage Instructions

### 1. Basic Usage
1. Upload your .ts1 hydrograph files as usual
2. Set soakwell parameters (soil conditions will be shared)
3. Enable "French Drain Analysis" in the sidebar
4. Configure French drain parameters:
   - Pipe diameter (225-450mm)
   - Pipe slope (0.3-2.0%)
   - Trench dimensions
   - System length

### 2. Analysis Features
- **Individual Performance**: Detailed analysis for each storm scenario
- **Comparative Analysis**: Side-by-side comparison with soakwell performance
- **Cost Estimation**: Rough cost comparison between systems
- **Design Recommendations**: Performance-based system selection

### 3. Output Interpretation

**Key Performance Metrics:**
- **Infiltration Efficiency**: Percentage of inflow successfully infiltrated
- **Storage Utilization**: Peak storage as percentage of total capacity
- **Overflow Volume**: Water not handled by the system
- **System Cost**: Estimated installation cost

**Performance Plots:**
- Flow rates over time (inflow, pipe flow, infiltration, overflow)
- Storage volume and water level in trench
- Cumulative volume analysis
- Comparison charts between systems

## Design Parameters

### Your Site Configuration
Based on your requirements:
- **Pipe**: 300mm diameter perforated concrete
- **Trench**: 600mm wide × 900mm deep
- **Aggregate**: Single-sized 40mm stone
- **Soil**: Sand with k = 4.63×10⁻⁵ m/s
- **Groundwater**: No impact (deep water table)

### Typical Performance
For a 100m French drain with your soil conditions:
- **Storage Capacity**: ~19 m³ (0.19 m³/m × 100m)
- **Infiltration Rate**: ~0.28 m³/s (at full capacity)
- **Pipe Capacity**: ~0.01 m³/s (at 0.5% slope)

## Comparison with Soakwells

### French Drain Advantages
- **Linear infiltration** along entire length
- **Better peak flow handling** (continuous discharge)
- **Lower maintenance** (less prone to clogging)
- **Flexible sizing** (adjustable length)

### Soakwell Advantages
- **Concentrated installation** (smaller footprint)
- **Standard sizing** (manufacturer specifications)
- **Predictable performance** (established design methods)
- **Lower excavation** (point installation vs linear)

### Selection Criteria
The dashboard will recommend the better system based on:
1. **Infiltration efficiency** across all storm scenarios
2. **Overflow frequency** and volume
3. **Storage requirements** and utilization
4. **Cost effectiveness** per m³ of water handled

## Cost Analysis

### French Drain Costs (Typical AUD per meter)
- **Pipe**: $50/m (300mm perforated concrete)
- **Excavation**: $80/m (600mm wide × 900mm deep)
- **Aggregate**: $30/m (40mm gravel bedding)
- **Installation**: $40/m (pipe placement, backfill)
- **Total**: ~$200/m

### Length Requirements
The model estimates required length based on:
- Peak flow handling capacity
- Total volume storage requirements  
- Soil infiltration capacity
- Available site space

## Validation and Limitations

### Model Validation
- Based on established hydraulic principles
- Uses conservative assumptions for safety
- Tested against typical Australian storm data

### Limitations
- Assumes uniform soil conditions
- No groundwater interaction modeled
- Simplified clogging effects
- Linear relationship assumptions

### Recommendations
- Conduct soil testing for accurate k values
- Consider site-specific constraints
- Plan for maintenance access
- Include safety factors in final design

## Technical Support

For questions about the French drain model:
1. Check the mathematical equations in `french_drain_model.py`
2. Review the demonstration script `french_drain_demo.py`
3. Examine soil parameter sensitivity in the analysis
4. Compare with local design standards and regulations

The model provides a scientific basis for comparing drainage systems but should be used alongside professional engineering judgment and local design standards.
