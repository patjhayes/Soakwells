#!/usr/bin/env python3
"""
Minimal Streamlit Test App
Just to verify basic Streamlit functionality works
"""

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Test App", page_icon="🧪")

st.title("🧪 Streamlit Test App")
st.write("This is a minimal test to verify Streamlit deployment works.")

st.subheader("Basic Functionality Test")

# Test basic widgets
name = st.text_input("Enter your name:", "World")
st.write(f"Hello, {name}!")

# Test data display
if st.button("Generate Sample Data"):
    data = pd.DataFrame({
        'x': np.random.randn(100),
        'y': np.random.randn(100)
    })
    
    st.write("Sample data generated:")
    st.dataframe(data.head())
    
    st.line_chart(data)

st.success("✅ If you can see this, Streamlit is working correctly!")

st.info("""
**Next Steps:**
1. Verify this basic app works
2. Gradually add back dashboard components
3. Identify which component is causing the deployment error
""")
