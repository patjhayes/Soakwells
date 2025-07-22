# 🌧️ Soakwell Design Dashboard

An interactive web-based dashboard for analyzing soakwell performance using storm hydrograph data from DRAINS or similar stormwater modeling software.

## Features

- **📁 File Upload**: Upload multiple .ts1 hydrograph files
- **⚙️ Real-time Parameter Adjustment**: Modify soakwell dimensions and soil properties on-the-fly
- **📊 Interactive Visualizations**: Dynamic plots showing volume in, volume stored, and volume out
- **📈 Performance Metrics**: Storage efficiency, volume utilization, and overflow analysis
- **⚖️ Scenario Comparison**: Compare multiple storm events and design parameters
- **💡 Design Recommendations**: Automated suggestions for optimal soakwell design

## Quick Start

### Option 1: Use the Batch File (Windows)
1. Double-click `start_dashboard.bat`
2. The dashboard will open automatically in your web browser at `http://localhost:8502`

### Option 2: Use Python Launcher
1. Run: `python start_dashboard.py`
2. Open your browser to `http://localhost:8502`

### Option 3: Manual Start
1. Activate virtual environment (if used): `.venv\Scripts\activate`
2. Run: `python -m streamlit run soakwell_dashboard.py --server.port 8502`

## How to Use

### 1. Upload Storm Data
- Click "Browse files" in the sidebar
- Upload one or more `.ts1` files from DRAINS or similar software
- View file summary with duration, peak flow, and total volume

### 2. Adjust Parameters
**Soakwell Geometry:**
- Diameter: 1.0 - 8.0 meters
- Height: 1.0 - 5.0 meters

**Soil Properties:**
- Soil Type: Sandy, Medium, Clay, or Custom
- Hydraulic Conductivity: 1×10⁻⁷ to 1×10⁻³ m/s
- Soil Moderation Factor: 0.5 - 2.0

### 3. View Results
- **Performance Summary**: Key metrics for all scenarios
- **Individual Analysis**: Detailed plots for each storm event
- **Scenario Comparison**: Side-by-side performance comparison
- **Design Recommendations**: Automated suggestions

## Understanding the Results

### Key Metrics

**Storage Efficiency (%)**: Percentage of inflow that infiltrates (outflow/inflow × 100)
- Higher is better for water quality and groundwater recharge
- Sandy soils typically achieve 30-50% efficiency
- Clay soils may only achieve 5-15% efficiency

**Volume Utilization (%)**: Maximum storage used as percentage of total capacity
- 100% indicates the soakwell is fully utilized
- <80% may indicate oversizing
- >95% indicates good capacity utilization

**Peak Overflow**: Maximum overflow rate during the storm
- Zero overflow is ideal but may not be economical
- Consider multiple smaller soakwells if overflow is excessive

### Plot Interpretations

**Flow Rates Plot**: 
- Blue line: Storm inflow (from hydrograph)
- Green line: Soakwell outflow (infiltration)
- Red line: Overflow (when storage is full)

**Storage & Water Level**:
- Purple line: Current volume stored
- Orange line: Water level in soakwell
- Red dashed line: Maximum capacity

**Cumulative Volumes**:
- Shows total water processed over the storm duration
- Gap between inflow and outflow represents stored/overflowed water

## File Format Requirements

Upload `.ts1` files with the following format:

```
! File created from: Storm_Model.drn
! Storm event: 1% AEP_4.5 hour burst_Storm 1
! Timestep: 1 min
Time (min),Cat1240,Cat3
1.000,0.000,0.000
2.000,0.000,0.000
3.000,0.001,0.001
...
```

- Time in minutes (first column)
- Flow rates in m³/s (subsequent columns)
- Comments starting with '!' are ignored
- Multiple catchments are automatically summed

## Design Guidelines

### Soil Hydraulic Conductivity Values
- **Sandy Soil**: 1×10⁻⁴ m/s (fast drainage)
- **Medium Soil**: 1×10⁻⁵ m/s (moderate drainage)
- **Clay Soil**: 1×10⁻⁶ m/s (slow drainage)

### Sizing Recommendations
1. Start with diameter = height for optimal infiltration area
2. For clay soils, consider larger storage volumes
3. For sandy soils, smaller soakwells may be sufficient
4. If overflow occurs, consider:
   - Increasing diameter (more impact than height)
   - Multiple smaller units
   - Pre-treatment to maintain infiltration rates

### Maintenance Considerations
- Set Soil Moderation Factor > 1.0 to account for clogging
- Sandy soils: Sr = 1.0 - 1.2
- Clay soils: Sr = 1.2 - 1.5
- High sediment loads: Sr = 1.5 - 2.0

## Troubleshooting

**Dashboard won't start:**
- Check Python is installed: `python --version`
- Install requirements: `pip install streamlit plotly pandas`
- Try manual start: `python -m streamlit run soakwell_dashboard.py`

**File upload issues:**
- Ensure file is plain text format (.ts1)
- Check file has proper column headers
- Verify time and flow data are numeric

**Performance issues:**
- Large files (>1000 time steps) may take longer to process
- Close browser tabs when not in use
- Restart dashboard if memory usage becomes high

## Technical Details

### Formulas Used
- **Inflow Volume**: V = C × i × A × D / 1000
- **Soakwell Diameter**: d = √[4V/(π + 120×ks×t/Sr)]
- **Outflow Rate**: Based on infiltration area (base + walls)

### References
- Stormwater Management Manual for Western Australia - Chapter 9
- Argue (2004) soakwell sizing methodology
- Engineers Australia (2006) stormwater management guidelines

## Version Information
- Dashboard Version: 1.0
- Last Updated: January 2025
- Compatible with: DRAINS .ts1 files, MUSIC, SWMM exports

## Support
For technical support or feature requests, refer to the analysis documentation or contact your stormwater engineering team.
