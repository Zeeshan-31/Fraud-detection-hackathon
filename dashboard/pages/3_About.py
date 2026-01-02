import streamlit as st

st.set_page_config(page_title="About", layout="wide", page_icon="ℹ️")

st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #f0f9ff 0%, #dbeafe 100%); }
        h1, h2, h3, p, li { font-family: 'Poppins', sans-serif; color: #000000; }
    </style>
""", unsafe_allow_html=True)

st.title("About AuditGuard")

st.markdown("""
### 🕵️ What is AuditGuard?
AuditGuard is an AI-powered fraud detection system designed to help auditors identify corruption in procurement data.

### 🧠 How it works:
1.  **Upload Data:** Users provide raw CSV files containing tender information.
2.  **AI Analysis:** Our Hybrid Forest model scans for patterns like:
    * **Shell Companies:** Vendors created immediately before receiving payment.
    * **Bid Rigging:** Multiple bids from the same IP address or phone number.
    * **Split Payments:** Transactions structured just below approval limits.
3.  **Visualization:** A dashboard highlights critical risks for immediate review.

---
*Built for the 2026 Hackathon*
""")