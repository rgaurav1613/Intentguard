# core/validator.py

def _diagnose_missing_column(df, column):
    return {
        "issue_type": "MISSING_COLUMN",
        "column": column,
        "estimated_affected_rows": len(df),
        "row_range": "Entire file",
        "sample_rows": [],
        "sample_values": []
    }


def _diagnose_duplicates(df, column, sample_size=5):
    dup_mask = df[column].duplicated(keep=False)
    dup_rows = df[dup_mask]

    sample = dup_rows.head(sample_size)

    if len(dup_rows) > 0:
        first_idx = int(dup_rows.index.min())
        last_idx = int(dup_rows.index.max())
        row_range = f"Rows ~{first_idx} to ~{last_idx}"
    else:
        row_range = "Unknown"

    return {
        "issue_type": "DUPLICATE_VALUES",
        "column": column,
        "estimated_affected_rows": int(len(dup_rows)),
        "row_range": row_range,
        "sample_rows": sample.index.tolist(),
        "sample_values": sample[column].tolist()
    }


def _diagnose_row_limit(df, max_rows):
    return {
        "issue_type": "ROW_LIMIT_EXCEEDED",
        "column": None,
        "estimated_affected_rows": len(df) - max_rows,
        "row_range": f"Rows > {max_rows}",
        "sample_rows": [],
        "sample_values": []
    }


def validate_data(df, intent):
    """
    Validate data and return explainability + diagnosis on failure.
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
                },
                "diagnosis": _diagnose_missing_column(df, col)
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
                },
                "diagnosis": _diagnose_duplicates(df, col)
            }

    # -----------------------------
    # MAX ROWS
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
            },
            "diagnosis": _diagnose_row_limit(df, max_rows)
        }

    return {"ok": True}
