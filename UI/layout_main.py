import streamlit as st
import base64
import os
from modules.auth import verify_user, register_user

def set_video_background(video_path):
    """Reads a local video file and sets it as a highly visible fixed fullscreen background."""
    try:
        with open(video_path, 'rb') as video_file:
            video_bytes = video_file.read()
        
        encoded_video = base64.b64encode(video_bytes).decode()
        
        video_html = f"""
        <style>
            #bg-video {{
                position: fixed;
                right: 0;
                bottom: 0;
                min-width: 100%;
                min-height: 100%;
                z-index: -1;
                object-fit: cover;
                opacity: 0.95; 
                filter: brightness(0.85) contrast(1.1); 
            }}
            /* Force Streamlit's default backgrounds to be fully transparent */
            .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {{
                background: transparent !important;
                background-color: transparent !important;
            }}
        </style>
        <video autoplay loop muted playsinline id="bg-video">
            <source src="data:video/mp4;base64,{encoded_video}" type="video/mp4">
        </video>
        """
        st.markdown(video_html, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"⚠️ Video file not found at: {video_path}. Please ensure 'robot.mp4' is inside the 'ui' folder.")

def inject_landing_css():
    """Dark cyberpunk styling with Dark Golden landing accents and Deep Blue Auth styling."""
    st.markdown("""
    <style>
        /* Base background is strictly pitch black */
        body, html, .stApp, .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { 
            background-color: #000000 !important; 
            background: #000000 !important;
        }
        
        /* Hide sidebar on login page */
        [data-testid="stSidebar"] { display: none !important; }
        
        /* Typography & Glow Effects */
        h1.main-title { 
            font-size: 3.5rem !important;
            font-weight: 900 !important;
            text-align: center;
            color: #FFFFFF !important;
            text-transform: uppercase;
            letter-spacing: 4px;
            text-shadow: 0 0 15px #000000, 0 0 20px #00FFCC; 
            margin-top: 0px !important;
            margin-bottom: 5px !important;
        }
        h3.subtitle {
            text-align: center; 
            color: #00FFCC !important; 
            font-size: 1.2rem !important; 
            font-weight: bold;
            letter-spacing: 2px;
            text-shadow: 0 0 10px #000000;
            margin-bottom: 20px !important;
        }
        
        /* Transparent Glass Feature Cards */
        .feature-card {
            background: rgba(5, 5, 8, 0.6); 
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(184, 134, 11, 0.4); 
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            height: 100%;
        }
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 25px rgba(218, 165, 32, 0.5); 
            border-color: #FFD700;
            background: rgba(10, 10, 15, 0.8);
        }
        .feature-card h4 { color: #FFD700 !important; font-weight: bold; font-size: 1.2rem; margin-bottom: 10px; text-shadow: 0 2px 4px #000000; }
        .feature-card p { color: #E2E8F0 !important; font-size: 0.95rem; line-height: 1.5; text-shadow: 0 1px 3px #000000; }

        /* =======================================================
           STREAMLIT NATIVE FORM STYLING
           ======================================================= */
        [data-testid="stForm"] {
            background: linear-gradient(145deg, rgba(10, 15, 30, 0.9), rgba(5, 5, 10, 0.9)) !important; 
            border: 1px solid rgba(30, 58, 138, 0.6) !important; 
            border-radius: 16px !important;
            padding: 30px !important;
            padding-bottom: 40px !important; /* Added extra padding to stop button clipping */
            box-shadow: 0 0 30px rgba(30, 58, 138, 0.2), inset 0 0 15px rgba(0, 255, 204, 0.05) !important;
        }
        
        /* Streamlit Tabs Styling */
        [data-testid="stTabs"] button {
            color: #94A3B8 !important;
            font-weight: bold !important;
            font-size: 1.1rem !important;
            border-bottom: 2px solid transparent !important;
            background: transparent !important;
        }
        [data-testid="stTabs"] button[aria-selected="true"] {
            color: #00FFCC !important;
            border-bottom: 2px solid #00FFCC !important;
            text-shadow: 0 0 10px rgba(0, 255, 204, 0.5) !important;
        }

        /* Input Styling */
        [data-testid="stTextInput"] input {
            background-color: rgba(0, 0, 0, 0.5) !important; 
            color: #00FFCC !important;
            -webkit-text-fill-color: #00FFCC !important;
            border: 1px solid rgba(30, 58, 138, 0.8) !important; 
            border-radius: 8px !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            caret-color: #00FFCC !important;
            padding: 10px !important;
        }
        [data-testid="stTextInput"] input:focus {
            border-color: #00FFCC !important;
            box-shadow: 0 0 15px rgba(0, 255, 204, 0.3) !important;
            background-color: #000000 !important;
        }
        [data-testid="stTextInput"] input::placeholder { color: #475569 !important; -webkit-text-fill-color: #475569 !important; }
        [data-testid="stTextInput"] label p { 
            color: #E2E8F0 !important; 
            font-weight: bold !important; 
            font-size: 0.95rem !important;
            margin-bottom: 2px !important;
        }

        /* =======================================================
           BUTTON STYLING (Primary = Blue/Cyan, Secondary = Abort)
           ======================================================= */
        /* Aggressively target the form submit button to override Streamlit's hollow style */
        [data-testid="stFormSubmitButton"] button, 
        button[kind="primary"] {
            background: linear-gradient(135deg, #020617 0%, #1E3A8A 100%) !important; /* Deep glowing blue */
            color: #00FFCC !important;
            font-weight: 900 !important;
            font-size: 1.2rem !important;
            border: 1px solid #3B82F6 !important; 
            border-radius: 8px !important;
            padding: 12px 24px !important; /* Made the button taller */
            text-transform: uppercase;
            letter-spacing: 2px;
            box-shadow: 0 0 20px rgba(37, 99, 235, 0.6), inset 0 0 10px rgba(0, 255, 204, 0.2) !important;
            transition: all 0.3s ease;
            margin-top: 15px !important; /* Push it down slightly from the text box */
            width: 100% !important; 
        }
        [data-testid="stFormSubmitButton"] button:hover, 
        button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%) !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 30px rgba(0, 255, 204, 0.8) !important;
            border-color: #00FFCC !important;
        }
        
        /* Top Right Landing Page Button Override */
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] button[kind="primary"] {
            background: linear-gradient(135deg, #0A0A0A 20%, #8B6508 100%) !important; /* Gold landing button */
            color: #FFD700 !important;
            border-color: #B8860B !important;
            box-shadow: 0 0 15px rgba(184, 134, 11, 0.6) !important;
            font-size: 1.1rem !important;
        }
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] button[kind="primary"]:hover {
            background: linear-gradient(135deg, #111111 0%, #DAA520 100%) !important;
            color: #000000 !important;
            box-shadow: 0 0 25px rgba(255, 215, 0, 0.8) !important;
            border-color: #FFD700 !important;
        }
        
        /* Secondary Button (Stylish Abort Button) */
        button[kind="secondary"] {
            background: linear-gradient(90deg, #0f172a, #1e293b) !important; 
            color: #94A3B8 !important;
            font-weight: 800 !important;
            font-size: 1rem !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
            transition: all 0.3s ease;
        }
        button[kind="secondary"]:hover {
            color: #EF4444 !important; /* Turns bright Red on hover to indicate 'Abort' */
            border-color: #EF4444 !important;
            box-shadow: 0 0 20px rgba(239, 68, 68, 0.4) !important;
            background: rgba(239, 68, 68, 0.1) !important;
        }
        
        .main .block-container { position: relative; z-index: 10 !important; padding-top: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

def render_landing_page():
    # Inject baseline CSS
    inject_landing_css()
    
    # Session state to toggle visibility of the login form
    if "show_auth_panel" not in st.session_state:
        st.session_state.show_auth_panel = False
    
    # ==========================================
    # STATE 1: DEFAULT LANDING PAGE (WITH VIDEO)
    # ==========================================
    if not st.session_state.show_auth_panel:
        # INJECT VIDEO ONLY ON LANDING PAGE
        video_path = os.path.join(os.path.dirname(__file__), "robot.mp4")
        set_video_background(video_path)

        # 1. Login Button at the TOP RIGHT (Golden)
        col_empty, col_btn = st.columns([5, 1])
        with col_btn:
            if st.button("🔐 SECURE LOGIN", type="primary", use_container_width=True):
                st.session_state.show_auth_panel = True
                st.rerun()

        # 2. Main Titles
        st.markdown("<h1 class='main-title'>Self Evolving SOC Analyst</h1>", unsafe_allow_html=True)
        st.markdown("<h3 class='subtitle'>NEXT-GENERATION AI SECURITY OPERATIONS CENTER</h3>", unsafe_allow_html=True)
        
        # 3. Vertical Spacer (Pushes feature cards down to reveal robot face)
        st.markdown("<div style='height: 35vh;'></div>", unsafe_allow_html=True)
        
        # 4. Mode Details at the bottom
        st.markdown("<div style='max-width: 1100px; margin: 0 auto;'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h4>⚡ MODE 1: Tactical Analyst</h4>
                <p>Real-time log ingestion and anomaly detection. Employs neural triage and heuristic rules to instantly classify high-risk commands.</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h4>🌐 MODE 2: Proactive Threat</h4>
                <p>Ingests global CVE intelligence. Mathematically cross-references threats against internal asset inventory to calculate exposure risk.</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h4>🧠 MODE 3: Strategic Copilot</h4>
                <p>Interactive Agentic RAG interface. Query historical incident memory and retrieve instant mitigation strategies from the SOC playbook.</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # STATE 2: AUTHENTICATION PANEL (NO VIDEO)
    # ==========================================
    else:
        st.markdown("<h1 class='main-title' style='margin-top: 0px !important;'>Self Evolving SOC Analyst</h1>", unsafe_allow_html=True)
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        # Stylish Abort Button Centered above the form
        back_col1, back_col2, back_col3 = st.columns([1, 1, 1])
        with back_col2:
            if st.button("🚫 ABORT LOGIN SEQUENCE", use_container_width=True):
                st.session_state.show_auth_panel = False
                st.rerun()

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # 🚀 Wrapping the forms in columns perfectly controls their width
        space_left, form_col, space_right = st.columns([1, 1.3, 1])
        
        with form_col:
            tab_login, tab_register = st.tabs(["🔒 SECURE LOGIN", "🛡️ REQUEST CLEARANCE"])
            
            # --- LOGIN TAB ---
            with tab_login:
                # border=True triggers our custom CSS background box
                with st.form("login_form", clear_on_submit=True, border=True):
                    username = st.text_input("Operator Callsign (Username)", placeholder="e.g., admin")
                    password = st.text_input("Passphrase", type="password", placeholder="Enter your secure password")
                    
                    # Added a break for visual spacing before the button
                    st.markdown("<br>", unsafe_allow_html=True)
                    submitted_login = st.form_submit_button("INITIALIZE UPLINK", type="primary", use_container_width=True)
                    
                    if submitted_login:
                        user_data = verify_user(username, password)
                        if user_data:
                            st.session_state.authenticated = True
                            st.session_state.current_user = user_data['username']
                            st.session_state.show_auth_panel = False # reset for next logout
                            st.rerun() 
                        else:
                            st.error("❌ Invalid Credentials. Access Denied.")
                            
            # --- SIMPLIFIED REGISTRATION TAB ---
            with tab_register:
                with st.form("register_form", clear_on_submit=True, border=True):
                    st.markdown("<p style='color:#00FFCC; text-align:center; font-size:0.85rem; margin-top:-10px; margin-bottom:10px;'>* Provisioning requires a valid SOC Clearance Code.</p>", unsafe_allow_html=True)
                    
                    reg_username = st.text_input("Desired Callsign (Username)", placeholder="e.g., CyberGhost")
                    reg_password = st.text_input("Create Passphrase", type="password", placeholder="Strong password required")
                    reg_code = st.text_input("Secret Clearance Code", type="password", placeholder="Enter authorization key")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    submitted_register = st.form_submit_button("PROVISION SOC ACCOUNT", type="primary", use_container_width=True)
                    
                    if submitted_register:
                        success, message = register_user(reg_username, reg_password, reg_code)
                        if success:
                            st.success(message)
                            st.info("Account created. Please switch to 'SECURE LOGIN' to access the terminal.")
                        else:
                            st.error(message)