import streamlit as st

st.title("🌧️ Soakwell Dashboard Test")
st.write("If you can see this, Streamlit is working!")

# Simple test interface
diameter = st.slider("Test Slider - Diameter (m)", 1.0, 5.0, 3.0)
st.write(f"Selected diameter: {diameter} m")

if st.button("Test Button"):
    st.success("Button works!")
