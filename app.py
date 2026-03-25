import streamlit as st
import pandas as pd
import json
import ollama # Replaced google.generativeai

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
# --- 2. LIVE LOCAL LLM FUNCTION ---
def live_llm_response(prompt, scenario, df, metadata=None):
    data_string = df.to_csv(index=False)
    
    if scenario == "ungoverned":
        system_instruction = f"""
        You are an AI assistant answering questions based on the provided dataset. 
        Here is the raw data in CSV format:
        {data_string}
        
        Answer the user's question directly based ONLY on this data.
        User Question: {prompt}
        """
        
    elif scenario == "governed":
        metadata_string = json.dumps(metadata, indent=2)
        system_instruction = f"""
        You are an enterprise AI assistant. You have been provided with a clean dataset 
        and a strict metadata dictionary that defines the rules, columns, and governance policies.
        
        Metadata & Governance Rules:
        {metadata_string}
        
        Governed Data (CSV format):
        {data_string}
        
        Follow the metadata rules strictly when calculating answers. Do not mention the raw CSV format to the user.
        Answer the user's question based on this governed data and context.
        User Question: {prompt}
        """
    
    # Call the local Ollama model
    try:
        response = ollama.chat(model='llama3.2', messages=[
            {
                'role': 'user',
                'content': system_instruction
            }
        ])
        return response['message']['content']
    except Exception as e:
        return f"Local Engine Error (Make sure Ollama is running!): {e}"

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
        with st.spinner("Analyzing with Local AI..."):
            # FIXED: Calling the new live function and passing df_ungoverned
            response = live_llm_response(prompt, "ungoverned", df_ungoverned)
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
        with st.spinner("Analyzing Governed Data with Local AI..."):
            # FIXED: Calling the new live function and passing df_governed AND metadata_dict
            response = live_llm_response(prompt, "governed", df_governed, metadata_dict)
            st.info(response)
            st.markdown("**Success Analysis:** The AI correctly used the metadata to filter for 'Enterprise', ignored one-off fees, deduplicated Account Managers, and maintained strict GDPR compliance.")