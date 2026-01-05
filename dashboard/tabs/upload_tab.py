"""
Upload tab component for the dashboard.
Handles file upload and initial data preview.
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    get_data_overview_stats,
    generate_analysis_info,
)
from styles import apply_analyze_button_css


def render_upload_tab(risk_threshold):
    """
    Render the upload tab where users can upload CSV files.
    
    Args:
        risk_threshold: Current risk threshold
    """
    st.markdown('<p class="section-header">📤 Upload Procurement Data</p>', unsafe_allow_html=True)
    
    # Statistics cards
    st.markdown('<p class="section-header">📊 Data Overview</p>', unsafe_allow_html=True)
    
    # State Machine: Either we have data (Persistent) or we need data (Upload)
    if 'persistent_df' in st.session_state and st.session_state['persistent_df'] is not None:
        df = st.session_state['persistent_df']
        filename = st.session_state.get('persistent_filename', 'Uploaded File')
        
        # PERSISTENT STATE: Show File Info & Reset Button
        col_info, col_reset = st.columns([3, 1])
        with col_info:
            st.info(f"📁 **Current File:** {filename} (Loaded)")
        with col_reset:
            if st.button("📤 Upload New File", use_container_width=True, type="secondary"):
                # Clear persistence and reload
                del st.session_state['persistent_df']
                del st.session_state['persistent_filename']
                if 'df' in st.session_state: del st.session_state['df']
                if 'analyzed' in st.session_state: del st.session_state['analyzed']
                st.rerun()
        
        # logic continues to common section below...

    else:
        # UPLOAD STATE: Show Uploader
        uploaded_file = st.file_uploader(
            "Drag & drop CSV file or click to browse",
            type=['csv'],
            help="Upload a CSV file containing procurement/tender data",
            key="procurement_uploader"
        )
        
        # Info box
        st.markdown("""
        <div class="info-box">
            <p style="color: #1f77b4; font-weight: 600; margin-bottom: 0.5rem;">📋 Supported Data Format</p>
            <p style="color: #6b7280; font-size: 0.9rem; margin: 0;">
            Upload a CSV file containing procurement/tender data with columns such as:
            Tender ID, Department, Amount, Vendor details, Dates, Contract information, Bid details, etc.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if uploaded_file is not None:
             # Process upload
             try:
                 df = pd.read_csv(uploaded_file)
                 # Save to session state
                 st.session_state['persistent_df'] = df
                 st.session_state['persistent_filename'] = uploaded_file.name
                 st.session_state['persistent_df'] = df
                 st.session_state['persistent_filename'] = uploaded_file.name 
             except Exception as e:
                 st.error(f"Error reading file: {e}")
                 return

        else:
            # Stop execution here if no data
            return 

    # ========================================================
    # COMMON LOGIC (Only runs if we have data)
    # ========================================================
    
    # Success message (optional, maybe check upload_time if needed, or skip to keep clean)
    # We skip special success message to avoid "double button" confusion or relying on transient state.
    # The "Current File" info box above serves as confirmation.
    
    if True: # wrapper to keep indentation consistent with rest of file
        # Auto-scroll script (can keep purely for UI polish if desired, or remove)
        pass
        
        overview_stats = get_data_overview_stats(df, risk_threshold)
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Card 1: Row Count
        with col1:
            st.markdown(f"""
            <div class="metric-card-blue">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">#️⃣</div>
                <p class="metric-value">{overview_stats['row_count']:,}</p>
                <p style="font-size: 0.9rem; opacity: 0.9; margin: 0;">Row Count</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Card 2: Column Count
        with col2:
            st.markdown(f"""
            <div class="metric-card-green">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">💾</div>
                <p class="metric-value">{overview_stats['column_count']}</p>
                <p style="font-size: 0.9rem; opacity: 0.9; margin: 0;">Column Count</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Card 3: Total Amount
        with col3:
            st.markdown(f"""
            <div class="metric-card-orange">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">💰</div>
                <p style="font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;">{overview_stats['total_amount']}</p>
                <p style="font-size: 0.9rem; opacity: 0.9; margin: 0;">Total Amount</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Card 4: Data Type
        with col4:
            st.markdown("""
            <div class="metric-card-red">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📄</div>
                <p style="font-size: 1.25rem; font-weight: 600; margin: 0.5rem 0;">Procurement</p>
                <p style="font-size: 0.9rem; opacity: 0.9; margin: 0;">Data Type</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Data Preview
        st.markdown('<p class="section-header">👁️ Data Preview (First 5 Rows)</p>', unsafe_allow_html=True)
        
        st.dataframe(
            df.head(5),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Analyze Button with form
        apply_analyze_button_css()
        
        # Import validation function
        from utils.ml_utils import validate_data_sufficiency
        
        # Run validation
        is_valid, message, status = validate_data_sufficiency(df)
        
        if status == "error":
            st.error(message)
        elif status == "warning":
            st.warning(message)
        else:
            st.success(message)
            
        with st.form(key="analyze_form"):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Disable button if critical error
                submit = st.form_submit_button("🚀 Analyze for Fraud", use_container_width=True, disabled=(status == "error"))
            
        if submit:
            with st.spinner("🔍 Analyzing data for fraud indicators..."):
                time.sleep(1.5)
                
                st.session_state['analyzed'] = True
                st.session_state['df'] = df
                st.session_state['upload_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state['risk_threshold'] = risk_threshold
                
                # Auto-switch to Dashboard tab after analysis
                st.success("✅ Analysis completed! Redirecting to Dashboard...")
                time.sleep(0.5)
                # Redirect to dashboard using session state
                st.session_state.current_page = "dashboard"
                st.rerun()
        

        
        # Analysis Info
        analysis_info = generate_analysis_info(len(df), risk_threshold)
        st.markdown(f"""
        <div class="info-box">
            <div style="display: flex; align-items: start; gap: 0.75rem;">
                <div style="font-size: 1.5rem;">ℹ️</div>
                <div>
                    <p style="color: #1f77b4; font-weight: 600; margin: 0 0 0.25rem 0;">Analysis Information</p>
                    <p style="color: #6b7280; font-size: 0.9rem; margin: 0;">
                    {analysis_info}
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
