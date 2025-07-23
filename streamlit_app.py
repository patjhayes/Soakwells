#!/usr/bin/env python3
"""
Streamlit App - Soakwell Analysis Dashboard
Main entry point with French drain integration
"""

import streamlit as st

def main():
    """Main application entry point"""
    
    st.set_page_config(
        page_title="Soakwell Analysis Dashboard", 
        page_icon="💧",
        layout="wide"
    )
    
    # Try to run the main dashboard with all features
    try:
        # Import and run the full dashboard
        from soakwell_dashboard import main as dashboard_main
        dashboard_main()
        
    except Exception as e:
        st.error(f"Error loading full dashboard: {str(e)}")
        st.info("Loading minimal dashboard as fallback...")
        
        try:
            # Fallback to minimal dashboard
            from soakwell_dashboard_minimal import main as minimal_main
            minimal_main()
            
        except Exception as e2:
            st.error(f"Error loading minimal dashboard: {str(e2)}")
            
            # Show basic interface
            st.title("💧 Soakwell Analysis Dashboard")
            st.write("Engineering analysis tool for stormwater soakwell sizing and performance")
            
            st.info("""
            The dashboard is temporarily unavailable. This tool provides:
            
            - Soakwell sizing calculations
            - Hydrograph analysis  
            - Performance optimization
            - French drain modeling
            
            Please try refreshing the page.
            """)

if __name__ == "__main__":
    main()
