import streamlit as st
from config import COLORS, APP_NAME, APP_TAGLINE

def set_page(page_name):
    st.session_state.current_page = page_name

def render_header():
    """
    Render custom header with pill navigation using st.button and session state.
    """
    current_page = st.session_state.get('current_page', 'upload')
    
    st.markdown(f"""
    <style>
        .header-row {{
            display: flex;
            align-items: center;
            gap: 1.25rem;
            margin: 0.75rem 0 1.25rem 0;
        }}
        
        /* 1. Container Style (Gradient) */
        /* We can't easily target the container of the buttons without a custom component or unsafe hacks.
           We'll rely on global button styling for pill shape. */

        /* 2. Button Styling */
        div.stButton > button {{
            border-radius: 999px !important;
            border: 2px solid transparent !important;
            font-weight: 600 !important;
            width: 100%;
        }}
        
        div.stButton > button:hover {{
            transform: scale(1.05);
            background-color: rgba(255,255,255,0.4) !important;
        }}
        
        /* Active Tab (Primary) - Dark Blue Bg, White Text */
        div.stButton > button[kind="primary"] {{
            background-color: #1f77b4 !important;
            color: #ffffff !important;
            border: 2px solid #1f77b4 !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        div.stButton > button[kind="primary"]:hover {{
            background-color: #155a8a !important;
            color: #ffffff !important;
        }}

        /* Inactive Tab (Secondary) - Transparent/Light Bg */
        div.stButton > button[kind="secondary"] {{
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%) !important;
            color: #0f3d6b !important;
            border: none !important;
        }}
    </style>
    
    <div class="header-row">
      <div style="line-height: 1.1;">
        <div style="font-size: 2.5rem; font-weight: 900; color: #1f77b4; margin: 0;">{APP_NAME}</div>
        <div style="font-size: 0.9rem; color: #6b7280; margin-top: 0.25rem;">{APP_TAGLINE}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        # Inject styles specifically for this container? Difficult.
        # We rely on the global 'kind' targeting defined above.

        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
        
        with c1:
            # UPLOAD
            t_upload = "primary" if current_page == "upload" else "secondary"
            st.button("📤 Upload", key="nav_upload", type=t_upload, use_container_width=True, on_click=set_page, args=("upload",))
            
        with c2:
            # DASHBOARD
            t_dash = "primary" if current_page == "dashboard" else "secondary"
            st.button("📊 Dashboard", key="nav_dashboard", type=t_dash, use_container_width=True, on_click=set_page, args=("dashboard",))
            
        with c3:
            # ABOUT
            t_about = "primary" if current_page == "about" else "secondary"
            st.button("ℹ️ About", key="nav_about", type=t_about, use_container_width=True, on_click=set_page, args=("about",))
            
        with c4:
            # LOGIN
            t_login = "primary" if current_page == "login" else "secondary"
            st.button("Login", key="nav_login", type=t_login, use_container_width=True, on_click=set_page, args=("login",))

    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
