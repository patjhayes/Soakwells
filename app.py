#!/usr/bin/env python3
"""
Streamlit App Entry Point
Simple, reliable entry point that gracefully handles all imports
"""

import streamlit as st

def main():
    """Main application entry point with graceful error handling"""
    
    st.set_page_config(
        page_title="Soakwell Analysis Dashboard", 
        page_icon="💧",
        layout="wide"
    )
    
    st.title("💧 Soakwell Analysis Dashboard")
    st.write("Engineering analysis tool for stormwater soakwell sizing and performance")
    
    # Try to import and run the main dashboard
    try:
        # Try the full dashboard first
        import soakwell_dashboard
        st.success("✅ Full dashboard loaded successfully")
        # The dashboard module should handle its own execution
        
    except Exception as e:
        st.error(f"Error loading full dashboard: {str(e)}")
        st.info("Attempting to load minimal dashboard...")
        
        try:
            # Fallback to minimal dashboard
            import soakwell_dashboard_minimal
            st.success("✅ Minimal dashboard loaded successfully")
            
        except Exception as e2:
            st.error(f"Error loading minimal dashboard: {str(e2)}")
            st.info("💡 There seems to be an issue with the dashboard modules.")
            
            # Show basic info
            st.subheader("Dashboard Information")
            st.write("""
            This dashboard provides:
            - Soakwell sizing calculations
            - Hydrograph analysis
            - Performance optimization
            - French drain modeling (when available)
            
            Please check the deployment logs for more information.
            """)

if __name__ == "__main__":
    main()
