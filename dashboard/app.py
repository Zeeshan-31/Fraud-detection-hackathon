import streamlit as st

# 1. CONFIGURATION
st.set_page_config(page_title="AuditGuard", layout="wide", page_icon="🛡️")

st.title("Welcome to AuditGuard 🛡️")
st.write("Please select a module from the sidebar to begin.")

# Simple redirect instruction
st.sidebar.success("Select a page above 👆")