"""
Government Procurement Fraud Detection System - Streamlit Dashboard
==================================================================

This is the main entry point for the dashboard. All functionality has been
modularized into separate components for better maintainability.

STRUCTURE:
- styles/theme.py: All CSS and theme configuration
- components/header.py: Top navigation bar
- components/sidebar.py: Side panel with settings
- tabs/upload_tab.py: File upload interface
- tabs/dashboard_tab.py: Analysis results and visualizations
- tabs/about_tab.py: System information
- utils/helpers.py: Shared utility functions

To modify colors, see styles/theme.py
To modify layout, see individual component files
"""

import streamlit as st
from pathlib import Path
from styles import apply_theme, apply_login_button_styling, fix_sidebar_and_text_colors
from components import render_header, render_sidebar
from tabs import render_upload_tab, render_dashboard_tab, render_about_tab


# =====================================================
# PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Government Procurement Fraud Detection System",
    page_icon="Gemini_Generated_Image_ve0gzve0gzve0gzv.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =====================================================
# APPLY THEME AND STYLING
# =====================================================
apply_theme()


# =====================================================
# FIX SIDEBAR AND TEXT COLORS
# =====================================================
fix_sidebar_and_text_colors()


# =====================================================
# INITIALIZE SESSION STATE
# =====================================================
if 'current_page' not in st.session_state:
    st.session_state.current_page = "upload"

if 'theme_mode' not in st.session_state:
    st.session_state.theme_mode = "Light"

# =====================================================
# RENDER HEADER
# =====================================================
render_header()


# =====================================================
# RENDER SIDEBAR AND GET RISK THRESHOLD
# =====================================================
current_threshold = render_sidebar(risk_threshold=70)
st.session_state['risk_threshold'] = current_threshold


# =====================================================
# APPLY LOGIN BUTTON STYLING
# =====================================================
apply_login_button_styling()


# =====================================================
# RENDER TAB CONTENT BASED ON STATE
# =====================================================
if st.session_state.current_page == "upload":
    render_upload_tab(st.session_state['risk_threshold'])

elif st.session_state.current_page == "dashboard":
    render_dashboard_tab()

elif st.session_state.current_page == "about":
    render_about_tab()

elif page == "login":
    st.subheader("Login")

    if st.session_state.is_logged_in:
        st.success(f"Logged in as {st.session_state.username}")
        st.markdown('<a href="?page=upload" target="_self">Go to Upload</a>', unsafe_allow_html=True)
    else:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Sign in"):
            # TODO: replace with real auth later (DB / API / OAuth)
            if u == "admin" and p == "admin":
                st.session_state.is_logged_in = True
                st.session_state.username = u
                st.query_params["page"] = "upload"  # redirect after login
                st.rerun()
            else:
                st.error("Invalid credentials")
