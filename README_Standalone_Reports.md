# Standalone Engineering Report Generator

This system generates comprehensive engineering reports for infiltration system analysis without requiring the interactive dashboard environment.

## 🚀 Quick Start

### Option 1: Windows Users (Easiest)
1. Double-click `generate_reports.bat`
2. Follow the on-screen prompts

### Option 2: Command Line
```bash
python report_launcher.py
```

### Option 3: Direct Script Execution
```bash
# Interactive single report
python standalone_report_generator.py

# Batch multiple reports
python batch_report_generator.py
```

## 📁 System Requirements

### Required Files
- `soakwell_dashboard.py` - Core analysis functions
- `comprehensive_report_generator.py` - Report generation engine
- `french_drain_integration.py` - French drain analysis (optional)
- `standalone_report_generator.py` - Interactive report generator
- `batch_report_generator.py` - Batch processing
- `report_launcher.py` - User-friendly launcher

### Required Python Packages
```bash
pip install numpy pandas plotly streamlit
```

### Storm Data
- DRAINS directory with .ts1 storm files
- System automatically detects available storm events

## 🎯 Report Generation Options

### 1. Interactive Single Report
- **Purpose**: Generate detailed report for specific storm/configuration
- **Use Case**: Focused analysis of particular design scenario
- **Features**:
  - Interactive configuration setup
  - Storm selection from available files
  - Custom parameter adjustment
  - Comprehensive engineering documentation

### 2. Batch Report Generation
- **Purpose**: Generate multiple reports for standard configurations
- **Use Case**: Comparative analysis across multiple design options
- **Features**:
  - Pre-defined standard configurations
  - Automatic critical storm selection
  - Bulk processing capability
  - Comparative analysis summaries

## ⚙️ Standard Configurations

The batch generator includes these pre-defined configurations:

1. **Standard Single 2m Soakwell**
   - Diameter: 2.0m, Depth: 2.0m
   - Single unit, Perth sand conditions

2. **Multiple 1.5m Soakwells (3 units)**
   - Diameter: 1.5m, Depth: 1.8m
   - Distributed system approach

3. **Large Single 2.5m Soakwell**
   - Diameter: 2.5m, Depth: 2.5m
   - High-capacity single unit

4. **Conservative Clay Soil Design**
   - Diameter: 3.0m, Depth: 3.0m, 2 units
   - Low permeability soil conditions

## 📊 Report Features

### Engineering Analysis
- **Extended Duration Analysis**: 72 hours for soakwells, 12+ hours for French drains
- **Emptying Time Assessment**: Critical performance criteria analysis
- **Mass Balance Verification**: ±1% accuracy requirement
- **Professional Documentation**: PDF-ready HTML format

### Technical Content
- Storm event characterization
- Soakwell system hydraulic analysis
- French drain linear infiltration modeling
- Comparative performance assessment
- Design recommendations
- Mass balance verification
- Technical notes and limitations

### Output Formats
- **HTML Reports**: Professional engineering documentation
- **Summary Files**: Quick reference analysis results
- **Batch Summaries**: Comparative analysis across configurations

## 📁 Output Directory Structure

```
engineering_reports/          (Interactive reports)
├── Infiltration_Analysis_Storm1_YYYYMMDD_HHMMSS.html
├── Analysis_Summary_YYYYMMDD_HHMMSS.txt
└── ...

batch_engineering_reports/    (Batch reports)
├── Standard_Single_2m_Soakwell_Storm1_YYYYMMDD_HHMMSS.html
├── Multiple_1.5m_Soakwells_Storm2_YYYYMMDD_HHMMSS.html
├── Batch_Analysis_Summary_YYYYMMDD_HHMMSS.txt
└── ...
```

## 🔧 Configuration Parameters

### Soakwell Parameters
- **Diameter**: Soakwell internal diameter (m)
- **Depth**: Soakwell depth (m)
- **Number of Units**: Multiple soakwell configuration
- **Soil Permeability (ks)**: Hydraulic conductivity (m/s)
- **Soil Factor (Sr)**: Soil resistance factor

### French Drain Parameters
- **Length**: Linear system length (m)
- **Pipe Diameter**: Collection pipe diameter (standard 300mm)
- **Trench Dimensions**: Width and depth (standard 600mm × 900mm)
- **Soil Permeability**: Same as soakwell analysis

### Default Values
- Perth sand permeability: 4.63×10⁻⁵ m/s
- Clay soil permeability: 1×10⁻⁶ m/s
- Aggregate porosity: 35%
- Manning's coefficient: 0.013 (concrete pipe)

## 🌧️ Storm Data Management

The system automatically processes .ts1 files from the DRAINS directory:

### Supported Storm Types
- Multiple AEP (Annual Exceedance Probability) events
- Various burst durations (10 min to 144 hours)
- Different storm patterns and intensities

### Critical Storm Selection
Batch processing automatically selects representative storms:
- Short intense events (1-2 hours)
- Medium duration events (4-6 hours)  
- Long duration events (24+ hours)

## 🛠️ Troubleshooting

### Common Issues

#### "Required modules not available"
```bash
pip install numpy pandas plotly streamlit
```

#### "DRAINS directory not found"
- Ensure DRAINS folder exists in project directory
- Verify .ts1 files are present in DRAINS folder

#### "No storm files found"
- Check file extensions (.ts1)
- Verify file permissions
- Ensure files contain valid hydrograph data

#### Report generation fails
- Check available disk space
- Verify write permissions to output directories
- Review error messages for specific issues

### System Status Check
Use the built-in system checker:
```bash
python report_launcher.py
# Select option 3: Check System Status
```

## 📋 Analysis Methodology

### Soakwell Analysis
- **Hydraulic Model**: Darcy's Law for cylindrical flow
- **Mass Balance**: Strict conservation verification
- **Performance Metrics**: Storage efficiency, overflow analysis, emptying time
- **Standards Compliance**: AS/NZS 3500.3 guidelines

### French Drain Analysis
- **Infiltration Model**: Linear Darcy's Law application
- **Pipe Flow**: Manning's equation for hydraulic capacity
- **Storage Model**: Aggregate-filled trench with porosity considerations
- **Performance Assessment**: Infiltration efficiency and overflow analysis

### Comparative Analysis
- Side-by-side performance comparison
- Cost-benefit considerations
- Site-specific factor assessment
- Engineering recommendation framework

## 🎓 Professional Standards

This analysis tool follows established engineering practices:
- Australian Standards compliance (AS/NZS 3500.3)
- Conservative design approaches
- Professional documentation standards
- Peer-reviewable methodology

## 📞 Support

For technical support or questions about the analysis methodology, refer to:
- Project documentation in `README.md`
- Dashboard user guide in `README_Dashboard.md`
- Performance optimization guide in `Performance_Optimization_Guide.md`

---

**Engineering Report Generator v2.0**  
*North Fremantle Pedestrian Infrastructure Project*  
*Professional infiltration system analysis and documentation*
