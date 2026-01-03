"""
Centralized styling and theme configuration for the dashboard.
All CSS styles are managed here for easy customization.
"""

import streamlit as st


def apply_theme():
    """
    Apply the clean light theme to the dashboard.
    """
    st.markdown("""
<script>
    // Theme consistency script placeholder
</script>
""", unsafe_allow_html=True)

    st.markdown("""
<style>
    /* ========================================== */
    /* 🎨 COLOR PALETTE - LIGHT THEME */
    /* ========================================== */
    :root {
        /* Brand Colors */
        --primary-blue: #1f77b4;
        --secondary-blue: #0f3d6b;
        --accent-blue: #eff6ff;
        
        /* Background Colors */
        --main-bg: #f8f9fa;
        --card-bg: #ffffff;
        
        /* Text Colors */
        --text-dark: #111827;
        --text-gray: #4b5563;
        --text-light: #9ca3af;
        
        /* Risk Colors */
        --risk-high: #e74c3c;
        --risk-med: #f39c12;
        --risk-low: #2ecc71;
    }
    
    /* Global Resets */
    /* Global Resets */
    /* Let Streamlit handle main background */
    
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    
    [data-testid="stToolbar"] {
        background-color: transparent;
    }
    

    /* Typography - Font family only */
    body {
        font-family: 'Inter', sans-serif;
    }

    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-dark) !important;
        margin: 1.5rem 0 1rem 0;
    }
    
    /* Cards */
    .white-card {
        background-color: var(--card-bg);
        border: 1px solid #e5e7eb;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: box-shadow 0.2s ease;
    }
    
    .white-card:hover {
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Metric Cards - Colored */
    .metric-card-blue, .metric-card-red, .metric-card-orange, .metric-card-green {
        padding: 1.5rem;
        border-radius: 0.75rem;
        color: white !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .metric-card-blue { background: linear-gradient(135deg, #1f77b4 0%, #0f3d6b 100%); }
    .metric-card-red { background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); }
    .metric-card-orange { background: linear-gradient(135deg, #f39c12 0%, #d68910 100%); }
    .metric-card-green { background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); }
    
    .metric-card-blue *, .metric-card-red *, .metric-card-orange *, .metric-card-green * {
        color: white !important;
    }
    
    .metric-value {
        font-size: 2.25rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    /* Info Boxes */
    .info-box {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 0.5rem;
        padding: 1rem;
        border-left: 4px solid #3b82f6;
    }
    
    .info-box-gray {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1.25rem;
    }
    
    .success-box {
        background-color: #ecfdf5;
        border: 1px solid #a7f3d0;
        border-radius: 0.5rem;
        padding: 1rem;
        border-left: 4px solid #10b981;
        color: #065f46 !important;
    }
    
    /* Feature Cards */
    .feature-card-blue { background-color: #eff6ff; padding: 1.25rem; border-radius: 0.5rem; }
    .feature-card-green { background-color: #ecfdf5; padding: 1.25rem; border-radius: 0.5rem; }
    .feature-card-red { background-color: #fef2f2; padding: 1.25rem; border-radius: 0.5rem; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--card-bg);
        border-right: 1px solid #e5e7eb;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: var(--text-dark) !important;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 2rem !important; /* Rounded pill shape */
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); /* Smooth iOS-like transition */
        padding: 0.5rem 1.5rem;
    }
    
    /* Primary buttons (Analyze, etc) */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-blue) 100%);
        color: white !important;
        border: none;
    }
    
    /* Default buttons */
    .stButton > button:not([kind]) {
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-blue) 100%);
        color: white !important;
        border: none;
    }
    
    /* Secondary buttons (Reset, etc) */
    .stButton > button[kind="secondary"] {
        background-color: white;
        color: var(--text-gray) !important;
        border: 1px solid #e5e7eb;
    }
    
    .stButton > button:hover {
        transform: scale(1.05); /* Pop effect */
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        opacity: 1;
    }

    /* Download Button */
    .stDownloadButton > button {
        background-color: var(--risk-low);
        color: white !important;
        border: none;
        border-radius: 0.5rem;
    }
    
    /* Footer */
    .footer {
        margin-top: 3rem;
        padding: 2rem;
        background: linear-gradient(to right, #1f77b4, #0f3d6b);
        color: white !important;
        border-radius: 0.75rem;
        text-align: center;
    }
    
    .footer h4, .footer p {
        color: white !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: nowrap;
        border: none;
        color: var(--text-gray);
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--primary-blue) !important;
        border-bottom: 2px solid var(--primary-blue);
        font-weight: 600;
    }

    /* Streamlit Components overrides */
    div[data-testid="stExpander"] {
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        background-color: white;
    }
    
    /* Remove white text forcing from previous theme */
    button { color: unset !important; }
    .stButton > button { color: white !important; }

    /* File Uploader Fix */
    [data-testid="stFileUploader"] {
        background-color: #f9fafb;
        border: 1px dashed #d1d5db;
        border-radius: 0.5rem;
        padding: 1rem;
    }
    
    [data-testid="stFileUploader"] div {
        color: var(--text-dark) !important;
        background-color: transparent !important;
    }
    
    [data-testid="stFileUploader"] section {
        background-color: #f9fafb !important;
    }
    
    [data-testid="stFileUploader"] button {
        color: var(--text-dark) !important;
    }
    
    [data-testid="stFileUploader"] span {
        color: var(--text-gray) !important;
    }
    
</style>
""", unsafe_allow_html=True)


def apply_login_button_styling():
    """
    Apply special styling to login button.
    """
    st.markdown("""
<style>
    /* Specific selector for login button if identifiable */
</style>
<script>
    const buttons = window.parent.document.querySelectorAll('button');
    buttons.forEach(button => {
        if (button.textContent.includes('Login')) {
            button.style.backgroundColor = '#2563eb';
            button.style.color = 'white';
            button.style.borderRadius = '9999px';
            button.style.padding = '0.5rem 1.5rem';
            button.style.border = 'none';
        }
    });
</script>
""", unsafe_allow_html=True)


def force_orange_button():
    """
    Force orange button styling for analyze.
    """
    st.markdown("""
<script>
    function forceOrangeButton() {
        const forms = window.parent.document.querySelectorAll('[data-testid="stForm"]');
        forms.forEach(form => {
            const buttons = form.querySelectorAll('button');
            buttons.forEach(btn => {
                btn.style.setProperty('background', 'linear-gradient(138deg, #ff6b35 0%, #f7931e 100%)', 'important');
                btn.style.setProperty('color', 'white', 'important');
                btn.style.setProperty('border-radius', '0.75rem', 'important');
                btn.style.setProperty('font-weight', '700', 'important');
                btn.style.setProperty('border', 'none', 'important');
                btn.style.setProperty('box-shadow', '0 6px 20px rgba(255, 107, 53, 0.4)', 'important');
                btn.style.setProperty('transition', 'all 0.2s ease-in-out', 'important');
            });
        });
    }
    
    forceOrangeButton();
    setTimeout(forceOrangeButton, 500);
</script>
""", unsafe_allow_html=True)


def apply_analyze_button_css():
    """
    Apply css for analyze button.
    """
    st.markdown("""
<style>
    div[data-testid="stForm"] button {
        background: linear-gradient(138deg, #ff6b35 0%, #f7931e 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 0.75rem !important;
        width: 100%;
        box-shadow: 0 4px 14px 0 rgba(194, 106, 60, 0.39) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stForm"] button:hover {
        background: linear-gradient(90deg, #b05c30 0%, #c97d42 100%) !important;
        box-shadow: 0 6px 20px rgba(194, 106, 60, 0.23) !important;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)


def fix_sidebar_and_text_colors():
    """
    Helper to ensure text colors are correct.
    """
    # Most logic moved to CSS above, this is for safety
    pass
