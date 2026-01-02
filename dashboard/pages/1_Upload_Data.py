import streamlit as st
import pandas as pd
import numpy as np

# 1. PAGE CONFIG
st.set_page_config(page_title="Upload Data", layout="wide", page_icon="📂")

# 2. SHARED CSS (So it looks good)
st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #f0f9ff 0%, #dbeafe 100%); }
        h1, h2, h3 { font-family: 'Poppins', sans-serif; color: #000000; }
        .stButton button { color: white !important; }
        div[data-testid="stFileUploaderDropzone"] { background-color: rgba(255, 255, 255, 0.6); }
        div[data-testid="stFileUploaderDropzone"] div { color: black !important; }
    </style>
""", unsafe_allow_html=True)

# 3. INITIALIZE SESSION STATE (The Memory)
if 'data' not in st.session_state:
    st.session_state.data = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

# 4. PAGE CONTENT
st.title("Upload Procurement Data")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    st.subheader("Data Preview")
    st.dataframe(df.head(), use_container_width=True)
    
    # RISK THRESHOLD (Simple slider for this page)
    risk_threshold = st.slider("High Risk Threshold", 50, 90, 70)

    if st.button("🚀 RUN FRAUD ANALYSIS", type="primary"):
        with st.spinner('Running Analysis...'):
            # --- AI MODEL LOGIC HERE ---
            # (Replace this mock logic with real model later)
            df['risk_score'] = np.random.randint(0, 100, size=len(df))
            
            def get_category(score):
                if score >= risk_threshold: return "High"
                elif score >= 40: return "Medium"
                else: return "Low"
            
            df['risk_level'] = df['risk_score'].apply(get_category)
            
            # --- SAVE TO MEMORY (CRITICAL STEP) ---
            st.session_state.data = df
            st.session_state.analysis_complete = True
            st.session_state.risk_threshold = risk_threshold # Save setting too
            
            st.success("✅ Analysis Complete! Go to the 'Dashboard' page in the sidebar.")