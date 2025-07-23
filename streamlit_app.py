#!/usr/bin/env python3
"""
Streamlit App - Main Entry Point
Robust entry point for Soakwell Analysis Dashboard with graceful error handling
"""

import streamlit as st
import sys
import traceback

def run_dashboard():
    """Run the dashboard with comprehensive error handling"""
    
    st.set_page_config(
        page_title="Soakwell Analysis Dashboard", 
        page_icon="💧",
        layout="wide"
    )
    
    st.title("💧 Soakwell Analysis Dashboard")
    st.write("Engineering analysis tool for stormwater soakwell sizing and performance")
    
    # Try to run the main dashboard
    try:
        # Import the main dashboard module
        from soakwell_dashboard import main as dashboard_main
        
        # Run the dashboard
        dashboard_main()
        
    except ImportError as e:
        st.error("⚠️ Import Error")
        st.write(f"Could not import dashboard module: {str(e)}")
        
        # Try minimal dashboard as fallback
        try:
            st.info("🔄 Attempting to load minimal dashboard...")
            from soakwell_dashboard_minimal import main as minimal_main
            minimal_main()
            
        except Exception as e2:
            st.error(f"Minimal dashboard also failed: {str(e2)}")
            show_fallback_interface()
            
    except Exception as e:
        st.error("⚠️ Application Error")
        st.write(f"Error: {str(e)}")
        
        with st.expander("Show Error Details"):
            st.code(traceback.format_exc())
        
        show_fallback_interface()

def show_fallback_interface():
    """Show a basic interface when the main dashboard fails"""
    
    st.subheader("🛠️ Dashboard Status")  
    st.info("""
    The dashboard is experiencing technical difficulties. This typically happens due to:
    
    - **Import Errors**: Missing dependencies or module import issues
    - **Configuration Issues**: Streamlit Cloud environment differences
    - **Code Errors**: Syntax or runtime errors in the dashboard code
    
    **What's Available:**
    - ✅ Basic Streamlit interface is working
    - ⚠️ Full dashboard features temporarily unavailable
    """)
    
    st.subheader("📋 About This Dashboard")
    st.write("""
    **Soakwell Analysis Dashboard** provides:
    
    🔹 **Soakwell Sizing**: Calculate optimal soakwell dimensions based on rainfall data and soil conditions
    
    🔹 **Performance Analysis**: Analyze soakwell performance under various storm conditions
    
    🔹 **Hydrograph Processing**: Import and analyze rainfall/runoff time series data
    
    🔹 **French Drain Modeling**: Mathematical modeling of French drain infiltration systems
    
    🔹 **Comparative Analysis**: Compare different stormwater management solutions
    """)
    
    st.subheader("🔧 Technical Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**System Status:**")
        st.write(f"- Python Version: {sys.version.split()[0]}")
        st.write(f"- Streamlit Version: {st.__version__}")
        
    with col2:
        st.write("**Repository:**")
        st.write("- GitHub: patjhayes/Soakwells")
        st.write("- Branch: main")

if __name__ == "__main__":
    run_dashboard()
