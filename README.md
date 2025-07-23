# 🌧️ Soakwell & French Drain Analysis Dashboard

Advanced stormwater management system analysis tool with integrated soakwell and French drain modeling capabilities.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://soakwells.streamlit.app)

## 🚀 Features

### Soakwell Analysis
- **Interactive Design Tool**: Real-time parameter adjustment and analysis
- **Multiple Storm Scenarios**: Upload and analyze multiple .ts1 hydrograph files
- **Comprehensive Solver**: Find optimal configurations across all size/quantity combinations
- **Manufacturer Integration**: Real specifications and pricing from Australian suppliers
- **Performance Visualization**: Detailed plots of flow, storage, and efficiency metrics

### French Drain Analysis  
- **Mathematical Modeling**: Rigorous hydraulic analysis using Manning's and Darcy's equations
- **Linear Infiltration**: Model perforated pipe systems with aggregate bedding
- **Customizable Geometry**: Adjustable pipe diameter, trench dimensions, and system length
- **Soil Integration**: Uses same soil parameters as soakwell analysis
- **Comparative Analysis**: Side-by-side performance comparison with soakwells

### Integrated Dashboard
- **Unified Interface**: Single dashboard for both drainage system types
- **Real-time Comparison**: Simultaneous analysis and performance comparison
- **Cost Analysis**: Economic evaluation and system recommendations
- **Export Capabilities**: Generate detailed reports and visualizations

## 🛠️ Technical Specifications

### System Configurations

#### Soakwells
- Standard concrete units: 0.6m to 1.8m diameter and depth
- Multiple unit configurations (1-30 units)
- Manufacturer specifications and pricing integration
- Advanced overflow and efficiency analysis

#### French Drains
- Pipe options: 225mm to 450mm diameter perforated concrete
- Trench geometry: Customizable width (400-1000mm) and depth (600-1500mm)
- Aggregate bedding: Single-sized stone with configurable porosity
- Length optimization: 10m to 500m+ systems

## 🚀 Quick Start

### Online Access
Visit the live dashboard: [https://soakwells.streamlit.app](https://soakwells.streamlit.app)

### Local Installation
```bash
# Clone the repository
git clone https://github.com/patjhayes/Soakwells.git
cd Soakwells

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run soakwell_dashboard.py
```

### Usage
1. **Upload Data**: Upload .ts1 hydrograph files from DRAINS or similar software
2. **Configure Systems**: Set soakwell and/or French drain parameters
3. **Analyze Performance**: Run analysis and view results
4. **Compare Systems**: Enable both systems for comparative analysis
5. **Export Results**: Generate reports and save visualizations

## 📁 File Structure

```
├── soakwell_dashboard.py          # Main Streamlit dashboard
├── french_drain_model.py          # French drain mathematical model
├── french_drain_integration.py    # Dashboard integration module
├── french_drain_demo.py           # Standalone demonstration
├── test_french_drain.py          # Validation test suite
├── requirements.txt               # Python dependencies
├── French_Drain_Summary.md       # Technical documentation
└── .streamlit/
    └── config.toml               # Streamlit configuration
```

## 💰 Cost Analysis

### Soakwell Systems
- **Material Costs**: Real pricing from Australian manufacturers
- **Installation Factors**: Excavation and setup complexity
- **Maintenance Considerations**: Long-term performance and upkeep
- **Size Optimization**: Cost-effective diameter and depth selection

### French Drain Systems
- **Linear Costing**: Per-meter pricing model including all components
- **Excavation Analysis**: Depth and width impact on installation cost
- **Material Breakdown**: Pipe, aggregate, and installation costs
- **Length Optimization**: Performance vs cost trade-off analysis

## 🎯 Use Cases

### Residential Development
- **House Lots**: Individual property drainage design
- **Subdivision Planning**: Multiple lot integration and optimization
- **Retrofit Projects**: Upgrading existing drainage systems
- **Compliance Checking**: Meeting local authority requirements

### Commercial Projects
- **Industrial Sites**: Large catchment area management
- **Shopping Centers**: High-intensity rainfall handling
- **Office Complexes**: Integrated stormwater management
- **Infrastructure Projects**: Road and utility corridor drainage

## 📧 Contact

**Patrick Hayes**  
Senior Water Engineer  
Aurecon Group  
📧 patrick.hayes@aurecongroup.com

---

*Built with ❤️ using Python, Streamlit, and advanced hydraulic modeling principles*

To run locally:

```bash
pip install -r requirements.txt
streamlit run soakwell_dashboard.py
```

## Author

Developed for stormwater engineering analysis and soakwell design optimization.
