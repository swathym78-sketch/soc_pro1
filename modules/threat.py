import streamlit as st
import chromadb
import ollama
import json
import re
import pandas as pd
import datetime
import os
from chromadb.utils import embedding_functions

# --- IMPORT STRICTLY SEPARATED UI COMPONENTS ---
from ui.mode2_ui import render_mode2_dashboard, inject_dark_executive_css

# =======================================================
# 1. SYSTEM CONFIGURATION & DB INITIALIZATION
# =======================================================
DB_PATH = "./chroma_db_storage"        
ASSET_COLLECTION_NAME = "asset_inventory_index"  # Index B
MEMORY_COLLECTION_NAME = "incident_memory_index" # Index C
ASSET_CSV_PATH = "documents/assets.csv"
EMBED_MODEL = "nomic-embed-text:latest"       
OLLAMA_URL = "http://localhost:11434"  

# Hardcoded Defaults (Sidebar UI Removed for Cleaner Experience)
LLM_MODEL = "llama3.2:1b"
FAST_MODE = True

# =======================================================
# 2. DATABASE LOGIC & ASSET INGESTION
# =======================================================
class CustomOllamaEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, model_name, base_url):
        self.model_name = model_name
        self.client = ollama.Client(host=base_url)

    def __call__(self, input):
        embeddings = []
        for text in input:
            try: embeddings.append(self.client.embeddings(model=self.model_name, prompt=text)['embedding'])
            except: pass
        return embeddings

def ingest_assets(asset_collection):
    if asset_collection.count() == 0 and os.path.exists(ASSET_CSV_PATH):
        try:
            df = pd.read_csv(ASSET_CSV_PATH)
            df = df.fillna("").astype(str)
            
            ids, metadatas, documents = [], [], []
            for index, row in df.iterrows():
                asset_id = f"asset_{row.get('asset_id', index)}"
                ids.append(asset_id)
                metadatas.append(row.to_dict())
                documents.append(f"Hostname: {row.get('hostname', '')} | OS: {row.get('os', '')} {row.get('os_version', '')} | Software: {row.get('software', '')} {row.get('software_version', '')}")
                
            asset_collection.add(documents=documents, metadatas=metadatas, ids=ids)
        except Exception as e:
            st.error(f"Failed to ingest assets.csv: {e}")

@st.cache_resource
def get_dbs():
    client = chromadb.PersistentClient(path=DB_PATH)
    ollama_ef = CustomOllamaEmbeddingFunction(model_name=EMBED_MODEL, base_url=OLLAMA_URL)
    asset_coll = client.get_or_create_collection(name=ASSET_COLLECTION_NAME, embedding_function=ollama_ef)
    memory_coll = client.get_or_create_collection(name=MEMORY_COLLECTION_NAME, embedding_function=ollama_ef)
    ingest_assets(asset_coll)
    return asset_coll, memory_coll

try:
    asset_db, memory_db = get_dbs()
except Exception as e:
    st.error(f"Database Error: {e}")

# =======================================================
# 3. PRE-PROCESSING VALIDATION
# =======================================================
def validate_threat_input(text):
    """Strict input validation to prevent generic text from triggering the engine."""
    clean_text = str(text).strip()
    
    # Rule A: Minimum length (reject "hi", "test")
    if len(clean_text) < 40:
        return False
        
    lower_text = clean_text.lower()
    
    # Rule B: Must contain a CVE or specific security contexts
    has_cve = bool(re.search(r'cve-\d{4}-\d+', lower_text))
    
    products = ["apache", "exchange", "windows", "vmware", "pan-os", "cisco", "nginx", "tomcat", "kubernetes", "fortinet", "fortios", "citrix"]
    has_product = any(p in lower_text for p in products)
    
    contexts = ["vulnerability", "remote code execution", "exploit", "patch", "security advisory", "buffer overflow", "zero-day", "privilege escalation", "bypass"]
    has_context = any(c in lower_text for c in contexts)
    
    # Rule C: If no CVE, no product, and no security context -> Invalid
    if not (has_cve or (has_product and has_context)):
        return False
        
    return True

# =======================================================
# 4. DETERMINISTIC EXTRACTION & SCORING LOGIC
# =======================================================
def deterministic_fallback(threat_text):
    cves = list(set(re.findall(r'CVE-\d{4}-\d+', threat_text, re.IGNORECASE)))
    cves = [c.upper() for c in cves]
    versions = list(set(re.findall(r'\b\d+\.\d+(?:\.\d+)?\b', threat_text)))
    
    products = []
    lower_text = threat_text.lower()
    known_products = ["exchange", "apache", "windows server", "ubuntu", "cisco", "tomcat", "kubernetes", "nginx", "vmware", "jira", "fortios", "macos", "active directory", "mssql"]
    
    for kp in known_products:
        if kp in lower_text:
            products.append(kp)
            
    technologies = []
    if products:
        for p in products:
            technologies.append({"product": p, "version": versions[0] if versions else ""})
    
    return {"technologies": technologies, "cve_ids": cves, "attack_vector": "Unknown (Regex Fallback)"}

def stream_extract_technologies_from_llm(threat_text):
    """Streams JSON extraction character by character from the LLM."""
    sys_prompt = """You are a deterministic threat parser. Extract ONLY:
    - product name
    - version
    - CVE IDs
    - attack vector
    Return STRICT JSON with no markdown and no extra text.
    Format exactly like this:
    {
        "technologies": [{"product": "apache", "version": "2.4.49"}],
        "cve_ids": ["CVE-2021-41773"],
        "attack_vector": "Path Traversal"
    }
    """
    try:
        response_generator = ollama.chat(
            model=LLM_MODEL, 
            messages=[{'role': 'system', 'content': sys_prompt}, {'role': 'user', 'content': threat_text}],
            options={"temperature": 0.0},
            stream=True
        )
        full_response = ""
        for chunk in response_generator:
            content = chunk["message"]["content"]
            full_response += content
            yield full_response
    except Exception as e:
        yield ""

def perform_asset_matching(extracted_json):
    matched_assets, max_score, total_assets = [], 0.0, 0
    try:
        all_assets_data = asset_db.get(include=["metadatas"])
        if all_assets_data and all_assets_data['metadatas']:
            total_assets = len(all_assets_data['metadatas'])
            for asset in all_assets_data['metadatas']:
                asset_score = 0.0
                software_str = asset.get('software', '').lower()
                os_str = asset.get('os', '').lower()
                software_ver = asset.get('software_version', '').lower()
                os_ver = asset.get('os_version', '').lower()
                
                for tech in extracted_json.get('technologies', []):
                    prod = str(tech.get('product', '')).lower()
                    ver = str(tech.get('version', '')).lower()
                    
                    if prod and (prod in software_str or prod in os_str):
                        asset_score += 0.5 
                        if ver and (ver in software_ver or ver in os_ver):
                            asset_score += 0.3
                        break 
                
                if asset_score > 0 and str(asset.get('internet_exposed', 'false')).lower() == 'true':
                    asset_score += 0.2
                    
                if asset_score > 0:
                    asset['match_score'] = min(1.0, asset_score)
                    matched_assets.append(asset)
                    if asset_score > max_score:
                        max_score = asset_score
    except Exception as e:
        print(f"Asset matching failed: {e}")
        
    if max_score >= 0.8: level = "CRITICAL"
    elif max_score >= 0.5: level = "HIGH"
    elif max_score >= 0.3: level = "MEDIUM"
    else: level = "LOW"
    
    return matched_assets, min(1.0, max_score), level, total_assets

def stream_generate_siem_query(threat_text, matched_assets, level, technologies, fast_mode):
    """Performance Optimized: Streams deterministic rule-based templates or streams LLM generation."""
    if level in ["LOW", "MEDIUM"] or not matched_assets:
        yield "" 
        return

    if fast_mode:
        prod_str = " ".join([t.get('product', '').lower() for t in technologies])
        if "exchange" in prod_str:
            yield 'index=msexchange EventCode=4624 OR EventCode=4625 | stats count by TargetUserName, IpAddress'
        elif any(x in prod_str for x in ["apache", "nginx", "tomcat"]):
            yield 'index=web sourcetype=access_combined status=200 uri_path="*..%2f*" | stats count by clientip, uri_path'
        elif any(x in prod_str for x in ["vmware", "esxi"]):
            yield 'index=vmware sourcetype=vmware:syslog "authentication failure" OR "Accepted password" | stats count by user, src_ip'
        elif any(x in prod_str for x in ["firewall", "pan-os", "cisco", "fortios"]):
            yield 'index=firewall action=allowed (dest_port=22 OR dest_port=443) | stats count by src_ip, dest_ip'
        else:
            yield 'index=main | head 10'
        return
            
    # Slower LLM Fallback (Only happens if Fast Mode is OFF and level is HIGH/CRITICAL)
    sys_prompt = "You are a deterministic SOC Architect. Provide ONE structured Splunk SPL hunting query to look for this threat. Reply with ONLY the query code block."
    try:
        response_generator = ollama.chat(
            model=LLM_MODEL, 
            messages=[{'role': 'system', 'content': sys_prompt}, {'role': 'user', 'content': threat_text[:500]}],
            options={"temperature": 0.0},
            stream=True
        )
        full_response = ""
        for chunk in response_generator:
            content = chunk["message"]["content"]
            full_response += content
            yield full_response
    except Exception:
        yield "index=main | head 10"

# =======================================================
# 5. DETERMINISTIC RECOMMENDATION ENGINE
# =======================================================
def get_dynamic_recommendations(level, technologies, matched_assets):
    recommendations = []
    
    if level == "LOW":
        recommendations.append({"icon": "✅", "title": "No Immediate Action", "desc": "No immediate action required. Current environment is not exposed to this specific threat vector."})
        recommendations.append({"icon": "👁️", "title": "Monitoring", "desc": "Continue routine monitoring and standard patch cycles."})
        return recommendations
        
    if level == "MEDIUM":
        recommendations.append({"icon": "🛡️", "title": "Schedule Patching", "desc": "Plan to patch affected systems during the next standard maintenance window."})
        recommendations.append({"icon": "🔐", "title": "Access Review", "desc": "Review access controls for identified internal assets to ensure defense-in-depth."})
        recommendations.append({"icon": "👁️", "title": "Monitor Logs", "desc": "Monitor related system logs for unusual authentication or execution activity."})
    elif level == "HIGH":
        recommendations.append({"icon": "🚨", "title": "Urgent Patching", "desc": "Patch affected systems urgently, ideally within 24-48 hours."})
        if any(str(a.get('internet_exposed', '')).lower() == 'true' for a in matched_assets):
            recommendations.append({"icon": "🌐", "title": "Restrict Network", "desc": "Restrict public network access to vulnerable systems until patches are verified."})
        recommendations.append({"icon": "👁️", "title": "Targeted Monitoring", "desc": "Deploy targeted log monitoring to detect specific indicators of compromise."})
        recommendations.append({"icon": "🔐", "title": "Validate Authentication", "desc": "Ensure Multi-Factor Authentication (MFA) is strictly enforced on affected boundaries."})
    elif level == "CRITICAL":
        recommendations.append({"icon": "🔥", "title": "Emergency Patching", "desc": "Immediate emergency patching required. Bypass standard maintenance windows."})
        if any(str(a.get('internet_exposed', '')).lower() == 'true' for a in matched_assets):
            recommendations.append({"icon": "🛑", "title": "Disable Exposure", "desc": "Temporarily disable external internet exposure to the affected assets immediately."})
        recommendations.append({"icon": "🔑", "title": "Rotate Credentials", "desc": "Rotate administrative credentials and active session tokens as a precaution."})
        recommendations.append({"icon": "👁️", "title": "Continuous SOC Monitoring", "desc": "Enable continuous, real-time SOC monitoring specifically focused on these assets."})
        
    prod_str = " ".join([t.get('product', '').lower() for t in technologies])
    
    if "exchange" in prod_str:
        recommendations.append({"icon": "📧", "title": "Exchange Security", "desc": "Monitor IIS authentication logs and review abnormal mailbox access patterns or unexpected rule creations."})
    if "apache" in prod_str or "nginx" in prod_str or "tomcat" in prod_str:
        recommendations.append({"icon": "🕸️", "title": "Web Application Firewall", "desc": "Inspect web server access logs and deploy WAF rules blocking path traversal and malicious payloads."})
    if "firewall" in prod_str or "pan-os" in prod_str or "cisco" in prod_str:
        recommendations.append({"icon": "🧱", "title": "Perimeter Lock", "desc": "Restrict administrative interface access strictly to internal, secure management IP subnets."})
    if "vmware" in prod_str or "esxi" in prod_str:
        recommendations.append({"icon": "🖥️", "title": "Hypervisor Integrity", "desc": "Audit hypervisor access logs, vCenter configurations, and review recent privileged account activity."})
        
    return recommendations[:6]

# =======================================================
# 6. HISTORY STORAGE
# =======================================================
def save_structured_history(final_output):
    try:
        timestamp = datetime.datetime.now().isoformat()
        threat_name = final_output['cve_ids'][0] if final_output['cve_ids'] else "Zero-Day Threat"
        meta = {
            "mode": "Mode2",
            "threat_name": threat_name,
            "cve_ids": ",".join(final_output['cve_ids']),
            "affected_assets_count": len(final_output['matched_assets']),
            "relevance_level": final_output['relevance_level'],
            "relevance_score": final_output['relevance_score'],
            "timestamp": timestamp
        }
        doc = f"MODE 2 ANALYSIS: Threat {threat_name} evaluated. Level: {final_output['relevance_level']}."
        memory_db.add(documents=[doc], metadatas=[meta], ids=[f"m2_{timestamp}"])
    except Exception as e:
        print(f"Failed to save memory: {e}")

# =======================================================
# 7. STREAMLIT ORCHESTRATION 
# =======================================================
inject_dark_executive_css()

st.markdown("<h1>🌐 PROACTIVE THREAT IMPACT ANALYSIS</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#94A3B8; margin-top:-10px; margin-bottom:20px;'>Assess incoming global threat intelligence against internal organizational assets.</p>", unsafe_allow_html=True)

default_intel = """Title: Critical Path Traversal Vulnerability in Apache HTTP Server
CVE: CVE-2021-41773
Description: A flaw was found in a change made to path normalization in Apache HTTP Server 2.4.49. An attacker could use a path traversal attack to map URLs to files outside the expected document root. If files outside of the document root are not protected by "require all denied", these requests can succeed."""

threat_input = st.text_area("Input Threat Intelligence Report / Blog / Advisory:", height=120, value=default_intel)

if st.button("▶ EXECUTE EXECUTIVE IMPACT ANALYSIS", use_container_width=True):
    
    # NEW VALIDATION GATE
    if not validate_threat_input(threat_input):
        st.error("❌ Invalid or insufficient threat intelligence input. Please provide a real CVE advisory, security report, or detailed threat description.")
        st.stop()
        
    # --- STREAMING JSON EXTRACTION ---
    st.markdown("<h4 style='color:#00FFCC;'>1️⃣ Extracting Technologies & CVEs (Neural Analysis)...</h4>", unsafe_allow_html=True)
    extract_placeholder = st.empty()
    raw_json_str = ""
    for chunk in stream_extract_technologies_from_llm(threat_input):
        raw_json_str = chunk
        extract_placeholder.markdown(f"<div style='background-color:#050505; padding:15px; border-left:4px solid #00FFCC; border-radius:8px; font-family:monospace; color:#00FFCC; margin-bottom:15px;'>{raw_json_str}▌</div>", unsafe_allow_html=True)
    extract_placeholder.empty()

    extracted_data = None
    json_match = re.search(r'\{.*\}', raw_json_str, re.DOTALL)
    if json_match:
        try:
            extracted_data = json.loads(json_match.group(0))
        except Exception: 
            pass
            
    if not extracted_data or not extracted_data.get("technologies") or not extracted_data["technologies"][0].get("product"):
        extracted_data = deterministic_fallback(threat_input)

    # --- DETERMINISTIC ASSET MATCHING ---
    with st.spinner("2️⃣ Computing Mathematical Asset Exposure..."):
        matched_assets, max_score, level, total_assets = perform_asset_matching(extracted_data)
        
    # --- STREAMING SIEM QUERY ---
    st.markdown("<h4 style='color:#FF007F;'>3️⃣ Generating Dynamic Action Plan & Hunting Queries...</h4>", unsafe_allow_html=True)
    query_placeholder = st.empty()
    raw_query = ""
    for chunk in stream_generate_siem_query(threat_input, matched_assets, level, extracted_data.get('technologies', []), FAST_MODE):
        raw_query = chunk
        query_placeholder.markdown(f"<div style='background-color:#050505; padding:15px; border-left:4px solid #FF007F; border-radius:8px; font-family:monospace; color:#FF007F; margin-bottom:15px;'>{raw_query}▌</div>", unsafe_allow_html=True)
    query_placeholder.empty()

    match = re.search(r'```[a-zA-Z]*\n(.*?)```', raw_query, re.DOTALL)
    query = match.group(1).strip() if match else raw_query.strip()
    
    recs = get_dynamic_recommendations(level, extracted_data.get('technologies', []), matched_assets)
    
    final_output = {
        "extracted_technologies": extracted_data.get('technologies', []),
        "matched_assets": matched_assets,
        "relevance_score": max_score,
        "relevance_level": level,
        "cve_ids": extracted_data.get('cve_ids', []),
        "hunting_query": query, 
        "recommendations": recs,
        "total_assets": total_assets
    }

    save_structured_history(final_output)
    st.session_state.m2_result = final_output

# =======================================================
# 8. UI RENDERING (Calling mode2_ui.py)
# =======================================================
if 'm2_result' in st.session_state:
    render_mode2_dashboard(st.session_state.m2_result)