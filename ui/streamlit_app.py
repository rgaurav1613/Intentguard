# ui/streamlit_app.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from app import run_intentguard

st.set_page_config(page_title="INTENTGUARD", layout="centered")

st.title("🛡️ INTENTGUARD – Safe Execution")

# -------------------------
# FILE INPUT
# -------------------------
uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx"]
)

# -------------------------
# INTENT INPUT
# -------------------------
st.subheader("🧠 Intent")

required_columns = st.text_input(
    "Required columns (comma separated)",
    placeholder="customer_id,email"
)

unique_columns = st.text_input(
    "Unique columns (comma separated)",
    placeholder="customer_id"
)

# -------------------------
# RESUME SUPPORT
# -------------------------
st.subheader("🔁 Resume (optional)")

execution_id = st.text_input(
    "Execution ID",
    placeholder="Paste execution_id here to resume"
)

# -------------------------
# OUTPUT
# -------------------------
output_path = st.text_input(
    "Output path",
    value="data/output"
)

# -------------------------
# ACTION
# -------------------------
if st.button("Validate / Resume"):
    if uploaded_file is None:
        st.warning("Please upload a file")
    else:
        intent_input = {
            "required_columns": [
                c.strip() for c in required_columns.split(",") if c.strip()
            ],
            "unique_columns": [
                c.strip() for c in unique_columns.split(",") if c.strip()
            ],
            "clean_required": True
        }

        result = run_intentguard(
            file=uploaded_file,
            intent_input=intent_input,
            output_path=output_path,
            execution_id=execution_id if execution_id else None
        )

        st.subheader("Result")
        st.json(result)

        if result.get("status") == "BLOCKED":
            st.error("Execution blocked. Fix the issue and resume using execution_id.")
