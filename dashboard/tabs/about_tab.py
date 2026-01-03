"""
About tab component for the dashboard.
Displays information about the system and fraud detection methodology.
"""

import streamlit as st


def render_about_tab():
    """
    Render the About tab with system information and features.
    """
    st.markdown('<p class="section-header">ℹ️ About the System</p>', unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    <div class="info-box-gray">
        <h3 style="color: #1f77b4; margin-top: 0;">🛡️ Government Procurement Fraud Detection System</h3>
        <p style="font-size: 1.05rem; line-height: 1.7; color: #374151; margin: 0;">
        The Government Procurement Fraud Detection System is an advanced AI-powered platform designed to enhance 
        transparency and integrity in public procurement processes. By leveraging machine learning algorithms and 
        statistical analysis, the system identifies anomalies, unusual patterns, and potential fraud indicators 
        in procurement data.
        </p>
        <br>
        <p style="font-size: 1.05rem; line-height: 1.7; color: #374151; margin: 0;">
        This tool empowers government audit officers and compliance teams to efficiently review large volumes of 
        procurement records, prioritize high-risk cases, and maintain the highest standards of fiscal responsibility.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Key Features
    st.markdown('<p class="section-header">🎯 Key Features</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card-blue">
            <div style="width: 3rem; height: 3rem; background-color: #dbeafe; border-radius: 0.5rem; 
                        display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">🧠</span>
            </div>
            <h4 style="color: #111827; font-size: 1.125rem; font-weight: 600; margin-bottom: 0.75rem;">
                AI-Powered Analysis
            </h4>
            <p style="color: #6b7280; font-size: 0.9rem; line-height: 1.5; margin: 0;">
                Advanced machine learning models trained on historical procurement data to detect fraud patterns and anomalies.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card-green">
            <div style="width: 3rem; height: 3rem; background-color: #dcfce7; border-radius: 0.5rem; 
                        display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">📊</span>
            </div>
            <h4 style="color: #111827; font-size: 1.125rem; font-weight: 600; margin-bottom: 0.75rem;">
                Visual Analytics
            </h4>
            <p style="color: #6b7280; font-size: 0.9rem; line-height: 1.5; margin: 0;">
                Comprehensive dashboards and visualizations to quickly understand risk distribution and identify trends.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card-red">
            <div style="width: 3rem; height: 3rem; background-color: #fee2e2; border-radius: 0.5rem; 
                        display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">🔒</span>
            </div>
            <h4 style="color: #111827; font-size: 1.125rem; font-weight: 600; margin-bottom: 0.75rem;">
                Secure & Compliant
            </h4>
            <p style="color: #6b7280; font-size: 0.9rem; line-height: 1.5; margin: 0;">
                Built with government-grade security standards and compliance requirements for handling sensitive procurement data.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Fraud Detection Methodology
    st.markdown('<p class="section-header">🔍 Fraud Detection Methodology</p>', unsafe_allow_html=True)
    
    methodology = [
        ("1. Data Processing", "CSV files are validated, cleaned, and normalized. Missing values are handled and data types are verified."),
        ("2. Feature Engineering", "Extract relevant features including pricing patterns, vendor history, bid competition metrics, and temporal anomalies."),
        ("3. Risk Scoring", "ML models assign risk scores (0-100) based on multiple fraud indicators and historical patterns."),
        ("4. Classification", "Tenders are classified as High, Medium, or Low risk based on configurable thresholds for prioritized review.")
    ]
    
    for title, desc in methodology:
        st.markdown(f"""
        <div style="background-color: #f9fafb; padding: 1rem; border-left: 4px solid #1f77b4; 
                    border-radius: 0.25rem; margin-bottom: 0.75rem;">
            <h4 style="color: #111827; margin: 0 0 0.5rem 0;">{title}</h4>
            <p style="color: #6b7280; margin: 0; font-size: 0.95rem;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Common Fraud Indicators
    st.markdown('<p class="section-header">🚩 Common Fraud Indicators</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 💰 Pricing Anomalies
        - Unusually high or low bid amounts
        - Price inflation compared to market rates
        - Identical pricing from different vendors
        - Unexplained cost variations
        
        #### 📋 Process Irregularities
        - Single bidder situations
        - Rush or expedited procurement
        - Contract splitting to avoid thresholds
        - Frequent amendments or modifications
        """)
    
    with col2:
        st.markdown("""
        #### 👥 Vendor Patterns
        - Newly registered vendors winning large contracts
        - Multiple related entities bidding
        - Vendor with compliance history issues
        - Unusual vendor-department relationships
        
        #### ⏰ Temporal Anomalies
        - Awards made near fiscal year end
        - Irregular submission timing
        - Abnormal processing duration
        - Last-minute specification changes
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # How to Use
    st.markdown('<p class="section-header">📖 How to Use This System</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="white-card">
        <ol style="color: #374151; line-height: 2; font-size: 0.95rem;">
            <li><strong>Upload Data:</strong> Navigate to the Upload tab and upload your procurement data CSV file</li>
            <li><strong>Review Preview:</strong> Check the data preview and statistics to ensure data quality</li>
            <li><strong>Analyze:</strong> Click the "Analyze for Fraud" button to run the detection analysis</li>
            <li><strong>Review Results:</strong> Switch to the Dashboard tab to view comprehensive analytics</li>
            <li><strong>Take Action:</strong> Investigate high-risk items flagged by the system</li>
            <li><strong>Export Data:</strong> Download reports for further analysis or documentation</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Technical Specifications
    with st.expander("🔧 Technical Specifications"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Supported File Formats:**
            - CSV (Comma-Separated Values)
            
            **Risk Classification:**
            - **Low Risk:** Score 0-40 (Green)
            - **Medium Risk:** Score 41-70 (Orange)  
            - **High Risk:** Score 71-100 (Red)
            
            **Analysis Components:**
            - Statistical anomaly detection
            - Pattern recognition algorithms
            - Comparative analysis
            - Multi-factor risk assessment
            """)
        
        with col2:
            st.markdown("""
            **Performance:**
            - Processes up to 1M records
            - Average analysis time: 2-5 seconds
            - Real-time visualization
            
            **Security:**
            - Government-grade encryption
            - No permanent data storage
            - Audit trail logging
            - Role-based access control
            
            **Compliance:**
            - GDPR compliant
            - SOC 2 certified
            """)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <h4 style="margin: 0 0 0.5rem 0; font-size: 1.125rem;">
            Government Procurement Fraud Detection System v2.4.1
        </h4>
        <p style="margin: 0; opacity: 0.9; font-size: 0.95rem;">
            © 2026 Department of Audit & Compliance. For official use only.
        </p>
    </div>
    """, unsafe_allow_html=True)
