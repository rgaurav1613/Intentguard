import sys
import os

# ---------------------------------
# FIX PYTHON PATH (RENDER SAFE)
# ---------------------------------
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import streamlit as st
from app import run_intentguard

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(
    page_title="INTENTGUARD",
    layout="centered"
)

st.title("🛡️ INTENTGUARD")
st.caption("Block → Diagnose → Compare → (Correct → Resume)")

# ---------------------------------
# 1️⃣ FILE UPLOAD
# ---------------------------------
st.subheader("1️⃣ Upload Data")

uploaded_file = st.file_uploader(
    "Upload CSV / Excel / TSV / JSON",
    type=["csv", "xlsx", "xls", "tsv", "json"]
)

# ---------------------------------
# 2️⃣ DEFINE INTENT
# ---------------------------------
st.subheader("2️⃣ Define Intent")

unique_columns = st.text_input(
    "Columns that must be UNIQUE (comma separated)",
    placeholder="id"
)

required_columns = st.text_input(
    "Required columns (comma separated)",
    placeholder="email"
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

# ---------------------------------
# 3️⃣ EXECUTE
# ---------------------------------
st.subheader("3️⃣ Execute")

if st.button("Validate & Execute"):

    if uploaded_file is None:
        st.error("❌ Please upload a file")

    else:
        # Normalize intent inputs (IMPORTANT)
        intent_input = {
            "unique_columns": [c.strip().lower() for c in unique_columns.split(",") if c.strip()],
            "required_columns": [c.strip().lower() for c in required_columns.split(",") if c.strip()],
            "clean_required": clean_required,
            "max_rows": max_rows if max_rows > 0 else None
        }

        with st.spinner("Validating data against intent..."):
            result = run_intentguard(
                file=uploaded_file,
                intent_input=intent_input,
                output_path=output_path
            )

        st.divider()
        st.subheader("Result")

        # =========================================================
        # 🚫 BLOCKED CASE — V2.1 + V2.2 + V2.3
        # =========================================================
        if result["status"] == "BLOCKED":

            explanation = result["explanation"]
            diagnosis = result.get("diagnosis")

            st.error("🚫 Execution Blocked")

            # -----------------------------
            # WHY (V2.1)
            # -----------------------------
            st.markdown("### ❓ Why was this blocked?")
            st.json(explanation)

            # -----------------------------
            # WHERE (V2.2)
            # -----------------------------
            if diagnosis:
                st.markdown("### 📍 Where is the problem?")
                st.json(diagnosis)
            else:
                st.info("No location diagnostics available for this rule.")

            # -----------------------------
            # EXPECTED vs ACTUAL (V2.3)
            # -----------------------------
            st.markdown("### 🔍 Expected vs Actual")

            expected = []
            actual = []

            rule = explanation["rule"]

            # REQUIRED COLUMN
            if rule == "REQUIRED_COLUMN_MISSING":
                expected.append(
                    f"Column '{explanation['field']}' must exist"
                )
                actual.append(
                    "❌ Column not found in data"
                )

            # UNIQUE CONSTRAINT
            elif rule == "UNIQUE_CONSTRAINT_VIOLATION":
                expected.append(
                    f"Column '{explanation['field']}' must be unique"
                )
                actual.append(
                    f"Duplicate values found "
                    f"({diagnosis['estimated_affected_rows']} rows affected)"
                )

            # ROW LIMIT
            elif rule == "ROW_LIMIT_EXCEEDED":
                expected.append(
                    "Row count must be within allowed limit"
                )
                actual.append(
                    f"Exceeded by {diagnosis['estimated_affected_rows']} rows"
                )

            # Render comparison table
            compare_table = {
                "Expected (Intent)": expected,
                "Actual (Data)": actual
            }

            st.table(compare_table)

            st.info(
                "Fix the issue in the source data and re-run. "
                "Inline correction & resume will be added in the next V2 step."
            )

        # =========================================================
        # ✅ SUCCESS CASE
        # =========================================================
        else:

            st.success("✅ Execution Successful")

            st.json({
                "Rows processed": result["rows"],
                "Output file": result["output"]
            })

            # Render-safe download
            try:
                with open(result["output"], "rb") as f:
                    st.download_button(
                        label="⬇️ Download Output CSV",
                        data=f,
                        file_name=os.path.basename(result["output"]),
                        mime="text/csv"
                    )
            except Exception:
                st.warning(
                    "Output generated but could not be loaded for download."
                )
