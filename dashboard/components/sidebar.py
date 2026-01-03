"""
Sidebar component for the dashboard.
Displays system information and configuration options.
"""

import streamlit as st


def render_sidebar(risk_threshold):
    """
    Render the sidebar with system information and risk threshold slider.
    
    Args:
        risk_threshold: Current risk threshold value
        
    Returns:
        Updated risk threshold value
    """
    with st.sidebar:
        st.markdown("### 🛡️ System Information")
        
        # System info card with blue gradient
        st.markdown("""
        <div class="metric-card-blue">
            <p style="font-size: 0.9rem; opacity: 0.8; margin: 0;">Version</p>
            <p style="font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;">v2.4.1</p>
            <p style="font-size: 0.9rem; opacity: 0.8; margin: 1rem 0 0.25rem 0;">Last Updated</p>
            <p style="font-size: 1rem; margin: 0;">January 2, 2026</p>
            <p style="font-size: 0.9rem; opacity: 0.8; margin: 1rem 0 0.25rem 0;">Status</p>
            <p style="font-size: 1rem; margin: 0;">🟢 Active</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Risk threshold slider
        st.markdown("### ⚙️ Risk Threshold")
        risk_threshold = st.slider(
            "High Risk Threshold (%)",
            min_value=50,
            max_value=90,
            value=risk_threshold,
            help="Tenders with risk score above this threshold will be flagged as high risk"
        )
        
        st.info(f"Tenders with a risk score above **{risk_threshold}%** will be flagged as high risk for review.")
        
        st.markdown("---")
        
        # Quick guide
        st.markdown("### 📖 Quick Guide")
        st.markdown("""
        - 📤 Upload procurement CSV files
        - 🤖 AI analyzes for fraud patterns
        - 🔍 Review high-risk tenders
        - 📥 Download detailed reports
        """)
    
    return risk_threshold
