def validate_data(df, intent):
    schema_snapshot = {
        "columns": list(df.columns),
        "dtypes": {c: str(df[c].dtype) for c in df.columns},
        "row_count": len(df)
    }

    for col in intent["presence"]["required"]:
        if col not in df.columns:
            return {
                "ok": False,
                "schema_snapshot": schema_snapshot,
                "explanation": {
                    "rule": "REQUIRED_COLUMN_MISSING",
                    "field": col,
                    "severity": "HIGH",
                    "impact": "Execution stopped",
                    "message": f"Required column '{col}' is missing"
                },
                "diagnosis": _diagnose_missing_column(df, col)
            }

    for col in intent["identity"]["unique"]:
        if col in df.columns and df[col].duplicated().any():
            return {
                "ok": False,
                "schema_snapshot": schema_snapshot,
                "explanation": {
                    "rule": "UNIQUE_CONSTRAINT_VIOLATION",
                    "field": col,
                    "severity": "HIGH",
                    "impact": "Execution stopped",
                    "message": f"Duplicate values found in column '{col}'"
                },
                "diagnosis": _diagnose_duplicates(df, col)
            }

    max_rows = intent["risk"].get("max_rows")
    if max_rows and len(df) > max_rows:
        return {
            "ok": False,
            "schema_snapshot": schema_snapshot,
            "explanation": {
                "rule": "ROW_LIMIT_EXCEEDED",
                "severity": "MEDIUM",
                "impact": "Execution stopped",
                "message": f"Row count {len(df)} exceeds allowed maximum {max_rows}"
            },
            "diagnosis": _diagnose_row_limit(df, max_rows)
        }

    return {"ok": True}
