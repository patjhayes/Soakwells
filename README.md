# Soakwell Design Dashboard

An interactive Streamlit web application for analyzing soakwell performance in stormwater management systems.

## Features

- 📊 Interactive storm hydrograph analysis
- 🌧️ Multiple storm scenario testing
- 🔧 Comprehensive soakwell configuration solver
- 📈 Real-time performance visualization
- 📋 Detailed engineering reports
- 💰 Cost analysis with manufacturer specifications

## How to Use

1. Upload your storm hydrograph files (.ts1 format)
2. Configure soil parameters and soakwell dimensions
3. Run analysis to see performance metrics
4. Use the solver to find optimal configurations
5. Generate detailed reports for your designs

## File Formats Supported

- DRAINS TS1 files
- CSV files with time-series data
- Custom storm hydrograph formats

## Technical Details

The application simulates soakwell performance using:
- Hydraulic modeling with variable outflow rates
- 24-hour extended simulation including emptying cycles
- Multiple storm scenario testing
- Standard manufacturer specifications from Perth Soakwells

## Deployment

This app is deployed on Streamlit Community Cloud. Visit the live application at: [Your App URL]

## Local Development

To run locally:

```bash
pip install -r requirements.txt
streamlit run soakwell_dashboard.py
```

## Author

Developed for stormwater engineering analysis and soakwell design optimization.
