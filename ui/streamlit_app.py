import streamlit as st
from app import run_intentguard

st.set_page_config(page_title="INTENTGUARD", layout="centered")

st.title("🛡️ INTENTGUARD – Safe Data Execution")

file = st.file_uploader("Upload CSV / Excel")

blocked_dates = st.text_input(
    "Dates NOT allowed (comma separated)",
    "2025-01-26"
)

critical = st.checkbox("Critical Data")

output_path = st.text_input(
    "Output Path",
    "data/output"
)

if st.button("Validate & Execute"):
    if file is None:
        st.error("Upload a file")
    else:
        result = run_intentguard(
            file=file,
            blocked_dates=blocked_dates,
            critical=critical,
            output_path=output_path
        )
        st.json(result)
