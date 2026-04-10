import streamlit as st
from ui.layout_main import render_landing_page

# Set the wide page config as the very first command
st.set_page_config(page_title="SOC Mission Control", layout="wide", page_icon="🛡️")

# 1. Initialize Authentication State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 2. Gatekeeper Logic
if not st.session_state.authenticated:
    # If not logged in, render the login page ONLY
    login_page = st.Page(render_landing_page, title="System Authentication", icon="🔒")
    pg = st.navigation([login_page])
    pg.run()
    
else:
    # If logged in, unlock the standard SOC navigation pages
    mode1 = st.Page("modules/cohensive.py", title="Tactical Analyst (M1)", icon="⚡")
    mode2 = st.Page("modules/threat.py", title="Proactive Threat (M2)", icon="🌐")
    mode3 = st.Page("modules/recom.py", title="Strategic Copilot (M3)", icon="🧠")
    
    # Optional Sidebar Profile/Logout Box
    st.sidebar.markdown(f"### 👤 Logged in as: **{st.session_state.current_user}**")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.rerun()
        
    st.sidebar.markdown("---")
    
    # Run standard navigation
    pg = st.navigation({
        "SOC Operations": [mode1, mode2, mode3]
    })
    
    pg.run()