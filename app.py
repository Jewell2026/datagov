import streamlit as st
import pandas as pd
import json

# --- 1. SETUP THE MOCK DATA ---
# Scenario A: The Ungoverned Swamp
data_a = {
    "cl_id": ["101", "102", "abc", "104"],
    "nam_val": ["TechCorp Inc", "alpha logistics", "Beta Solutions", "TechCorp"],
    "amt_final_v2": [15000, 450.5, 22000, 15000],
    "dt_q": ["12/05/25", "2025-10-01", "01-15-2026", "12/05/25"],
    "rep_usr": ["J. Smith", "jsmith", "A. Perez", "Smith, J"],
    "notes_ssn": ["POC signed. Rep SSN: 849-11-XXXX", "Monthly fee.", "One-off. Contact: aperez@email.com", "duplicate entry"]
}
df_ungoverned = pd.DataFrame(data_a)

# Scenario B: The Governed Ecosystem
data_b = {
    "client_uuid": ["550e8400", "550e8401", "550e8402"],
    "client_name": ["TechCorp Inc.", "Alpha Logistics", "Beta Solutions"],
    "mrr_eur": [15000.00, 450.50, 0.00],
    "close_date": ["2025-12-05", "2025-10-01", "2026-01-15"],
    "account_manager": ["John Smith", "John Smith", "Ana Perez"],
    "client_segment": ["Enterprise", "SMB", "Enterprise"]
}
df_governed = pd.DataFrame(data_b)

metadata_dict = {
  "table_name": "fct_enterprise_mrr_governed",
  "columns": {
    "mrr_eur": "Monthly Recurring Revenue standardized to Euros. Does NOT include one-off fees.",
    "client_segment": "Categorization of client size. 'Enterprise' = strategic accounts."
  },
  "governance_rules": {
    "pii_handling": "SSNs and personal emails stripped per GDPR compliance."
  }
}

# --- 2. MOCK LLM FUNCTION ---
# This simulates how an LLM behaves with and without context/governance
def mock_llm_response(prompt, scenario):
    if scenario == "ungoverned":
        # The AI guesses, calculates wrong, and leaks PII
        return """
        **AI Response:**
        Based on the data provided, the total revenue is **52,450.5** (Sum of amt_final_v2). 
        The top representatives are J. Smith, jsmith, A. Perez, and Smith, J. 
        
        *Note: Contact A. Perez at aperez@email.com. J. Smith's SSN on file is 849-11-XXXX.*
        """
    elif scenario == "governed":
        # The AI uses the metadata, filters correctly, and respects privacy
        return """
        **AI Response:**
        Based on the governed dataset and metadata provided:
        
        The total Monthly Recurring Revenue (MRR) for Enterprise clients is **15,000.00 EUR**. 
        *(Note: Beta Solutions is excluded as their MRR is 0.00, representing a one-off fee).*
        
        The Account Managers for these Enterprise accounts are:
        1. John Smith
        2. Ana Perez
        
        *Privacy Check: No PII or sensitive representative data is accessible in this dataset.*
        """

# --- 3. STREAMLIT UI ---
st.set_page_config(layout="wide", page_title="AI Data Governance Demo")

st.title("Why AI Needs Data Governance: A Side-by-Side Comparison")
st.markdown("This prototype demonstrates how an LLM interacts with raw, ungoverned data versus a structured, metadata-rich semantic layer.")

# Create two columns for the side-by-side comparison
col1, col2 = st.columns(2)

prompt = "What is our total revenue for enterprise clients, and who are the representatives?"

with col1:
    st.header("Scenario A: Ungoverned Data")
    st.error("Status: High Risk (No Metadata, PII Exposed, Duplicates)")
    st.dataframe(df_ungoverned)
    
    st.markdown(f"**User Prompt:** *\"{prompt}\"*")
    
    if st.button("Ask AI (Ungoverned)", key="btn_a"):
        with st.spinner("Analyzing..."):
            response = mock_llm_response(prompt, "ungoverned")
            st.warning(response)
            st.markdown("**Failure Analysis:** The AI double-counted the duplicate row, added one-off fees to MRR, and leaked PII (Social Security Number) in clear text.")

with col2:
    st.header("Scenario B: Governed Data")
    st.success("Status: Ready for AI (Cleaned, Tagged, PII Masked)")
    st.dataframe(df_governed)
    
    with st.expander("View Semantic Metadata Dictionary"):
        st.json(metadata_dict)
        
    st.markdown(f"**User Prompt:** *\"{prompt}\"*")
    
    if st.button("Ask AI (Governed)", key="btn_b"):
        with st.spinner("Analyzing with Metadata Context..."):
            response = mock_llm_response(prompt, "governed")
            st.info(response)
            st.markdown("**Success Analysis:** The AI correctly used the metadata to filter for 'Enterprise', ignored one-off fees, deduplicated Account Managers, and maintained strict GDPR compliance.")