import sys
import os

# ================================
# FIX PYTHON PATH (CRITICAL)
# ================================
# This allows Streamlit (running from /ui)
# to find app.py and core/
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import streamlit as st
from app import run_intentguard

# ================================
# BASIC PAGE CONFIG
# ================================
st.set_page_config(
    page_title="INTENTGUARD",
    layout="centered"
)

# ================================
# UI HEADER (DEBUG CONFIRMATION)
# ================================
st.title("🛡️ INTENTGUARD – Safe Execution")
st.write("INTENTGUARD IS RUNNING ✅")

# ================================
# INPUT SECTION
# ================================
st.subheader("1️⃣ Upload Input Data")

uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx"]
)

st.subheader("2️⃣ Define Intent")

blocked_dates = st.text_input(
    "Dates NOT allowed (comma separated)",
    placeholder="2025-01-01,2025-01-26"
)

critical = st.checkbox("Critical data (high risk)")

st.subheader("3️⃣ Output Destination")

output_path = st.text_input(
    "Output path",
    value="data/output"
)

# ================================
# ACTION BUTTON
# ================================
st.subheader("4️⃣ Execute Safely")

if st.button("Validate & Execute"):
    if uploaded_file is None:
        st.warning("⚠️ Please upload a file before running.")
    else:
        try:
            result = run_intentguard(
                file=uploaded_file,
                blocked_dates=blocked_dates,
                critical=critical,
                output_path=output_path
            )

            st.success("Execution completed")
            st.json(result)

        except Exception as e:
            st.error("Execution failed ❌")
            st.exception(e)
