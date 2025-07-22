📊 Soakwell Dashboard Updates - Real Manufacturer Specifications
================================================================

## Changes Made:

### 1. Expanded Size Options
✅ Updated available diameters: 0.6m, 0.9m, 1.2m, 1.5m, 1.8m (was limited to 0.6m, 0.9m, 1.2m, 1.8m)
✅ Updated available depths: 0.6m, 0.9m, 1.2m, 1.5m, 1.8m (was limited to 0.6m, 0.9m, 1.2m)

### 2. Real Manufacturer Data Integration
✅ Added get_standard_soakwell_specs() function with Perth Soakwells data
✅ Includes actual specifications for each size combination:
   - Capacity (Litres and m³)
   - Weight (kg)
   - Price (AUD ex GST)

### 3. Enhanced User Interface
✅ Real-time specification display in sidebar
✅ Shows manufacturer capacity, weight, and pricing
✅ Total system calculations for multiple units
✅ Warning for non-standard sizes

### 4. Cost-Effectiveness Analysis
✅ Added comprehensive cost analysis table
✅ Cost per % efficiency metric
✅ Cost per m³ capacity metric
✅ Automatic identification of most cost-effective option

### 5. Improved Documentation
✅ Updated parameter sensitivity guide
✅ Added multiple unit considerations
✅ Referenced manufacturer data source

## Available Soakwell Configurations:

| Diameter | Heights Available | Size Range |
|----------|------------------|------------|
| 600mm    | 600mm           | 175L      |
| 900mm    | 600mm, 900mm, 1200mm | 386L - 760L |
| 1200mm   | 600mm, 900mm, 1200mm, 1500mm | 688L - 1560L |
| 1500mm   | 900mm, 1200mm, 1500mm | 1550L - 2560L |
| 1800mm   | 600mm, 900mm, 1200mm, 1500mm, 1800mm | 1520L - 4580L |

## Key Features:

### Real-Time Specifications
- Shows actual manufacturer capacity vs theoretical calculation
- Displays weight for installation planning
- Shows current pricing for budgeting

### Multiple Unit Analysis
- Compares single large vs multiple small units
- Total system capacity and cost calculations
- Flow distribution modeling

### Cost Optimization
- Cost per performance metrics
- Identifies most cost-effective solutions
- Considers both efficiency and capacity

### Engineering Validation
- Based on real Perth Soakwells product specifications
- Watercorp approved products
- Concrete rebar reinforced construction

## Usage:
1. Select diameter and depth from dropdown menus
2. View real-time manufacturer specifications
3. Adjust number of soakwells for distributed systems
4. Upload storm hydrograph files (.ts1)
5. Compare scenarios with cost-effectiveness analysis

## Data Source:
Manufacturer specifications from: https://www.soakwells.com/
Perth Soakwells Pty Ltd - Watercorp Approved Products

Updated: July 21, 2025
