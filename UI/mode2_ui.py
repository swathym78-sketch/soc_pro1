import streamlit as st
import plotly.graph_objects as go

def inject_dark_executive_css():
    """ABSOLUTE PITCH BLACK OVERRIDE. Clean, professional, high-contrast UI without floating elements."""
    st.markdown("""
    <style>
        /* =========================================================
           1. UNBREAKABLE PITCH BLACK BACKGROUND OVERRIDES (Includes Sidebar)
           ========================================================= */
        body, html, #root, .stApp, .main, [data-testid="stAppViewContainer"], 
        [data-testid="stAppViewBlockContainer"], [data-testid="stHeader"],
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child { 
            background-color: #000000 !important; 
            background: #000000 !important;
            background-image: none !important;
        }

        /* Sidebar right border separator */
        [data-testid="stSidebar"] {
            border-right: 1px solid #FF003C !important;
        }

        /* =========================================================
           2. FORCE ALL TEXT TO BRIGHT WHITE FOR 100% VISIBILITY
           ========================================================= */
        p, span, div, li, label, 
        [data-testid="stMarkdownContainer"] p, 
        [data-testid="stMarkdownContainer"] span { 
            color: #FFFFFF !important; 
        }
        
        h1, h2, h3, h4, h5, h6 { 
            color: #FFFFFF !important; 
            font-weight: 900 !important; 
            letter-spacing: 2px !important; 
            text-shadow: 0 0 10px rgba(255,0,60,0.8) !important; 
            text-transform: uppercase;
        }

        /* Make Input Labels Super Bright */
        label p, .stTextArea label p, .stRadio label p {
            color: #00FFCC !important;
            font-size: 1.3rem !important;
            font-weight: 900 !important;
            text-shadow: 0 0 10px rgba(0,255,204,0.6) !important;
            letter-spacing: 1px;
        }
        
        /* Bring app content to the very front */
        .main .block-container { position: relative; z-index: 9999 !important; }
        
        /* =========================================================
           3. DASHBOARD PANELS (Pitch Black with Neon Borders)
           ========================================================= */
        .dashboard-panel { 
            background-color: #050505 !important; 
            border: 2px solid #FF007F !important; 
            border-radius: 12px; 
            padding: 30px; 
            box-shadow: 0 0 30px rgba(255, 0, 127, 0.2), inset 0 0 20px rgba(255, 0, 60, 0.1) !important; 
            margin-bottom: 24px; 
        }
        
        /* =========================================================
           4. IMPRESSIVE NEON BUTTONS
           ========================================================= */
        .stButton > button {
            background: linear-gradient(90deg, #FF003C, #FF007F) !important;
            color: #FFFFFF !important;
            font-weight: 900 !important;
            font-size: 1.3rem !important;
            border: 2px solid #FFFFFF !important;
            border-radius: 8px !important;
            padding: 15px 30px !important;
            box-shadow: 0 0 25px #FF003C, 0 0 50px rgba(255,0,127,0.7) !important;
            transition: all 0.2s ease-in-out !important;
            text-transform: uppercase;
            letter-spacing: 3px;
        }
        .stButton > button:hover {
            transform: scale(1.02) !important;
            background: linear-gradient(90deg, #FF007F, #00FFCC) !important;
            box-shadow: 0 0 40px #00FFCC, 0 0 80px #FF007F, inset 0 0 20px rgba(255,255,255,0.8) !important;
            border-color: #00FFCC !important;
        }
        
        /* =========================================================
           5. DYNAMIC BANNERS
           ========================================================= */
        .banner-critical { background: #050000; border-left: 8px solid #FF003C; padding: 25px; border-radius: 8px; box-shadow: 0 0 30px rgba(255,0,60,0.5); }
        .banner-high { background: #050005; border-left: 8px solid #FF007F; padding: 25px; border-radius: 8px; box-shadow: 0 0 30px rgba(255,0,127,0.5); }
        .banner-medium { background: #050200; border-left: 8px solid #FF5500; padding: 25px; border-radius: 8px; box-shadow: 0 0 20px rgba(255,85,0,0.4); }
        .banner-low { background: #000505; border-left: 8px solid #00FFCC; padding: 25px; border-radius: 8px; box-shadow: 0 0 20px rgba(0,255,204,0.4); }
        
        .banner-title { font-size: 32px; font-weight: 900; margin-bottom: 12px; color: #FFFFFF !important; text-shadow: 0 0 15px currentColor; letter-spacing: 2px;}
        .banner-desc { font-size: 19px; color: #FFFFFF !important; margin: 0; font-weight: 700; line-height: 1.6; }
        
        /* =========================================================
           6. ASSET GRID CARDS
           ========================================================= */
        .asset-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; margin-top: 20px; }
        .asset-card { background-color: #050505 !important; border: 2px solid #FF003C; border-top: 6px solid #FF007F; padding: 20px; border-radius: 8px; transition: all 0.3s ease; box-shadow: inset 0 0 20px rgba(255,0,60,0.3); }
        .asset-card:hover { transform: translateY(-5px); box-shadow: 0 0 30px rgba(255,0,127,0.6); border-color: #00FFCC; border-top-color: #00FFCC;}
        
        /* =========================================================
           7. INPUT TEXT AREA, ALERTS & EXPANDERS
           ========================================================= */
        [data-testid="stTextArea"] textarea { 
            background-color: #000000 !important; 
            color: #00FFCC !important; 
            border: 2px solid #FF003C !important; 
            font-size: 1.2rem !important; 
            font-weight: 700 !important; 
            box-shadow: inset 0 0 30px rgba(255,0,60,0.4) !important; 
        }
        [data-testid="stTextArea"] textarea:focus {
            border-color: #00FFCC !important;
            box-shadow: 0 0 40px #00FFCC !important;
        }

        /* Fix Streamlit Info/Alert Boxes (Used in Sidebar) */
        [data-testid="stAlert"] {
            background-color: #0A0A0A !important;
            border: 1px solid #00FFCC !important;
            border-radius: 8px;
            box-shadow: inset 0 0 10px rgba(0,255,204,0.2) !important;
        }
        [data-testid="stAlert"] div[data-testid="stMarkdownContainer"] p {
            color: #00FFCC !important;
            font-weight: bold !important;
            text-shadow: none !important;
        }
        
        /* Expanders */
        .streamlit-expanderHeader { color: #00FFCC !important; font-weight: 900 !important; font-size: 1.2rem !important; background: #050505 !important; border: 2px solid #FF003C !important; border-radius: 5px; }
        .streamlit-expanderContent { color: #FFFFFF !important; background: #000000 !important; border: 2px solid #FF003C !important; border-top: none !important; }
        
        /* JSON & Code Blocks */
        .stJson, .stCodeBlock, pre, code { 
            background-color: #000000 !important; 
            border-radius: 8px; 
            padding: 15px; 
            border: 2px solid #00FFCC !important; 
            box-shadow: inset 0 0 20px rgba(0,255,204,0.2) !important; 
            color: #FFFFFF !important;
        }
        
        /* View Toggle Radio Buttons */
        div[data-testid="stRadio"] > div { background: #000000; padding: 10px 20px; border-radius: 8px; display: inline-flex; border: 2px solid #FF007F; box-shadow: 0 0 25px rgba(255,0,127,0.5); }
        div[data-testid="stRadio"] label p { color: #FFFFFF !important; font-weight: 900 !important; text-shadow: none !important;}
    </style>
    """, unsafe_allow_html=True)

def get_color_scheme(level):
    if level == "CRITICAL": return "#FF003C", "banner-critical", "rgba(255, 0, 60, 0.1)"
    if level == "HIGH": return "#FF007F", "banner-high", "rgba(255, 0, 127, 0.1)"
    if level == "MEDIUM": return "#FF5500", "banner-medium", "rgba(255, 85, 0, 0.1)"
    return "#00FFCC", "banner-low", "rgba(0, 255, 204, 0.1)"

def render_executive_banner(level, score, affected_count):
    color, css_class, _ = get_color_scheme(level)
    
    if level == "CRITICAL":
        story = f"CRITICAL EXPOSURE DETECTED. {affected_count} internal systems are highly vulnerable to this exploit. IMMEDIATE EMERGENCY ACTION REQUIRED."
    elif level == "HIGH":
        story = f"HIGH EXPOSURE DETECTED. {affected_count} systems match this threat profile. Prioritize lockdown and patching."
    elif level == "MEDIUM":
        story = f"Moderate exposure. {affected_count} systems have partial matches to this threat. Routine patch management applies."
    else:
        story = "No significant exposure. Current asset inventory does not match the published threat indicators. Safe to monitor."

    st.markdown(f"""<div class="{css_class}">
<div class="banner-title" style="color: {color};">⚠️ SYSTEM EXPOSURE STATUS: {level}</div>
<p class="banner-desc">{story}</p>
</div>""", unsafe_allow_html=True)

def render_impact_visualizations(score, affected_count, total_count, matched_assets, color):
    col1, col2, col3 = st.columns(3)
    score_100 = int(score * 100)
    safe_count = max(0, total_count - affected_count)
    
    # 1. GAUGE CHART
    with col1:
        gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = score_100,
            title = {'text': "THREAT THERMOMETER", 'font': {'color': "#FFFFFF", 'size': 16, 'family': "Arial Black"}},
            number = {'font': {'color': color, 'size': 40, 'family': "Arial Black"}},
            gauge = {
                'axis': {'range': [0, 100], 'tickcolor': "#FF003C", 'tickwidth': 2},
                'bar': {'color': color, 'thickness': 0.8},
                'bgcolor': "#111111",
                'borderwidth': 3,
                'bordercolor': "#FF003C",
                'steps': [
                    {'range': [0, 30], 'color': "rgba(0, 255, 204, 0.3)"},
                    {'range': [30, 80], 'color': "rgba(255, 0, 127, 0.3)"},
                    {'range': [80, 100], 'color': "rgba(255, 0, 60, 0.5)"}
                ]
            }
        ))
        gauge.update_layout(height=280, margin=dict(l=20, r=20, t=60, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#FFFFFF"})
        st.plotly_chart(gauge, use_container_width=True)

    # 2. DONUT CHART
    with col2:
        donut = go.Figure(data=[go.Pie(
            labels=['VULNERABLE', 'SECURE'], values=[affected_count, safe_count],
            hole=.6, marker_colors=[color, '#00FFCC'], textinfo='percent',
            textfont=dict(color="#FFFFFF", size=16, family="Arial Black")
        )])
        donut.update_layout(
            title={'text': "EXPOSURE RATIO", 'font': {'color': "#FFFFFF", 'size': 16, 'family': "Arial Black"}, 'x': 0.5}, 
            height=280, margin=dict(l=20, r=20, t=60, b=50), paper_bgcolor="rgba(0,0,0,0)", 
            showlegend=True, 
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, font=dict(color="#FFFFFF", size=12, family="Arial Black"))
        )
        st.plotly_chart(donut, use_container_width=True)

    # 3. BAR CHART
    with col3:
        if not matched_assets:
            bar = go.Figure()
            bar.update_layout(title={'text': "NO AFFECTED ASSETS", 'font': {'color': "#00FFCC", 'size': 16, 'family': "Arial Black"}, 'x': 0.5}, height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        else:
            hostnames = [a['hostname'] for a in matched_assets[:5]] 
            scores = [a['match_score'] * 100 for a in matched_assets[:5]]
            bar = go.Figure(data=[go.Bar(
                x=hostnames, y=scores, marker_color=color, 
                text=[f"{int(s)}%" for s in scores], textposition='outside', 
                textfont=dict(color="#FFFFFF", family="Arial Black", size=13)
            )])
            bar.update_layout(
                title={'text': "TOP AFFECTED ASSETS", 'font': {'color': "#FFFFFF", 'size': 16, 'family': "Arial Black"}, 'x': 0.5},
                height=280, margin=dict(l=20, r=20, t=60, b=40), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(range=[0, max(115, max(scores)+20) if scores else 115], gridcolor='rgba(255,0,127,0.3)', visible=False), 
                xaxis=dict(gridcolor='rgba(255,0,127,0.3)', tickangle=-35, tickfont=dict(color='#FFFFFF', size=11, family="Arial Black"))
            )
        st.plotly_chart(bar, use_container_width=True)

def render_attack_flow_diagram(matched_assets):
    st.markdown("<h2 style='text-align:center; color:#00FFCC; margin-top:30px; text-shadow: 0 0 15px #00FFCC;'>⚠️ ATTACK SIMULATION FLOW ⚠️</h2>", unsafe_allow_html=True)
    
    flow_style = "display: flex; align-items: center; justify-content: center; gap: 20px; padding: 40px; background: #050505; border-radius: 12px; border: 2px dashed #00FFCC; margin: 20px 0; flex-wrap: wrap; box-shadow: 0 0 30px rgba(0,255,204,0.3);"
    node_style = "padding: 20px 30px; border-radius: 8px; text-align: center; font-weight: 900; min-width: 180px; font-size: 1.2rem; border: 3px solid; text-transform: uppercase;"
    
    if not matched_assets:
        st.markdown(f"""<div style="{flow_style}">
<div style="{node_style} background: #110005; border-color: #FF003C; color: #FFFFFF;">🌐 Public Internet</div>
<div style="font-size: 32px; color: #00FFCC; font-weight: bold; text-shadow: 0 0 10px #00FFCC;">➔</div>
<div style="{node_style} background: #002211; border-color: #00FFCC; color: #00FFCC; box-shadow: 0 0 20px #00FFCC;">🛡️ Secure Perimeter<br><span style="color:#FFFFFF; font-size:1rem;">No Vulnerable Assets</span></div>
<div style="font-size: 32px; color: #00FFCC; font-weight: bold; text-shadow: 0 0 10px #00FFCC;">➔</div>
<div style="{node_style} background: #110005; border-color: #FF003C; color: #FFFFFF;">🏢 Internal Network</div>
</div>""", unsafe_allow_html=True)
    else:
        exposed = [a for a in matched_assets if str(a.get('internet_exposed', '')).lower() == 'true']
        target = exposed[0]['hostname'] if exposed else matched_assets[0]['hostname']
        icon = "🌐" if exposed else "💻"
        
        st.markdown(f"""<div style="{flow_style}">
<div style="{node_style} background: #110005; border-color: #FF003C; color: #FFFFFF;">🌐 Public Internet</div>
<div style="font-size: 32px; color: #FF003C; font-weight: bold; text-shadow: 0 0 10px #FF003C;">➔</div>
<div style="{node_style} background: #330000; border-color: #FF003C; color: #FFFFFF; box-shadow: 0 0 30px #FF003C;">🚨 BREACH POINT DETECTED<br><span style="color:#00FFCC; font-size:1.3rem;">{icon} {target}</span></div>
<div style="font-size: 32px; color: #FF003C; font-weight: bold; text-shadow: 0 0 10px #FF003C;">➔</div>
<div style="{node_style} background: #110005; border-color: #FF003C; color: #FFFFFF;">🏢 Internal Network</div>
</div>""", unsafe_allow_html=True)

def render_asset_grid(matched_assets, base_color):
    if not matched_assets: return
    st.markdown("<h2 style='color: #FFFFFF; text-shadow: 0 0 20px #FF007F; margin-top: 30px;'>🖥️ ASSET IMPACT GRID</h2>", unsafe_allow_html=True)
    
    grid_html = "<div class='asset-grid'>"
    for a in sorted(matched_assets, key=lambda x: x['match_score'], reverse=True):
        score_pct = int(a['match_score'] * 100)
        card_color = base_color if score_pct >= 50 else "#FF5500"
        exposed_badge = "<span style='color:#FF003C; font-weight:900; text-shadow: 0 0 10px #FF003C;'>🌐 EXPOSED</span>" if str(a.get('internet_exposed','')).lower() == 'true' else "<span style='color:#00FFCC; font-weight:900; text-shadow: 0 0 10px #00FFCC;'>🔒 INTERNAL</span>"
        
        grid_html += f"""<div class="asset-card" style="border-top-color: {card_color}; box-shadow: 0 10px 30px {card_color}44;">
<div style="display:flex; justify-content:space-between; align-items:center;">
<h3 style="margin:0; color:#FFFFFF; text-shadow: 0 0 15px {card_color}; font-size: 1.5rem;">{a['hostname']}</h3>
<div style="background:{card_color}; color:#000000; padding:8px 16px; border-radius:6px; font-size:16px; font-weight:900; box-shadow: 0 0 15px {card_color};">{score_pct}% RISK</div>
</div>
<hr style="border-color:rgba(255,255,255,0.2); margin:20px 0;">
<div style="font-size:16px; color:#FFFFFF !important; line-height:2.0; font-weight: 700;">
<b style="color:{card_color};">TYPE:</b> {a['asset_type']}<br>
<b style="color:{card_color};">SOFTWARE:</b> {a['software']} v{a['software_version']}<br>
<b style="color:{card_color};">OS:</b> {a['os']} v{a['os_version']}<br>
<b style="color:{card_color};">STATUS:</b> {exposed_badge} | <span style="color:#00FFCC;">{a['criticality']} VALUE</span>
</div>
</div>"""
    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)

def render_action_panel(recommendations, hunting_query, is_analyst, level):
    st.markdown("<h2 style='color: #FFFFFF; text-shadow: 0 0 20px #00FFCC; margin-top: 30px;'>🎯 IMMEDIATE ACTION PLAN</h2>", unsafe_allow_html=True)
    
    color, _, bg_color = get_color_scheme(level)
    
    html_list = f"<div style='background-color: #050505; border: 3px solid {color}; box-shadow: 0 0 40px {bg_color}; padding: 30px; border-radius: 12px;'><ul style='list-style: none; padding: 0; margin: 0;'>"
    for rec in recommendations:
        html_list += f"<li style='padding: 20px 0; border-bottom: 2px solid rgba(255,255,255,0.1); display: flex; align-items: center; gap: 20px;'><span style='font-size: 35px; filter: drop-shadow(0 0 15px {color});'>{rec['icon']}</span> <div><b style='color:{color}; font-size: 1.3rem; text-transform: uppercase; text-shadow: 0 0 10px {color};'>{rec['title']}</b> <span style='color:#FFFFFF; font-size:1.15rem; display:block; font-weight: 700; margin-top:5px;'>{rec['desc']}</span></div></li>"
    html_list += "</ul></div>"
    
    st.markdown(html_list, unsafe_allow_html=True)
    
    if is_analyst and hunting_query:
        with st.expander("🛠️ SHOW TECHNICAL MITIGATION & SPLUNK HUNTING QUERY", expanded=False):
            st.markdown("<h4 style='color:#00FFCC;'>SIEM Splunk / KQL Query</h4>", unsafe_allow_html=True)
            st.code(hunting_query, language="sql")

def render_mode2_dashboard(res):
    """Main Orchestrator for the UI."""
    inject_dark_executive_css()
    
    # 1. View Toggle
    c1, c2 = st.columns([1, 2])
    with c1:
        view_mode = st.radio("SELECT DASHBOARD VIEW:", ["👔 Executive View", "🔬 Analyst View"], horizontal=True, label_visibility="visible")
    
    is_analyst = "Analyst" in view_mode
    color, _, _ = get_color_scheme(res['relevance_level'])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Top Banner
    render_executive_banner(res['relevance_level'], res['relevance_score'], len(res['matched_assets']))
    
    # 3. Impact Visualizations
    st.markdown("<div class='dashboard-panel'>", unsafe_allow_html=True)
    render_impact_visualizations(res['relevance_score'], len(res['matched_assets']), res['total_assets'], res['matched_assets'], color)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 4. Attack Flow
    render_attack_flow_diagram(res['matched_assets'])
    
    # 5. Asset Grid
    render_asset_grid(res['matched_assets'], color)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 6. Dynamic Action Panel (Full Width)
    st.markdown("<div class='dashboard-panel'>", unsafe_allow_html=True)
    render_action_panel(res['recommendations'], res.get('hunting_query', ''), is_analyst, res['relevance_level'])
    st.markdown("</div>", unsafe_allow_html=True)

    # 7. Analyst Technical Details
    if is_analyst:
        st.markdown("<h2 style='color:#FFFFFF; text-shadow: 0 0 20px #FF003C; margin-top: 30px;'>🔬 ANALYST TECHNICAL DATA</h2>", unsafe_allow_html=True)
        with st.expander("RAW EXTRACTION JSON DATA", expanded=True):
            st.json({
                "CVEs": res.get('cve_ids', []),
                "Extracted_Technologies": res.get('extracted_technologies', [])
            })