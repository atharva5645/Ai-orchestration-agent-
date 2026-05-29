import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="Financial Deep Research Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Financial Deep Research Agent 🤖📊")
st.markdown("Ask complex financial questions and our multi-agent pipeline will generate a comprehensive Wall-Street grade report.")

# --- BACKEND STATUS CHECK ---
try:
    health = requests.get(f"{BACKEND_URL}/health/", timeout=3)
    if health.status_code == 200:
        st.sidebar.success("✅ Backend: Online")
    else:
        st.sidebar.warning(f"⚠️ Backend: Unexpected status {health.status_code}")
except Exception:
    st.sidebar.error("❌ Backend: Offline — Start Uvicorn first!")

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Target Asset")
    ticker = st.text_input(
        "Optional: Stock Ticker Symbol", 
        value="", 
        help="Leave blank to let the AI automatically extract the ticker from your query (e.g. AAPL, TSLA, MSFT)"
    )
    
    st.divider()
    
    st.header("📄 Knowledge Base")
    st.markdown("Upload internal PDFs, 10-Ks, or Annual Reports to ingest into the local RAG engine.")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    
    if uploaded_file is not None:
        st.success(f"📄 {uploaded_file.name} selected")
        if st.button("⚡ Ingest into Local Vector DB"):
            progress_text = st.empty()
            progress_text.info("⏳ Reading and chunking PDF...")
            try:
                files = {"file": (uploaded_file.name, 
                         uploaded_file.getvalue(), 
                         "application/pdf")}
                data = {"ticker": ticker or "UNKNOWN"}
                progress_text.info("🧠 Embedding chunks into ChromaDB...")
                res = requests.post(
                    f"{BACKEND_URL}/api/v1/documents/upload",
                    files=files,
                    data=data,
                    timeout=300
                )
                progress_text.empty()
                if res.status_code == 200:
                    data_json = res.json()
                    chunks = data_json.get("chunks_processed", 0)
                    time_taken = data_json.get("time_taken")
                    
                    if time_taken:
                        st.success(f"✅ Successfully vectorized {chunks} chunks into ChromaDB in {time_taken:.1f}s!")
                    else:
                        st.success(f"✅ Successfully vectorized {chunks} chunks into ChromaDB!")
                else:
                    st.error(f"❌ Ingestion failed: {res.text}")
            except Exception as e:
                progress_text.empty()
                st.error(f"❌ Error: {str(e)}")


# --- MAIN CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

query = st.chat_input("Research any company, ETF, or trend (e.g., 'Provide me research on HDFC silver etf')...")

if query:
    st.chat_message("user").write(query)
    st.session_state.messages.append({"role": "user", "content": query})
    
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        status_placeholder.info("🚀 Multi-Agent Workflow Triggered! Router → Finance → Researcher+Analyst → Reporter...")
        
        payload = {
            "query": query,
            "company_symbol": ticker
        }
        
        import threading
        import time
        from streamlit.runtime.scriptrunner import add_script_run_ctx

        result = {"data": None, "error": None, "done": False}

        def fetch_data():
            try:
                res = requests.post(f"{BACKEND_URL}/api/v1/research/", json=payload, timeout=300)
                if res.status_code == 200:
                    result["data"] = res.json()
                else:
                    result["error"] = f"⚠️ **Backend HTTP {res.status_code}:**\n\n```\n{res.text}\n```"
            except requests.exceptions.Timeout:
                result["error"] = "⏱️ **Request timed out** (5 min limit). The pipeline may still be running in the background — check Uvicorn logs."
            except requests.exceptions.ConnectionError:
                result["error"] = f"🔌 **Cannot connect to backend** at `{BACKEND_URL}`. Make sure Uvicorn is running!"
            except Exception as e:
                result["error"] = f"❌ **Unexpected error:** {str(e)}"
            finally:
                result["done"] = True

        req_thread = threading.Thread(target=fetch_data)
        add_script_run_ctx(req_thread)
        req_thread.start()

        step_status = st.status("Initializing...", expanded=True)
        start_time = time.time()
        
        current_label = "Initializing..."
        while not result["done"]:
            elapsed = time.time() - start_time
            if elapsed < 15:
                new_label = "🔍 Searching the web for latest data..."
            elif elapsed < 30:
                new_label = "📊 Fetching live stock data from Yahoo Finance..."
            elif elapsed < 50:
                new_label = "🧠 Analysing and cross-referencing findings..."
            else:
                new_label = "✍️ Writing your research report..."
                
            if new_label != current_label:
                step_status.update(label=new_label, state="running")
                current_label = new_label
                
            time.sleep(0.1)

        req_thread.join()
        status_placeholder.empty()
        step_status.update(label="✅ Research Complete!", state="complete", expanded=False)

        if result["error"]:
            st.error(result["error"])
            st.session_state.messages.append({"role": "assistant", "content": result["error"]})
        else:
            data = result["data"]
            if data.get("status") == "error" or data.get("error"):
                err_detail = data.get("error", "Unknown error from pipeline.")
                error_msg = f"⚠️ **Pipeline Error:**\n\n```\n{err_detail}\n```"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            else:
                report = data.get("final_report") or "The pipeline completed but produced no report."
                
                import re
                # Split on any line that starts with ## followed by a number
                sections = re.split(r'\n(?=## \d)', report.strip())
                
                if len(sections) > 1:
                    # First block is the report title (before first ## heading)
                    title_block = sections[0].strip()
                    if title_block:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(90deg, #1a1a2e, #16213e);
                            padding: 16px 20px;
                            border-radius: 8px;
                            border-left: 4px solid #00d4aa;
                            margin-bottom: 16px;
                        ">
                            <h2 style="color: #00d4aa; margin: 0; font-size: 1.4em;">
                                📊 {title_block}
                            </h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    for i, section in enumerate(sections[1:]):
                        lines = section.strip().split("\n", 1)
                        section_title = lines[0].replace("##", "").strip()
                        section_body = lines[1].strip() if len(lines) > 1 else ""
                        # Section 1 (Executive Summary) expanded, rest collapsed
                        with st.expander(section_title, expanded=(i == 0)):
                            st.markdown(section_body)
                else:
                    st.markdown(report)
                    
                st.session_state.messages.append({"role": "assistant", "content": report})
