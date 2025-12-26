# core/validator.py

def validate_data(df, intent):
    """
    Validates data against intent.
    Returns structured explainability on failure.
    """

    # -----------------------------
    # REQUIRED COLUMNS
    # -----------------------------
    for col in intent["presence"]["required"]:
        if col not in df.columns:
            return {
                "ok": False,
                "explanation": {
                    "rule": "REQUIRED_COLUMN_MISSING",
                    "field": col,
                    "severity": "HIGH",
                    "impact": "Execution stopped",
                    "message": f"Required column '{col}' is missing"
                }
            }

    # -----------------------------
    # UNIQUE CONSTRAINTS
    # -----------------------------
    for col in intent["identity"]["unique"]:
        if col in df.columns and df[col].duplicated().any():
            return {
                "ok": False,
                "explanation": {
                    "rule": "UNIQUE_CONSTRAINT_VIOLATION",
                    "field": col,
                    "severity": "HIGH",
                    "impact": "Execution stopped",
                    "message": f"Duplicate values found in column '{col}'"
                }
            }

    # -----------------------------
    # MAX ROWS (RISK CONTROL)
    # -----------------------------
    max_rows = intent["risk"].get("max_rows")
    if max_rows and len(df) > max_rows:
        return {
            "ok": False,
            "explanation": {
                "rule": "ROW_LIMIT_EXCEEDED",
                "field": None,
                "severity": "MEDIUM",
                "impact": "Execution stopped",
                "message": f"Row count {len(df)} exceeds allowed maximum {max_rows}"
            }
        }

    # -----------------------------
    # PASS
    # -----------------------------
    return {"ok": True}
