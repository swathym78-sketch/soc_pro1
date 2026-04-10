import streamlit as st
import chromadb
import ollama
import json
import re
import datetime
import os
import time
from chromadb.utils import embedding_functions

# --- IMPORT STRICTLY SEPARATED UI COMPONENTS ---
from ui.mode1_ui import (
    inject_cyber_css, render_system_status, get_terminal_html,
    render_critical_alert, render_warning_alert, render_report_card,
    get_risk_gauges
)

# =======================================================
# 1. SYSTEM CONFIGURATION & DB INITIALIZATION
# =======================================================
DB_PATH = "./chroma_db_storage"
KNOWLEDGE_COLLECTION = "soc_knowledge_base"
MEMORY_COLLECTION = "soc_incident_history"
EMBED_MODEL = "nomic-embed-text:latest"
LLM_MODEL = "llama3.2:1b"

class CustomOllamaEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, model_name):
        self.model_name = model_name

    def __call__(self, input):
        embeddings = []
        for text in input:
            try: 
                embeddings.append(ollama.embeddings(model=self.model_name, prompt=text)['embedding'])
            except: 
                pass
        return embeddings

def ingest_threat_intelligence(collection):
    """Seed data for the global threat intel database."""
    threat_intel = [
        {"id": "t1", "text": "Execution of mimikatz or lsadump for credential dumping.", "severity": "CRITICAL", "weight": 0.95},
        {"id": "t2", "text": "Adding users to localgroup administrators using net user /add.", "severity": "HIGH", "weight": 0.85},
        {"id": "t3", "text": "Encoded powershell commands (-enc or -EncodedCommand) bypassing execution policies.", "severity": "HIGH", "weight": 0.80},
        {"id": "t4", "text": "Reverse shell connections using nc -e or netcat.", "severity": "CRITICAL", "weight": 0.95},
        {"id": "t5", "text": "Deleting shadow copies using vssadmin delete shadows.", "severity": "CRITICAL", "weight": 0.90},
        {"id": "t6", "text": "Standard system update via apt-get or yum.", "severity": "LOW", "weight": 0.1},
        {"id": "t7", "text": "Legitimate admin running PsExec for remote configuration.", "severity": "MEDIUM", "weight": 0.4},
        {"id": "t8", "text": "Execution of powershell with ExecutionPolicy Bypass.", "severity": "HIGH", "weight": 0.85},
        {"id": "t9", "text": "Remote process creation using wmic process call create.", "severity": "HIGH", "weight": 0.75}
    ]
    
    ids = [t["id"] for t in threat_intel]
    documents = [t["text"] for t in threat_intel]
    metadatas = [{"severity": t["severity"], "weight": t["weight"]} for t in threat_intel]
    
    try:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
    except Exception as e:
        print(f"Failed to ingest baseline threat intelligence: {e}")

@st.cache_resource
def get_dbs():
    client = chromadb.PersistentClient(path=DB_PATH)
    ollama_ef = CustomOllamaEmbeddingFunction(model_name=EMBED_MODEL)
    vector_db = client.get_or_create_collection(name=KNOWLEDGE_COLLECTION, embedding_function=ollama_ef)
    memory_db = client.get_or_create_collection(name=MEMORY_COLLECTION, embedding_function=ollama_ef)
    return vector_db, memory_db

try:
    vector_db, memory_db = get_dbs()
    if vector_db.count() == 0:
        st.warning("⚠️ Threat Intelligence Database is empty or missing. Rebuilding knowledge base automatically...")
        ingest_threat_intelligence(vector_db)
except Exception as e:
    st.error(f"Critical Database Error: {e}")
    st.stop()

# =======================================================
# 2. FIVE-LAYER SCORING ENGINE (RULES)
# =======================================================
def baseline_threat_rules(command):
    """Static rule-based detection for obvious malicious patterns."""
    cmd_lower = str(command).lower()
    
    # Absolute Critical (Cannot be easily overridden)
    critical_indicators = ["mimikatz", "lsadump", "nc -e", "vssadmin delete shadows"]
    for indicator in critical_indicators:
        if indicator in cmd_lower: return 0.95
            
    # High Risk
    high_indicators = ["executionpolicy bypass", "-exec bypass", "net user /add", "net localgroup administrators"]
    for indicator in high_indicators:
        if indicator in cmd_lower: return 0.85
            
    # Suspicious
    suspicious_indicators = ["wmic /node", "process call create", "downloadstring"]
    for indicator in suspicious_indicators:
        if indicator in cmd_lower: return 0.65
            
    return 0.0

def benign_activity_rules(command):
    """Heuristic rule-based detection for normal administrative IT behavior."""
    cmd_lower = str(command).lower()
    benign_indicators = ["robocopy", "ping", "nslookup", "gpupdate", "tasklist"]
    for indicator in benign_indicators:
        if indicator in cmd_lower: return -0.25  
    return 0.0

# =======================================================
# 3. CORE LOGIC
# =======================================================
def extract_entities(log_text):
    user_match = re.search(r'"user"\s*:\s*"([^"]+)"', log_text, re.IGNORECASE)
    host_match = re.search(r'"host"\s*:\s*"([^"]+)"', log_text, re.IGNORECASE)
    cmd_match = re.search(r'"command"\s*:\s*"([^"]+)"', log_text, re.IGNORECASE)
    
    user = user_match.group(1) if user_match else "unknown"
    host = host_match.group(1) if host_match else "unknown"
    command = cmd_match.group(1) if cmd_match else log_text

    if user != "unknown" and host != "unknown":
        return {"user": user, "host": host, "command": command}

    sys_prompt = "Extract JSON: user, host, command. No extra text."
    try:
        response = ollama.chat(model=LLM_MODEL, messages=[{'role': 'system', 'content': sys_prompt}, {'role': 'user', 'content': log_text}], options={"temperature": 0.0})
        content = response['message']['content']
        match = re.search(r'\{.*\}', content, re.DOTALL)
        return json.loads(match.group(0)) if match else {"user": user, "host": host, "command": command}
    except:
        return {"user": user, "host": host, "command": command}

def check_threat_intel(command):
    try:
        results = vector_db.query(query_texts=[command], n_results=1)
        if results and results['metadatas'] and results['metadatas'][0]:
            return float(results['metadatas'][0][0].get('weight', 0.5))
    except: pass
    return 0.5

def get_llm_score(log_text):
    sys_prompt = "Analyze log. Return ONLY a float between 0.0 and 1.0 representing risk."
    try:
        response = ollama.chat(model=LLM_MODEL, messages=[{'role': 'system', 'content': sys_prompt}, {'role': 'user', 'content': log_text}], options={"temperature": 0.0})
        content = response['message']['content']
        match = re.search(r'0\.\d+|1\.0', content)
        return float(match.group(0)) if match else 0.5
    except:
        return 0.5

def get_memory_adjustment(user, host, command, rule_weight):
    adjustment = 0.0
    past_incidents = []
    
    try:
        results = memory_db.get(include=["metadatas"])
        apply_benign_discount = False
        
        current_cmd_clean = str(command).lower().replace('"', '').replace("'", "").strip()
        exe_name = current_cmd_clean.split()[0] if current_cmd_clean else ""
        exe_name = exe_name.split('\\')[-1] 
        
        current_user = str(user).strip().lower()
        current_host = str(host).strip().lower()
        
        if results and results.get('metadatas'):
            for meta in results['metadatas']:
                status = meta.get('status', '')
                past_user = str(meta.get('user', '')).lower()
                past_host = str(meta.get('host', '')).lower()
                past_tool = str(meta.get('tool', '')).lower()
                
                if status == "VERIFIED_HACKING":
                    match_user = (current_user != "unknown" and current_user != "" and current_user == past_user)
                    match_host = (current_host != "unknown" and current_host != "" and current_host == past_host)
                    match_tool = (exe_name != "" and exe_name == past_tool)
                    
                    if match_user or match_host or match_tool:
                        if "Malicious" not in past_incidents:
                            adjustment += 0.4
                            past_incidents.append("Malicious")
                            
                elif status == "BENIGN_LEARNED":
                    if current_user != "unknown" and current_user != "" and current_user == past_user:
                        # FIX: Allow learning benign for High/Suspicious rules (< 0.95), but NOT Critical rules (0.95+)
                        if rule_weight < 0.95:  
                            if exe_name and exe_name == past_tool:
                                apply_benign_discount = True

            if apply_benign_discount:
                adjustment -= 0.5
                if "Benign" not in past_incidents:
                    past_incidents.append("Benign")
                    
    except Exception as e:
        print(f"Memory processing error: {e}")
        
    return min(0.5, max(-0.5, adjustment)), past_incidents

def stream_final_report(log_text, entities, risk_score_100, classification, history):
    """Generates a highly detailed, structured SOC report using STREAMING CHUNKS."""
    sys_prompt = f"""You are an elite Lead SOC Analyst writing an official, detailed Incident Analysis Report based on the provided JSON telemetry.
    Do NOT write a generic one-liner. Your report must contain specific technical details.

    Required Format:
    **Incident Overview**: What happened? Reference the exact User ({entities.get('user', 'unknown')}), Host ({entities.get('host', 'unknown')}).
    **Technical Analysis**: What is the specific command `{entities.get('command', 'unknown')}` attempting to do? Break down its flags (e.g., -enc, Bypass, /add, compression).
    **Risk Justification**: Why is this a {classification} event with a score of {risk_score_100}/100? Mention the potential threat vectors or if it resembles normal admin activity.
    **Memory Context**: If history exists ({history}), explain how prior learned behavior affected the risk score.

    Format the report professionally using Markdown, bullet points, and bold text to ensure readability."""
    
    try:
        response_generator = ollama.chat(
            model=LLM_MODEL, 
            messages=[{'role': 'system', 'content': sys_prompt}, {'role': 'user', 'content': f"Log Data: {log_text}"}], 
            options={"temperature": 0.4},
            stream=True
        )
        
        full_response = ""
        for chunk in response_generator:
            content = chunk["message"]["content"]
            full_response += content
            yield full_response
    except Exception:
        yield "Unable to generate detailed report. Verify Ollama LLM is running."

def log_to_terminal(msg, placeholder=None):
    if 'terminal_logs' not in st.session_state:
        st.session_state.terminal_logs = []
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.terminal_logs.append(f"[{timestamp}] {msg}")
    if placeholder:
        placeholder.markdown(get_terminal_html("\n".join(st.session_state.terminal_logs)), unsafe_allow_html=True)

def save_feedback(log_data, status, reasoning):
    try:
        doc_id = f"mem_{datetime.datetime.now().timestamp()}"
        user_val = str(log_data.get('user', 'unknown'))
        host_val = str(log_data.get('host', 'unknown'))
        command_val = str(log_data.get('command', ''))
        
        cmd_clean = command_val.lower().replace('"', '').replace("'", "").strip()
        exe_name = cmd_clean.split()[0] if cmd_clean else ""
        exe_name = exe_name.split('\\')[-1]
        
        doc = f"User: {user_val} Host: {host_val} Command: {command_val} Reasoning: {reasoning}"
        meta = {"user": user_val, "host": host_val, "tool": exe_name, "status": status, "timestamp": datetime.datetime.now().isoformat()}
        memory_db.add(documents=[doc], metadatas=[meta], ids=[doc_id])
    except Exception as e:
        st.error(f"Failed to save feedback: {e}")

# =======================================================
# 4. STREAMLIT UI (Mode 1)
# =======================================================
inject_cyber_css()

st.markdown("<h1>⚡ MODE 1: TACTICAL ANALYST</h1>", unsafe_allow_html=True)
render_system_status()

st.markdown("### 📥 RAW TELEMETRY INPUT")
default_log = '{"timestamp": "2026-03-03T10:00:00Z", "user": "admin_sarah", "host": "PROD-DB-01", "event_id": 4688, "command": "powershell.exe -enc JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAEkATwAuAE0AZQBtAG8AcgB5AFMAdAByAGUAYQBtACgAWwBDAG8AbgB2AGUAcgB0AF0AOgA6AEYAcgBvAG0AQgBhAHMAZQA2ADQAUwB0AHIAaQBuAGcAKAAiAEgA..."}'

log_input = st.text_area("Raw Telemetry JSON", value=default_log, height=300, label_visibility="collapsed")

terminal_placeholder = st.empty()

if st.button("▶ INITIATE NEURAL TRIAGE", use_container_width=True):
    st.session_state.terminal_logs = []
    st.session_state.feedback_action = None 
    
    log_to_terminal("Parsing raw telemetry JSON...", terminal_placeholder)
    time.sleep(0.3) 
    
    entities = extract_entities(log_input)
    cmd = entities.get('command', '')
    user = entities.get('user', '')
    host = entities.get('host', '')
    
    log_to_terminal(f"Extracted -> User: {user} | Host: {host}", terminal_placeholder)
    time.sleep(0.3)
    
    log_to_terminal("Querying Global Threat Intel (Index A)...", terminal_placeholder)
    threat_weight = check_threat_intel(cmd)
    time.sleep(0.3)
    
    log_to_terminal("Initiating LLM Behavior Analysis...", terminal_placeholder)
    llm_score = get_llm_score(log_input)
    
    log_to_terminal("Evaluating deterministic heuristics...", terminal_placeholder)
    rule_weight = baseline_threat_rules(cmd)
    if rule_weight > 0:
        log_to_terminal(f"⚠️ STATIC THREAT RULE MATCHED! Overriding baseline weight to {rule_weight}", terminal_placeholder)

    benign_adj = benign_activity_rules(cmd)
    if benign_adj < 0:
        log_to_terminal(f"✅ BENIGN RULE MATCHED! Applying reduction of {benign_adj}", terminal_placeholder)
    time.sleep(0.3)

    if threat_weight >= 0.7:
        base_risk = max(rule_weight, threat_weight)
        log_to_terminal(f"Strong Threat Intel Match ({threat_weight}) bypassing LLM dilution.", terminal_placeholder)
    else:
        base_risk = max(rule_weight, (threat_weight * 0.5) + (llm_score * 0.5))
        
    log_to_terminal(f"Base Risk Calculated: {base_risk:.2f}", terminal_placeholder)
    time.sleep(0.3)
    
    log_to_terminal("Querying Incident Memory (Index C) for Context...", terminal_placeholder)
    mem_adj, history = get_memory_adjustment(user, host, cmd, rule_weight)
    
    if history:
        if "Malicious" in history: log_to_terminal("Found VERIFIED_HACKING history (+0.4 penalty)", terminal_placeholder)
        if "Benign" in history: log_to_terminal("Found specific BENIGN_LEARNED history (-0.5 discount)", terminal_placeholder)
        time.sleep(0.3)
        
    total_adj = mem_adj + benign_adj
    final_risk = min(1.0, max(0.0, base_risk + total_adj))
    risk_score_100 = int(final_risk * 100)
    
    log_to_terminal(f"Adjustments: Memory({mem_adj:.2f}) + BenignHeuristics({benign_adj:.2f}) -> Final Risk: {final_risk:.2f}", terminal_placeholder)
    time.sleep(0.3)
    
    if final_risk >= 0.75: classification = "HIGH RISK"
    elif final_risk >= 0.45: classification = "SUSPICIOUS"
    else: classification = "LOW RISK"
    
    log_to_terminal(f"Triage Complete. Final Verdict: {classification}", terminal_placeholder)
    time.sleep(0.3)
    
    log_to_terminal("Generating detailed official SOC report...", terminal_placeholder)
    
    report_placeholder = st.empty()
    report = ""
    for chunk_text in stream_final_report(log_input, entities, risk_score_100, classification, history):
        report = chunk_text
        report_placeholder.markdown(f"<div style='background-color:#0A0A0A; padding:20px; border-left:4px solid #00FFCC; border-radius:8px; margin-top:15px; margin-bottom:15px; box-shadow: 0 0 15px rgba(0,255,204,0.1);'>{report}▌</div>", unsafe_allow_html=True)
    report_placeholder.empty() 
    
    log_to_terminal("Report Generation Complete.", terminal_placeholder)
    
    st.session_state.m1_result = {
        "entities": entities,
        "risk_score_100": risk_score_100,
        "classification": classification,
        "history": history,
        "report": report
    }

if 'terminal_logs' in st.session_state and st.session_state.terminal_logs:
    terminal_placeholder.markdown(get_terminal_html("\n".join(st.session_state.terminal_logs)), unsafe_allow_html=True)

# =======================================================
# UI RENDERING & FEEDBACK CHATBOT
# =======================================================
if 'm1_result' in st.session_state:
    res = st.session_state.m1_result
    st.markdown("---")
    
    if res['history']:
        if "Malicious" in res['history']:
            render_critical_alert(res['entities']['user'])
        if "Benign" in res['history']:
            render_warning_alert(res['entities']['user'])
            
    col1, col2 = st.columns([1, 1])
    with col1:
        gauge, radar = get_risk_gauges(res['risk_score_100'])
        st.plotly_chart(gauge, use_container_width=True)
    with col2:
        st.plotly_chart(radar, use_container_width=True)
        
    render_report_card(res['report'], res['classification'])
    
    st.markdown("### 🔄 ANALYST FEEDBACK LOOP")
    
    if 'flash_msg' in st.session_state:
        st.success(st.session_state.flash_msg)
        del st.session_state.flash_msg
        
    if 'feedback_action' not in st.session_state:
        st.session_state.feedback_action = None

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🟢 Flag as False Positive (Learn Benign)", use_container_width=True):
            st.session_state.feedback_action = "BENIGN_LEARNED"
            st.rerun()
    with c2:
        if st.button("🔴 Confirm Malicious (Learn Attack)", use_container_width=True):
            save_feedback(res['entities'], "VERIFIED_HACKING", "Analyst confirmed malicious activity.")
            st.session_state.flash_msg = "✅ Successfully learned: VERIFIED_HACKING. Memory updated!"
            st.session_state.feedback_action = None
            st.rerun()
    with c3:
        if st.button("🧹 Clear Terminal", use_container_width=True):
            st.session_state.terminal_logs = []
            st.session_state.feedback_action = None
            st.rerun()

    if st.session_state.feedback_action == "BENIGN_LEARNED":
        st.markdown("---")
        
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown("<h2 style='color: #00ffcc; margin-bottom: 0px;'>🧠 AI Memory Calibration Matrix</h2>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 1.15rem; color: #e0e0e0; line-height: 1.6;'>I have currently flagged this event as potentially dangerous. To recalibrate my neural network, please explain why this specific activity is a <b>False Positive</b>. Your reasoning will be permanently hardcoded into my memory database to prevent future alert fatigue for this user and tool.</p>", unsafe_allow_html=True)
            
            with st.form(key="feedback_form", border=True):
                st.markdown("<h4 style='color: #a0a0a0;'>✍️ Analyst Context & Justification</h4>", unsafe_allow_html=True)
                reasoning = st.text_area("Provide your context below:", height=150, placeholder="E.g., Authorized Network Admin performing remote troubleshooting...")
                
                submit_button = st.form_submit_button(
                    label="⚡ SUBMIT TRAINING DATA & RECALIBRATE", 
                    type="primary", 
                    use_container_width=True
                )
                
                if submit_button:
                    if reasoning:
                        save_feedback(res['entities'], "BENIGN_LEARNED", reasoning)
                        st.session_state.flash_msg = "✅ Training data saved to memory! Run 'Initiate Neural Triage' again to see the new score."
                        st.session_state.feedback_action = None
                        st.rerun()
                    else:
                        st.warning("⚠️ Please enter your reasoning before submitting to the memory matrix.")