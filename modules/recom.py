import streamlit as st
import chromadb
import ollama
import os
import re
from collections import Counter
from chromadb.utils import embedding_functions

# --- IMPORT STRICTLY SEPARATED UI COMPONENTS ---
from ui.mode3_ui import inject_mode3_css, render_dashboard_visuals

# =======================================================
# CONFIGURATION
# =======================================================
DB_PATH = "./chroma_db_storage"
PLAYBOOK_PATH = "documents/security_recommendations.md"
PLAYBOOK_COLLECTION = "security_playbook_index"
LLM_MODEL = "llama3.2:1b"
EMBED_MODEL = "nomic-embed-text:latest"

class CustomOllamaEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, model_name):
        self.model_name = model_name

    def __call__(self, input):
        embeddings = []
        for text in input:
            try: embeddings.append(ollama.embeddings(model=self.model_name, prompt=text)['embedding'])
            except: pass
        return embeddings

# =======================================================
# PLAYBOOK INGESTION & DATA AGGREGATION (PYTHON ONLY)
# =======================================================
def initialize_playbook():
    """Initializes the RAG playbook database for Mode 3 Copilot."""
    client = chromadb.PersistentClient(path=DB_PATH)
    ef = CustomOllamaEmbeddingFunction(model_name=EMBED_MODEL)
    playbook_db = client.get_or_create_collection(name=PLAYBOOK_COLLECTION, embedding_function=ef)
    
    if playbook_db.count() == 0 and os.path.exists(PLAYBOOK_PATH):
        try:
            with open(PLAYBOOK_PATH, "r", encoding="utf-8") as f:
                content = f.read()
            sections = re.split(r'\n(?=### )', content)
            docs, ids, metas = [], [], []
            for i, sec in enumerate(sections):
                if sec.strip():
                    docs.append(sec.strip())
                    ids.append(f"playbook_rule_{i}")
                    metas.append({"source": "security_playbook"})
            if docs: playbook_db.add(documents=docs, ids=ids, metadatas=metas)
        except Exception as e: print(f"Failed to ingest security playbook: {e}")
            
    return playbook_db

@st.cache_data(ttl=60)
def get_aggregated_stats():
    """Reads Mode 1 & 2 history. Strictly calculates math to prevent LLM hallucination."""
    client = chromadb.PersistentClient(path=DB_PATH)
    stats = {"total_incidents": 0, "malicious": 0, "benign": 0, "hosts": Counter(), "tools": Counter(), "vulnerabilities": Counter()}
    
    try:
        m1_db = client.get_collection(name="soc_incident_history")
        data = m1_db.get(include=["metadatas"])
        if data and data.get('metadatas'):
            stats["total_incidents"] += len(data['metadatas'])
            for m in data['metadatas']:
                if m.get('status') == 'VERIFIED_HACKING': stats['malicious'] += 1
                if m.get('status') == 'BENIGN_LEARNED': stats['benign'] += 1
                host = m.get('host', 'unknown')
                tool = m.get('tool', 'unknown')
                if host and str(host).lower() != 'unknown': stats['hosts'][host] += 1
                if tool and str(tool).lower() != 'unknown': stats['tools'][tool] += 1
    except Exception: pass

    try:
        m2_db = client.get_collection(name="incident_memory_index")
        data = m2_db.get(include=["metadatas"])
        if data and data.get('metadatas'):
            for m in data['metadatas']:
                cve_string = m.get('cve_ids', '')
                if cve_string:
                    for cve in cve_string.split(','):
                        if cve.strip(): stats['vulnerabilities'][cve.strip()] += 1
    except Exception: pass

    stats['hosts'] = dict(stats['hosts'].most_common(5))
    stats['tools'] = dict(stats['tools'].most_common(5))
    stats['vulnerabilities'] = dict(stats['vulnerabilities'].most_common(5))
    return stats

# =======================================================
# AGENTIC RAG CONTEXT FETCHERS
# =======================================================
def get_history_context(query):
    """Searches ChromaDB for semantic incident matches AND the absolute latest events."""
    client = chromadb.PersistentClient(path=DB_PATH)
    ef = CustomOllamaEmbeddingFunction(model_name=EMBED_MODEL)
    context_lines = []
    recent_pool = []
    
    # 1. Fetch Mode 1 Tactical Memory
    try:
        m1_db = client.get_collection(name="soc_incident_history", embedding_function=ef)
        res1 = m1_db.query(query_texts=[query], n_results=3)
        if res1 and res1.get('metadatas') and res1['metadatas'][0]:
            for m in res1['metadatas'][0]:
                context_lines.append(f"[M1 Tactical] Time: {m.get('timestamp')} | Host: {m.get('host')} | User: {m.get('user')} | Tool: {m.get('tool')} | Status: {m.get('status')}")
        
        m1_all = m1_db.get(include=["metadatas"])
        if m1_all and m1_all.get('metadatas'):
            recent_pool.extend(m1_all['metadatas'])
    except Exception: pass

    # 2. Fetch Mode 2 Strategic Memory
    try:
        m2_db = client.get_collection(name="incident_memory_index", embedding_function=ef)
        res2 = m2_db.query(query_texts=[query], n_results=3)
        if res2 and res2.get('metadatas') and res2['metadatas'][0]:
            for m in res2['metadatas'][0]:
                context_lines.append(f"[M2 Strategic] Time: {m.get('timestamp')} | Threat: {m.get('threat_name')} | Severity: {m.get('relevance_level')} | Exposed Assets: {m.get('affected_assets_count')}")
        
        m2_all = m2_db.get(include=["metadatas"])
        if m2_all and m2_all.get('metadatas'):
            recent_pool.extend(m2_all['metadatas'])
    except Exception: pass

    # 3. Handle Time-based queries
    query_lower = query.lower()
    if any(word in query_lower for word in ["last", "recent", "latest", "today"]):
        recent_sorted = sorted(recent_pool, key=lambda x: x.get('timestamp', ''), reverse=True)
        context_lines.append("--- THE MOST RECENT INCIDENTS ---")
        for m in recent_sorted[:3]:
            if 'threat_name' in m:
                context_lines.append(f"[M2 Strategic] Time: {m.get('timestamp')} | Threat: {m.get('threat_name')} | Severity: {m.get('relevance_level')}")
            else:
                context_lines.append(f"[M1 Tactical] Time: {m.get('timestamp')} | Host: {m.get('host')} | User: {m.get('user')} | Tool: {m.get('tool')} | Status: {m.get('status')}")

    return "\n".join(list(dict.fromkeys(context_lines)))

def get_playbook_context(query):
    """Searches the Playbook DB for mitigation strategies."""
    playbook_db = initialize_playbook()
    try:
        res = playbook_db.query(query_texts=[query], n_results=2)
        if res and res.get('documents') and res['documents'][0]:
            return "\n\n".join(res['documents'][0])
    except Exception: pass
    return ""

# =======================================================
# LLM STREAMING & AGENTIC ROUTING
# =======================================================
def stream_copilot_response(query, stats_dict):
    """Agentic RAG: Routes query, fetches dynamic context, and yields streaming chunks."""
    
    # --- STEP 1: FAST INTENT ROUTER ---
    intent_prompt = f"Classify the intent of the user's query into exactly ONE word: 'STATS' (asking about metrics/graphs), 'HISTORY' (asking about past events, recent incidents, specific IPs), or 'PLAYBOOK' (asking how to mitigate/defend). Query: {query}"
    try:
        intent_res = ollama.chat(model=LLM_MODEL, messages=[{"role": "user", "content": intent_prompt}], options={"temperature": 0.0})
        intent = intent_res['message']['content'].strip().upper()
    except:
        intent = "HISTORY" 
        
    # --- STEP 2: DYNAMIC CONTEXT GATHERING ---
    context_block = f"""
    === BASELINE METRICS ===
    Total Evaluated Incidents: {stats_dict['total_incidents']}
    Confirmed Malicious Attacks: {stats_dict['malicious']}
    Learned Benign Activities: {stats_dict['benign']}
    Most Targeted Hosts: {stats_dict['hosts']}
    Most Frequent Attack Tools: {stats_dict['tools']}
    """
    
    if "HISTORY" in intent or any(w in query.lower() for w in ["last", "recent", "incident", "happen"]):
        history_data = get_history_context(query)
        if history_data:
            context_block += f"\n=== HISTORICAL INCIDENT LOGS (RAG RETRIEVED) ===\n{history_data}"
            
    if "PLAYBOOK" in intent or any(w in query.lower() for w in ["fix", "mitigate", "prevent", "stop", "recommend"]):
        playbook_data = get_playbook_context(query)
        if playbook_data:
            context_block += f"\n=== SECURITY PLAYBOOK (RAG RETRIEVED) ===\n{playbook_data}"

    # --- STEP 3: SYNTHESIS AGENT ---
    sys_prompt = f"""You are the SOC Strategic AI Copilot.
    You MUST ground your answers ONLY in the provided Context Data. Do not invent details.
    If the user asks about recent incidents, read the 'HISTORICAL INCIDENT LOGS' section to answer accurately.
    Be concise, analytical, and conversational.

    {context_block}
    """
    
    response_generator = ollama.chat(
        model=LLM_MODEL, 
        messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": query}], 
        options={"temperature": 0.2},
        stream=True
    )
    
    full_response = ""
    for chunk in response_generator:
        content = chunk["message"]["content"]
        full_response += content
        yield full_response

def stream_strategic_recommendations(stats_dict):
    """Yields streaming chunks for the RAG Playbook recommendations button."""
    patterns = list(stats_dict['tools'].keys()) + list(stats_dict['vulnerabilities'].keys())
    search_query = " ".join(patterns) if patterns else "general security best practices"
    
    playbook_data = get_playbook_context(search_query)

    sys_prompt = f"""You are a Lead SOC Architect. Based strictly on the provided PLAYBOOK KNOWLEDGE and DETECTED THREATS, generate a prioritized list of specific SOC mitigation steps. 
    Format your answer purely as detailed bullet points. Do not write a summary paragraph.
    
    === DETECTED THREATS IN ENVIRONMENT ===
    {search_query}

    === PLAYBOOK KNOWLEDGE (RAG EXTRACT) ===
    {playbook_data}
    """
    
    response_generator = ollama.chat(
        model=LLM_MODEL, 
        messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": "Provide strategic security recommendations."}], 
        options={"temperature": 0.2},
        stream=True
    )
    
    full_response = ""
    for chunk in response_generator:
        content = chunk["message"]["content"]
        full_response += content
        yield full_response

# =======================================================
# MAIN STREAMLIT UI EXECUTION LOOP
# =======================================================
inject_mode3_css()

st.markdown("<h1>🧠 MODE 3: STRATEGIC SOC COPILOT</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#00FFCC; font-weight:bold; margin-top:-10px; margin-bottom:20px;'>Interactive AI Copilot analyzing historical telemetry and strategic security playbooks.</p>", unsafe_allow_html=True)

# 1. STATE INITIALIZATION
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_analytics" not in st.session_state:
    st.session_state.show_analytics = False
if "show_recs" not in st.session_state:
    st.session_state.show_recs = False
if "rec_text" not in st.session_state:
    st.session_state.rec_text = ""

stats = get_aggregated_stats()

# 2. UI LAYOUT
col_chat, col_side = st.columns([3, 1])

# Right Sidebar: Suggested Questions
with col_side:
    st.markdown("<div class='dashboard-panel'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1.2rem; color:#00FFCC !important;'>💡 Suggested Queries</h3>", unsafe_allow_html=True)
    if st.button("What was the last incident?"):
        st.session_state.trigger_query = "What was the last incident?"
    if st.button("Which host is attacked most?"):
        st.session_state.trigger_query = "Which host is attacked most?"
    if st.button("What are the most frequent attack tools?"):
        st.session_state.trigger_query = "What are the most frequent attack tools?"
    st.markdown("</div>", unsafe_allow_html=True)

# Main Chat Interface (Box removed here)
with col_chat:
    
    # Render Conversation History
    for msg in st.session_state.messages:
        avatar = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            
    # CHAT INPUT HANDLING
    query = st.chat_input("Ask Copilot about recent incidents, hosts, or defenses...")
    if 'trigger_query' in st.session_state:
        query = st.session_state.trigger_query
        del st.session_state.trigger_query

    if query:
        # Save and render User message
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user", avatar="👤"):
            st.markdown(query)
        
        # Handle empty database strictly
        if stats['total_incidents'] == 0:
            bot_reply = "No incident history available yet. Run Mode 1 or Mode 2 to generate security telemetry."
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(bot_reply)
            st.session_state.show_analytics = False
        else:
            # ⚡ STREAMING CHATBOT RESPONSE ⚡
            with st.chat_message("assistant", avatar="🤖"):
                placeholder = st.empty()
                final_text = ""
                try:
                    for text_chunk in stream_copilot_response(query, stats):
                        final_text = text_chunk
                        placeholder.markdown(final_text + "▌")
                    placeholder.markdown(final_text) # Remove cursor at the end
                except Exception as e:
                    final_text = f"System Error: {str(e)}"
                    placeholder.markdown(final_text)

            st.session_state.messages.append({"role": "assistant", "content": final_text})
            st.session_state.show_analytics = True
            st.session_state.show_recs = False 
            st.session_state.rec_text = ""
            
    # Dynamic Visuals Appear AFTER Copilot Answers
    if st.session_state.show_analytics and stats['total_incidents'] > 0:
        st.markdown("<hr style='border-color:#8A2BE2;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#00FFCC !important;'>📊 Active Incident Telemetry</h3>", unsafe_allow_html=True)
        render_dashboard_visuals(stats)
        
        # ⚡ STREAMING RAG RECOMMENDATIONS ⚡
        if not st.session_state.show_recs:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⚡ GENERATE STRATEGIC RECOMMENDATIONS (RAG PLAYBOOK)", use_container_width=True):
                st.session_state.trigger_recs_stream = True
                st.session_state.show_recs = True
                st.rerun()
                
        if st.session_state.show_recs:
            st.markdown("<h3 style='color:#FF007F !important; margin-top:20px;'>🛡️ Security Recommendations</h3>", unsafe_allow_html=True)
            
            if st.session_state.get('trigger_recs_stream', False):
                rec_placeholder = st.empty()
                final_rec_text = ""
                try:
                    for rec_chunk in stream_strategic_recommendations(stats):
                        final_rec_text = rec_chunk
                        rec_placeholder.markdown(f"<div style='background-color:#111; padding:20px; border-radius:8px; border-left:4px solid #FF007F;'>{final_rec_text}▌</div>", unsafe_allow_html=True)
                    
                    rec_placeholder.markdown(f"<div style='background-color:#111; padding:20px; border-radius:8px; border-left:4px solid #FF007F;'>{final_rec_text}</div>", unsafe_allow_html=True)
                except Exception as e:
                    final_rec_text = f"Error generating recommendations: {str(e)}"
                    rec_placeholder.markdown(final_rec_text)

                st.session_state.rec_text = final_rec_text
                st.session_state.trigger_recs_stream = False 
            else:
                if st.session_state.rec_text:
                    st.markdown(f"<div style='background-color:#111; padding:20px; border-radius:8px; border-left:4px solid #FF007F;'>{st.session_state.rec_text}</div>", unsafe_allow_html=True)