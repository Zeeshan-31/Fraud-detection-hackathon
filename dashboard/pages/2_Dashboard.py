import streamlit as st
import pandas as pd
import plotly.express as px

# 1. PAGE CONFIG
st.set_page_config(page_title="Dashboard", layout="wide", page_icon="📊")

# 2. SHARED CSS
st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #f0f9ff 0%, #dbeafe 100%); }
        h1, h2, h3 { font-family: 'Poppins', sans-serif; color: #000000; }
        div[data-testid="metric-container"] { background-color: rgba(255,255,255,0.6); border: 1px solid rgba(0,0,0,0.1); }
        div[data-testid="metric-container"] label { color: black !important; }
        div[data-testid="metric-container"] div { color: black !important; }
    </style>
""", unsafe_allow_html=True)

# 3. CHECK FOR DATA
if 'analysis_complete' not in st.session_state or not st.session_state.analysis_complete:
    st.warning("⚠️ No data found! Please go to the 'Upload Data' page first.")
    st.stop() # Stop the code here if no data

# 4. RETRIEVE DATA
df = st.session_state.data
risk_threshold = st.session_state.get('risk_threshold', 70)

# 5. DASHBOARD CONTENT
st.title("Fraud Risk Dashboard")

# Metrics
total = len(df)
high_risk = len(df[df['risk_level'] == 'High'])
med_risk = len(df[df['risk_level'] == 'Medium'])
low_risk = len(df[df['risk_level'] == 'Low'])
high_pct = (high_risk / total) * 100

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Tenders", total)
m2.metric("High Risk", f"{high_risk} ({high_pct:.1f}%)", "Critical", delta_color="inverse")
m3.metric("Medium Risk", med_risk, "Monitor", delta_color="off") 
m4.metric("Low Risk", low_risk, "Safe", delta_color="normal")

st.markdown("### Risk Distribution")
c1, c2 = st.columns(2)

# Charts
with c1:
    fig_pie = px.pie(df, names='risk_level', color='risk_level',
                     color_discrete_map={'High':'#FF4B4B', 'Medium':'#FFAA00', 'Low':'#09AB3B'}, hole=0.4)
    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'color': "black"})
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    fig_hist = px.histogram(df, x='risk_score', nbins=20, color_discrete_sequence=['#3b82f6'])
    fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'color': "black"})
    fig_hist.add_vline(x=risk_threshold, line_dash="dash", line_color="#FF4B4B")
    st.plotly_chart(fig_hist, use_container_width=True)

# Table
st.markdown("### 🚩 High Risk Tenders")
high_risk_df = df[df['risk_score'] >= risk_threshold].sort_values(by='risk_score', ascending=False).head(20)
st.dataframe(high_risk_df, use_container_width=True)