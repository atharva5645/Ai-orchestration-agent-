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
    
    if uploaded_file and st.button("Ingest into Local Vector DB"):
        with st.spinner("Chunking & Embedding..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                data = {"ticker": ticker}
                res = requests.post(f"{BACKEND_URL}/api/v1/documents/upload", files=files, data=data)
                if res.status_code == 200:
                    chunks = res.json().get("chunks_processed", 0)
                    st.success(f"Successfully vectorized {chunks} text chunks into ChromaDB!")
                else:
                    st.error(f"Ingestion failed: {res.text}")
            except Exception as e:
                st.error(f"API Error: {str(e)}")


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
        status_placeholder.info("🚀 Multi-Agent Workflow Triggered! Planner → Researcher → Analyst → Reporter...")
        with st.spinner("Deep Researching... This may take 30-60 seconds on free API tier."):
            payload = {
                "query": query,
                "company_symbol": ticker
            }
            try:
                res = requests.post(f"{BACKEND_URL}/api/v1/research/", json=payload, timeout=300)
                status_placeholder.empty()
                
                if res.status_code == 200:
                    data = res.json()
                    if data.get("status") == "error" or data.get("error"):
                        err_detail = data.get("error", "Unknown error from pipeline.")
                        error_msg = f"⚠️ **Pipeline Error:**\n\n```\n{err_detail}\n```"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    else:
                        report = data.get("final_report") or "The pipeline completed but produced no report."
                        st.markdown(report)
                        st.session_state.messages.append({"role": "assistant", "content": report})
                else:
                    error_msg = f"⚠️ **Backend HTTP {res.status_code}:**\n\n```\n{res.text}\n```"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except requests.exceptions.Timeout:
                status_placeholder.empty()
                err = "⏱️ **Request timed out** (5 min limit). The pipeline may still be running in the background — check Uvicorn logs."
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})
            except requests.exceptions.ConnectionError:
                status_placeholder.empty()
                err = "🔌 **Cannot connect to backend** at `http://127.0.0.1:8000`. Make sure Uvicorn is running!"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})
            except Exception as e:
                status_placeholder.empty()
                err = f"❌ **Unexpected error:** {str(e)}"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})
