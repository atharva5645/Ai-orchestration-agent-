import streamlit as st
import requests
import json

import re

# Set up the page configuration
st.set_page_config(
    page_title="Deep Research AI",
    page_icon="📈",
    layout="centered"
)

# Custom CSS for aesthetics
st.markdown("""
<style>
    .report-box {
        background-color: #1E1E1E;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Deep Research AI")
st.markdown("Enter a company symbol and a specific financial query to generate a professional, multi-agent equity research report.")

# Input fields
col1, col2 = st.columns([1, 3])
with col1:
    company_symbol = st.text_input("Company Symbol", placeholder="e.g., AAPL")
with col2:
    query = st.text_input("Research Query", placeholder="e.g., Analyze recent hardware sales and profit margins.")

# Submit button
if st.button("Generate Research Report", type="primary"):
    if not query or not query.strip():
        st.warning("Please enter a question")
    elif not company_symbol:
        st.warning("Please enter both a company symbol and a research query.")
    else:
        # Prepare the payload
        payload = {
            "query": query.strip(),
            "company_symbol": company_symbol.strip()
        }

        status_placeholder = st.empty()
        report_placeholder = st.empty()
        
        import threading
        import time
        from streamlit.runtime.scriptrunner import add_script_run_ctx

        # Shared state for thread communication
        thread_state = {"is_running": True, "result": None, "error": None}

        def fetch_data():
            try:
                # Backend is now a single blocking call (simulated or real)
                response = requests.post("http://127.0.0.1:8000/api/v1/research/", json=payload, timeout=300)
                if response.status_code == 200:
                    data = response.json() if "application/json" in response.headers.get("Content-Type", "") else None
                    if not data:
                        # Fallback for ndjson stream if it's still returning stream
                        lines = [line.decode('utf-8') for line in response.iter_lines() if line]
                        for line in lines:
                            try:
                                d = json.loads(line)
                                if d.get("type") == "complete":
                                    thread_state["result"] = d.get("final_report", "")
                                elif d.get("type") == "error":
                                    thread_state["error"] = d.get("message", "Unknown error")
                            except Exception:
                                pass
                    else:
                        thread_state["result"] = data.get("final_report", "")
                else:
                    thread_state["error"] = f"Backend Error: {response.status_code}"
            except requests.exceptions.RequestException as e:
                thread_state["error"] = f"Failed to connect to the backend: {e}"
            finally:
                thread_state["is_running"] = False

        # Start background thread
        req_thread = threading.Thread(target=fetch_data)
        add_script_run_ctx(req_thread)
        req_thread.start()

        # Simulated progress steps
        steps = [
            "🔍 Searching the web...",
            "📊 Fetching stock data...",
            "🧠 Analysing findings...",
            "✍️ Writing your report..."
        ]
        
        step_idx = 0
        while thread_state["is_running"]:
            if step_idx < len(steps):
                status_placeholder.info(steps[step_idx])
                step_idx += 1
            # Sleep in chunks to keep UI responsive
            for _ in range(20): 
                if not thread_state["is_running"]:
                    break
                time.sleep(0.1)

        req_thread.join()

        if thread_state["error"]:
            status_placeholder.error(thread_state["error"])
        elif thread_state["result"]:
            status_placeholder.success("Research Complete!")
            final_report = str(thread_state["result"])
            
            if "Query Rejected" in final_report or "We only provide answers" in final_report or "apologize" in final_report:
                report_placeholder.error(final_report)
            else:
                with report_placeholder.container():
                    st.markdown("### Final Report")
                    
                    lines = final_report.split('\n')
                    sections = []
                    current_title = ""
                    current_content = []
                    
                    for line in lines:
                        if re.match(r'^##\s+', line):
                            if current_title or current_content:
                                sections.append((current_title, current_content))
                            current_title = re.sub(r'^##\s+', '', line).strip()
                            current_content = []
                        else:
                            current_content.append(line)
                            
                    if current_title or current_content:
                        sections.append((current_title, current_content))
                        
                    for i, (title, content) in enumerate(sections):
                        is_expanded = (i == 0) # Only first section expanded
                        with st.expander(title if title else "Overview", expanded=is_expanded):
                            st.markdown('\n'.join(content))
