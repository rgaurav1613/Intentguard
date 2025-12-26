import sys
import os

# Fix Python path for Render
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import streamlit as st
from app import run_intentguard

st.set_page_config(page_title="INTENTGUARD", layout="centered")

st.title("🛡️ INTENTGUARD – Data Execution Safety")

# -----------------------
# Upload
# -----------------------
uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx"]
)

# -----------------------
# Intent Section
# -----------------------
st.subheader("🧠 Define Intent")

unique_columns = st.text_input(
    "Columns that must be UNIQUE (comma separated)",
    placeholder="customer_id"
)

required_columns = st.text_input(
    "Required columns (comma separated)",
    placeholder="customer_id,email"
)

clean_required = st.checkbox(
    "Clean data before output",
    value=True
)

max_rows = st.number_input(
    "Maximum allowed rows (optional)",
    min_value=0,
    step=1000
)

output_path = st.text_input(
    "Output path (internal)",
    value="data/output"
)

# -----------------------
# Execute
# -----------------------
if st.button("Validate & Execute"):
    if uploaded_file is None:
        st.error("Please upload a file")
    else:
        intent_input = {
            "unique_columns": [c.strip() for c in unique_columns.split(",") if c.strip()],
            "required_columns": [c.strip() for c in required_columns.split(",") if c.strip()],
            "clean_required": clean_required,
            "max_rows": max_rows if max_rows > 0 else None
        }

        result = run_intentguard(
            file=uploaded_file,
            intent_input=intent_input,
            output_path=output_path
        )

        st.subheader("Result")
        st.json(result)

        # -----------------------
        # Download Output (CRITICAL FOR RENDER)
        # -----------------------
        if result["status"] == "SUCCESS":
            try:
                with open(result["output"], "rb") as f:
                    st.download_button(
                        label="⬇️ Download Output CSV",
                        data=f,
                        file_name=os.path.basename(result["output"]),
                        mime="text/csv"
                    )
            except Exception as e:
                st.warning("Output generated but could not be loaded for download")
                st.exception(e)
