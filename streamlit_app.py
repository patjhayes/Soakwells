#!/usr/bin/env python3
"""
Streamlit App - Testing Basic Functionality
"""

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Soakwell Dashboard Test", page_icon="💧")

st.title("💧 Soakwell Dashboard - Deployment Test")
st.write("Testing basic Streamlit functionality before loading full dashboard.")

st.info("🔄 **Step 1**: Basic Streamlit functionality test")

# Test basic functionality
if st.button("Test Basic Features"):
    st.success("✅ Button clicks work!")
    
    # Test data handling
    data = pd.DataFrame({
        'Time': range(10),
        'Flow': np.random.rand(10) * 100
    })
    
    st.write("Sample data generation:")
    st.dataframe(data)
    
    st.line_chart(data.set_index('Time'))

st.info("🔄 **Step 2**: Attempting to load dashboard components")

# Now try to load dashboard components one by one
dashboard_status = {}

# Test 1: Try importing pandas/numpy/plotly
try:
    import plotly.graph_objects as go
    dashboard_status['plotly'] = "✅ Success"
except Exception as e:
    dashboard_status['plotly'] = f"❌ Error: {str(e)}"

# Test 2: Try importing our modules
try:
    import soakwell_dashboard_minimal
    dashboard_status['minimal_dashboard'] = "✅ Success"
except Exception as e:
    dashboard_status['minimal_dashboard'] = f"❌ Error: {str(e)}"

try:
    import french_drain_model
    dashboard_status['french_drain'] = "✅ Success"
except Exception as e:
    dashboard_status['french_drain'] = f"❌ Error: {str(e)}"

try:
    import french_drain_integration
    dashboard_status['french_integration'] = "✅ Success"
except Exception as e:
    dashboard_status['french_integration'] = f"❌ Error: {str(e)}"

try:
    import soakwell_dashboard
    dashboard_status['full_dashboard'] = "✅ Success"
except Exception as e:
    dashboard_status['full_dashboard'] = f"❌ Error: {str(e)}"

# Display results
st.subheader("� Component Import Status")
for component, status in dashboard_status.items():
    st.write(f"**{component}**: {status}")

# If everything imports successfully, try running minimal dashboard
if all("✅" in status for status in dashboard_status.values()):
    st.success("🎉 All components imported successfully!")
    
    if st.button("Load Full Dashboard"):
        try:
            from soakwell_dashboard import main as dashboard_main
            st.info("🔄 Loading full dashboard...")
            dashboard_main()
        except Exception as e:
            st.error(f"Error running full dashboard: {str(e)}")
            try:
                from soakwell_dashboard_minimal import main as minimal_main
                st.info("� Loading minimal dashboard...")
                minimal_main()
            except Exception as e2:
                st.error(f"Error running minimal dashboard: {str(e2)}")
else:
    st.error("⚠️ Some components failed to import. Check the status above.")
    st.info("This helps identify which specific component is causing deployment issues.")
