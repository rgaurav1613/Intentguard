import sys
import os

# -------------------------------
# Fix Python path (RENDER SAFE)
# -------------------------------
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import streamlit as st
from app import run_intentguard

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="INTENTGUARD",
    layout="centered"
)

st.title("🛡️ INTENTGUARD")
st.caption("Prevention-first data execution")

# -------------------------------
# FILE UPLOAD
# -------------------------------
st.subheader("1️⃣ Upload Data")

uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx"]
)

# -------------------------------
# INTENT DEFINITION
# -------------------------------
st.subheader("2️⃣ Define Intent")

unique_columns = st.text_input(
    "Columns that must be UNIQUE",
    placeholder="customer_id"
)

required_columns = st.text_input(
    "Required columns",
    placeholder="customer_id,email"
)

clean_required = st.checkbox(
    "Clean data if validation passes",
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

# -------------------------------
# EXECUTION
# -------------------------------
st.subheader("3️⃣ Execute")

if st.button("Validate & Execute"):
    if uploaded_file is None:
        st.error("❌ Please upload a file first")
    else:
        intent_input = {
            "unique_columns": [c.strip() for c in unique_columns.split(",") if c.strip()],
            "required_columns": [c.strip() for c in required_columns.split(",") if c.strip()],
            "clean_required": clean_required,
            "max_rows": max_rows if max_rows > 0 else None
        }

        with st.spinner("Validating data against intent..."):
            result = run_intentguard(
                file=uploaded_file,
                intent_input=intent_input,
                output_path=output_path
            )

        # -------------------------------
        # RESULT HANDLING (V2.1)
        # -------------------------------
        st.divider()
        st.subheader("Result")

        if result["status"] == "BLOCKED":
            st.error("🚫 Execution Blocked")

            explanation = result["explanation"]

            st.markdown("### ❓ Why was this blocked?")
            st.json(explanation)

            if "diagnosis" in result and result["diagnosis"]:
            st.markdown("### 📍 Where is the problem?")
            st.json(result["diagnosis"])

            st.info(
                "Fix the issue in the source data and re-run. "
                "Correction & resume will be added in V2.3."
            )

        else:
            st.success("✅ Execution Successful")
            st.json({
                "Rows processed": result["rows"],
                "Output file": result["output"]
            })

            # -------------------------------
            # DOWNLOAD (RENDER SAFE)
            # -------------------------------
            try:
                with open(result["output"], "rb") as f:
                    st.download_button(
                        label="⬇️ Download Output CSV",
                        data=f,
                        file_name=os.path.basename(result["output"]),
                        mime="text/csv"
                    )
            except Exception:
                st.warning("Output generated but could not be loaded for download.")

