import streamlit as st
import plotly.graph_objects as go

def inject_cyber_css():
    """Injects all Hacker/Cyber CSS styling."""
    st.markdown("""
    <style>
        .stApp { background-color: #0a0e17; color: #c9d1d9; font-family: 'Courier New', Courier, monospace; }
        h1, h2, h3 { color: #00ff41 !important; text-shadow: 0 0 5px rgba(0, 255, 65, 0.5); font-weight: 800 !important; text-transform: uppercase; }
        .cyber-terminal {
            background-color: #010409; border: 1px solid #30363d; border-left: 4px solid #00ff41;
            padding: 15px; border-radius: 5px; color: #00ff41; font-size: 14px;
            box-shadow: inset 0 0 10px rgba(0,255,65,0.05); height: 250px; overflow-y: auto; white-space: pre-wrap;
        }
        .report-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; color: #c9d1d9; font-family: 'Inter', sans-serif; }
        .alert-border { border-top: 4px solid #ff003c; box-shadow: 0 0 15px rgba(255,0,60,0.1); }
        .suspicious-border { border-top: 4px solid #ffa500; box-shadow: 0 0 15px rgba(255,165,0,0.1); }
        .safe-border { border-top: 4px solid #00ff41; box-shadow: 0 0 15px rgba(0,255,65,0.1); }
        
        .critical-alert {
            background: rgba(255, 0, 60, 0.05); border: 1px solid #ff003c; border-left: 5px solid #ff003c;
            padding: 15px; border-radius: 5px; margin-bottom: 20px; animation: pulse 2s infinite;
        }
        .warning-alert {
            background: rgba(255, 165, 0, 0.05); border: 1px solid #ffa500; border-left: 5px solid #ffa500;
            padding: 15px; border-radius: 5px; margin-bottom: 20px; color: #ffa500;
        }
        @keyframes pulse { 0% { box-shadow: 0 0 5px rgba(255, 0, 60, 0.2); } 50% { box-shadow: 0 0 20px rgba(255, 0, 60, 0.6); } 100% { box-shadow: 0 0 5px rgba(255, 0, 60, 0.2); } }
        .critical-alert h4 { color: #ff003c !important; margin-top: 0; font-weight: 900;}
        .warning-alert h4 { color: #ffa500 !important; margin-top: 0; font-weight: 900;}
        
        /* --- BUG FIX: CHAT MESSAGE VISIBILITY --- */
        .stChatMessage { background-color: #161b22 !important; border: 1px solid #30363d !important; border-radius: 8px; }
        .stChatMessage, .stChatMessage p, .stChatMessage div { color: #c9d1d9 !important; }
        
        /* --- BUG FIX: CHAT INPUT COMPONENT VISIBILITY --- */
        [data-testid="stChatInput"] { background-color: #010409 !important; border: 1px solid #30363d !important; border-radius: 8px; }
        [data-testid="stChatInput"] textarea { color: #00e5ff !important; font-family: 'Courier New', monospace; }
        [data-testid="stChatInput"] textarea::placeholder { color: #8b949e !important; }
        [data-testid="stChatInputSubmitButton"] { color: #00ff41 !important; }
        [data-testid="stChatInputSubmitButton"] svg { fill: #00ff41 !important; }
        /* Fix the "Press Enter to Send" text */
        [data-testid="stChatInput"] div { color: #8b949e !important; }

        .stButton>button { background-color: transparent; color: #00ff41; border: 1px solid #00ff41; border-radius: 4px; padding: 8px 16px; text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s ease; }
        .stButton>button:hover { background-color: #00ff41; color: #0a0e17; box-shadow: 0 0 10px #00ff41; }
        .stTextArea textarea { background-color: #010409; color: #00e5ff; border: 1px solid #30363d; font-family: 'Courier New', monospace; }
        .stTextArea textarea:focus { border-color: #00e5ff; box-shadow: 0 0 5px rgba(0,229,255,0.5); }
    </style>
    """, unsafe_allow_html=True)

def render_system_status():
    st.markdown("<div style='text-align:center; padding-top:20px;'><h3 style='color:#00e5ff;'>SYSTEM STATUS</h3><p>RAG Engine: <b style='color:#00ff41;'>ONLINE</b></p><p>Memory Index: <b style='color:#00ff41;'>ACTIVE</b></p></div>", unsafe_allow_html=True)

def get_terminal_html(log_history):
    return f"<div class='cyber-terminal'>{log_history}</div>"

def render_critical_alert(user_name):
    st.markdown(f"""
    <div class="critical-alert">
        <h4>🚨 CRITICAL ALERT: REPEAT OFFENDER DETECTED</h4>
        <p>Target entity <b>'{user_name}'</b> has a verified history of malicious activity in the system logs. Immediate containment protocol recommended.</p>
    </div>
    """, unsafe_allow_html=True)

def render_warning_alert(user_name):
    st.markdown(f"""
    <div class="warning-alert">
        <h4>⚠ SYSTEM NOTIFICATION: REPEAT ACTIVITY</h4>
        <p>User <b>'{user_name}'</b> has previous recorded activity in the system memory index.</p>
    </div>
    """, unsafe_allow_html=True)

def render_report_card(report_text, classification):
    if classification == "HIGH RISK":
        border_class = 'alert-border'
    elif classification == "SUSPICIOUS":
        border_class = 'suspicious-border'
    else:
        border_class = 'safe-border'
        
    st.markdown(f"<div class='report-card {border_class}'>", unsafe_allow_html=True)
    st.markdown(report_text)
    st.markdown('</div>', unsafe_allow_html=True)

def get_risk_gauges(risk_score_100):
    """Generates continuous Plotly Risk Visualizations based on probabilistic score."""
    overall_risk = int(risk_score_100)
    
    if overall_risk < 45:
        gauge_color = "#00ff41" # Green
        fill_color = "rgba(0, 255, 65, 0.2)"
    elif overall_risk < 75:
        gauge_color = "#ffa500" # Orange
        fill_color = "rgba(255, 165, 0, 0.2)"
    else:
        gauge_color = "#ff003c" # Red
        fill_color = "rgba(255, 0, 60, 0.2)"
        
    impact_score = min(100, overall_risk + 10)
    anomaly_score = overall_risk
    stealth_score = max(10, overall_risk - 15)
    
    gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = overall_risk,
        title = {'text': "PROBABILISTIC THREAT SCORE", 'font': {'color': "#00ff41", 'size': 14}},
        number = {'font': {'color': "#c9d1d9"}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "#30363d"},
            'bar': {'color': gauge_color},
            'bgcolor': "rgba(0,0,0,0)",
            'steps': [
                {'range': [0, 44], 'color': "rgba(0, 255, 65, 0.05)"},
                {'range': [45, 74], 'color': "rgba(255, 165, 0, 0.05)"},
                {'range': [75, 100], 'color': "rgba(255, 0, 60, 0.05)"}
            ]
        }
    ))
    gauge.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#c9d1d9"})

    radar = go.Figure(data=go.Scatterpolar(
        r=[impact_score, anomaly_score, stealth_score, overall_risk],
        theta=['Asset Impact', 'Behavior Anomaly', 'Technique Stealth', 'Overall Risk'],
        fill='toself', fillcolor=fill_color, line=dict(color=gauge_color)
    ))
    radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], color="#c9d1d9"), bgcolor="rgba(0,0,0,0)"),
        showlegend=False, height=250, margin=dict(l=40, r=40, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#c9d1d9"}
    )
    
    return gauge, radar