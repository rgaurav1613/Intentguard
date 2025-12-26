import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import streamlit as st
from app import run_intentguard

st.set_page_config(page_title="INTENTGUARD", layout="centered")
st.title("🛡️ INTENTGUARD")
st.caption("Block → Diagnose → Compare → Clarity")

# ---------------- Upload ----------------
st.subheader("1️⃣ Upload Data")
uploaded_file = st.file_uploader(
    "Upload CSV / Excel / TSV / JSON",
    type=["csv", "xlsx", "xls", "tsv", "json"]
)

# ---------------- Intent ----------------
st.subheader("2️⃣ Define Intent")

unique_columns = st.text_input("Unique columns", placeholder="id")
required_columns = st.text_input(
    "Required columns",
    placeholder="actual gross(in 2022 dollars)"
)

clean_required = st.checkbox("Clean data if valid", True)
max_rows = st.number_input("Max rows (optional)", min_value=0, step=1000)
output_path = st.text_input("Output path", "data/output")

# ---------------- Execute ----------------
st.subheader("3️⃣ Execute")

if st.button("Validate & Execute"):

    if uploaded_file is None:
        st.error("Please upload a file")
    else:
        intent_input = {
            "unique_columns": [c.strip().lower() for c in unique_columns.split(",") if c.strip()],
            "required_columns": [c.strip().lower() for c in required_columns.split(",") if c.strip()],
            "clean_required": clean_required,
            "max_rows": max_rows if max_rows > 0 else None
        }

        with st.spinner("Running INTENTGUARD..."):
            result = run_intentguard(
                uploaded_file,
                intent_input,
                output_path
            )

        st.divider()
        st.subheader("Result")

        # ================= BLOCKED =================
        if result["status"] == "BLOCKED":

            st.error("🚫 Execution Blocked")

            st.markdown("### ❓ Why was this blocked?")
            st.json(result["explanation"])

            st.markdown("### 📍 Where is the problem?")
            st.json(result["diagnosis"])

            st.markdown("### 🔍 Expected vs Actual")
            st.table({
                "Expected (Intent)": [
                    f"Column '{result['explanation']['field']}' must exist"
                ],
                "Actual (Data)": [
                    "Column not found (header mismatch)"
                ]
            })

            # ⭐ THIS IS THE CRITICAL CLARITY
            st.markdown("### 🧾 Columns detected in file")
            st.code("\n".join(result.get("detected_columns", [])))

            st.info(
                "Copy the exact column name shown above into intent "
                "OR fix the source file header."
            )

        # ================= SUCCESS =================
        else:
            st.success("Execution Successful")
            st.json(result)
