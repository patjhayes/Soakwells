"""
Quick test to verify French drain integration works locally
"""

import streamlit as st

# Test French drain imports
try:
    from french_drain_integration import integrate_french_drain_analysis, add_french_drain_sidebar
    from report_generator import generate_calculation_report, display_mass_balance_summary
    print("✅ All imports successful!")
    
    # Test the sidebar function
    print("Testing add_french_drain_sidebar()...")
    
    # Mock streamlit sidebar for testing
    class MockSidebar:
        def markdown(self, text):
            print(f"Sidebar markdown: {text}")
        def header(self, text):
            print(f"Sidebar header: {text}")
        def checkbox(self, label, **kwargs):
            print(f"Sidebar checkbox: {label}")
            return False  # Default to disabled
        def button(self, label, **kwargs):
            print(f"Sidebar button: {label}")
            return False
        def subheader(self, text):
            print(f"Sidebar subheader: {text}")
        def selectbox(self, label, options, **kwargs):
            print(f"Sidebar selectbox: {label}")
            return options[0] if options else None
        def slider(self, label, **kwargs):
            print(f"Sidebar slider: {label}")
            return kwargs.get('value', 0)
        def info(self, text):
            print(f"Sidebar info: {text}")
    
    # Temporarily replace st.sidebar with mock
    import sys
    if 'streamlit' not in sys.modules:
        st.sidebar = MockSidebar()
    
    # Test the function
    result = add_french_drain_sidebar()
    print(f"Function result: {result}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback
    traceback.print_exc()

print("Test completed!")
