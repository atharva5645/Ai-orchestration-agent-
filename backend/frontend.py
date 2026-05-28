import streamlit as st
import requests
import json

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
    if not company_symbol or not query:
        st.warning("Please enter both a company symbol and a research query.")
    else:
        # Prepare the payload
        payload = {
            "query": query,
            "company_symbol": company_symbol
        }

        with st.spinner("Agents are deeply researching the web and analyzing data. This may take a minute..."):
            try:
                # Call the FastAPI backend with a longer timeout
                response = requests.post("http://127.0.0.1:8000/api/v1/research/", json=payload, timeout=300)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    final_report = str(data.get("final_report", ""))

                    if "Query Rejected" in final_report or "We only provide answers" in final_report or "apologize" in final_report:
                        st.error(final_report)
                    else:
                        st.success("Research Complete!")
                        st.markdown("### Final Report")
                        st.markdown(f'<div class="report-box">{final_report}</div>', unsafe_allow_html=True)
                else:
                    st.error(f"Backend Error: {response.status_code}")
                    st.write(response.text)

            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to the backend: {e}")
                st.info("Make sure the Uvicorn server is running on http://127.0.0.1:8000")
