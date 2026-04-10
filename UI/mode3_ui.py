import streamlit as st
import plotly.graph_objects as go

def inject_mode3_css():
    """Injects sleek, unbreakable pitch-black CSS and permanently fixes Chat Input visibility."""
    st.markdown("""
    <style>
        /* Unbreakable Pitch Black Override */
        body, html, #root, .stApp, .main, [data-testid="stAppViewContainer"], 
        [data-testid="stAppViewBlockContainer"], [data-testid="stHeader"],
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child { 
            background-color: #000000 !important; 
            background: #000000 !important;
            background-image: none !important;
        }
        
        /* Sidebar Border */
        [data-testid="stSidebar"] {
            border-right: 1px solid #8A2BE2 !important;
        }

        /* Text Visibility */
        p, span, div, li, label, h1, h2, h3, h4, h5, h6, 
        [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span { 
            color: #FFFFFF !important; 
        }
        
        h1, h2, h3 { 
            font-weight: 900 !important; 
            letter-spacing: 1px !important; 
            text-shadow: 0 0 15px #8A2BE2 !important; 
            text-transform: uppercase;
        }

        /* Dashboard Panels */
        .dashboard-panel { 
            background-color: #050505 !important; 
            border: 2px solid #8A2BE2 !important; 
            border-radius: 12px; 
            padding: 20px; 
            box-shadow: 0 0 25px rgba(138, 43, 226, 0.2), inset 0 0 15px rgba(0, 255, 204, 0.1) !important; 
            margin-bottom: 20px; 
        }

        /* Generate Recommendations Button */
        .stButton > button {
            background: linear-gradient(90deg, #8A2BE2, #FF007F) !important;
            color: #FFFFFF !important;
            font-weight: 900 !important;
            font-size: 1.1rem !important;
            border: 1px solid #FFFFFF !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            box-shadow: 0 0 20px #8A2BE2 !important;
            transition: all 0.2s ease-in-out !important;
            text-transform: uppercase;
            width: 100%;
        }
        .stButton > button:hover {
            transform: scale(1.01) !important;
            background: linear-gradient(90deg, #FF007F, #00FFCC) !important;
            box-shadow: 0 0 30px #00FFCC !important;
            border-color: #00FFCC !important;
        }
        
        /* Suggested Query Buttons */
        div[data-testid="stVerticalBlock"] .stButton > button {
            background: #0A0A0A !important;
            color: #00FFCC !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            border: 1px solid #00FFCC !important;
            box-shadow: none !important;
            text-transform: none !important;
            text-align: left !important;
            padding: 8px 15px !important;
        }
        div[data-testid="stVerticalBlock"] .stButton > button:hover {
            background: rgba(0, 255, 204, 0.1) !important;
            box-shadow: 0 0 15px rgba(0, 255, 204, 0.4) !important;
            transform: translateX(5px) !important;
        }

        /* =======================================================
           CHAT INPUT VISIBILITY FIX (BULLETPROOF)
           ======================================================= */
        /* 1. Main Outer Container */
        [data-testid="stChatInput"] { 
            background-color: #0A0A0A !important; 
            border: 2px solid #8A2BE2 !important; 
            border-radius: 10px; 
        }
        /* 2. Inner wrapper backgrounds forced transparent */
        [data-testid="stChatInput"] > div, 
        [data-testid="stChatInput"] > div > div {
            background-color: transparent !important;
        }
        /* 3. Force all text to be bright white */
        [data-testid="stChatInput"] * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }
        /* 4. The actual typing area */
        [data-testid="stChatInput"] textarea { 
            background-color: #0A0A0A !important;
            caret-color: #00FFCC !important; /* Glowing Neon Cyan Cursor */
            font-size: 1.1rem !important;
            font-weight: 700 !important; /* Make text bolder */
        }
        /* 5. Placeholder text */
        [data-testid="stChatInput"] textarea::placeholder {
            color: #888888 !important;
            -webkit-text-fill-color: #888888 !important;
            font-weight: 400 !important;
        }
        /* 6. Send Button Icon */
        [data-testid="stChatInput"] button svg {
            fill: #00FFCC !important;
            color: #00FFCC !important;
        }
        
        /* Chat Avatar Colors */
        [data-testid="chatAvatarIcon-user"] { background-color: #00FFCC !important; }
        [data-testid="chatAvatarIcon-assistant"] { background-color: #8A2BE2 !important; }
        
        /* Bring app content to the very front */
        .main .block-container { position: relative; z-index: 9999 !important; }
    </style>
    """, unsafe_allow_html=True)

def render_dashboard_visuals(stats):
    """Renders the 3 dynamic charts with native HTML headers to prevent Plotly truncation."""
    col1, col2, col3 = st.columns(3)
    
    # 1. Incident Distribution (Pie Chart)
    with col1:
        st.markdown("<h4 style='text-align:center; color:#FFFFFF; font-family:\"Arial Black\"; font-size:14px; margin-bottom:0;'>INCIDENT DISTRIBUTION</h4>", unsafe_allow_html=True)
        if stats['total_incidents'] > 0:
            donut = go.Figure(data=[go.Pie(
                labels=['Verified Attacks', 'Benign Activity'], values=[stats['malicious'], stats['benign']],
                hole=.5, marker_colors=['#FF003C', '#00FFCC'], textinfo='percent',
                textfont=dict(color="#FFFFFF", size=14, family="Arial Black")
            )])
            donut.update_layout(
                height=220, margin=dict(l=10, r=10, t=10, b=40), paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, font=dict(color="#FFFFFF"))
            )
            st.plotly_chart(donut, use_container_width=True)

    # 2. Targeted Hosts (Bar Chart)
    with col2:
        st.markdown("<h4 style='text-align:center; color:#FFFFFF; font-family:\"Arial Black\"; font-size:14px; margin-bottom:0;'>TOP TARGETED HOSTS</h4>", unsafe_allow_html=True)
        if not stats['hosts']:
            bar_hosts = go.Figure()
            bar_hosts.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=40), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(bar_hosts, use_container_width=True)
        else:
            hosts = list(stats['hosts'].keys())
            counts = list(stats['hosts'].values())
            bar_hosts = go.Figure(data=[go.Bar(x=hosts, y=counts, marker_color="#8A2BE2", text=counts, textposition='outside', textfont=dict(color="#FFFFFF", family="Arial Black"))])
            bar_hosts.update_layout(
                height=220, margin=dict(l=10, r=10, t=20, b=40), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(visible=False), xaxis=dict(tickangle=-25, tickfont=dict(color='#FFFFFF', size=11, family="Arial Black"))
            )
            st.plotly_chart(bar_hosts, use_container_width=True)

    # 3. Frequent Attack Tools (Bar Chart)
    with col3:
        st.markdown("<h4 style='text-align:center; color:#FFFFFF; font-family:\"Arial Black\"; font-size:14px; margin-bottom:0;'>FREQUENT ATTACK TOOLS</h4>", unsafe_allow_html=True)
        if not stats['tools']:
            bar_tools = go.Figure()
            bar_tools.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=40), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(bar_tools, use_container_width=True)
        else:
            tools = list(stats['tools'].keys())
            counts = list(stats['tools'].values())
            bar_tools = go.Figure(data=[go.Bar(x=tools, y=counts, marker_color="#FF007F", text=counts, textposition='outside', textfont=dict(color="#FFFFFF", family="Arial Black"))])
            bar_tools.update_layout(
                height=220, margin=dict(l=10, r=10, t=20, b=40), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(visible=False), xaxis=dict(tickangle=-25, tickfont=dict(color='#FFFFFF', size=11, family="Arial Black"))
            )
            st.plotly_chart(bar_tools, use_container_width=True)