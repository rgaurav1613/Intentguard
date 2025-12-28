# core/validator.py

SEVERITY_ORDER = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4
}


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
        row_range = f"Rows ~{int(dup_rows.index.min())} to ~{int(dup_rows.index.max())}"
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
        "estimated_affected_rows": max(0, len(df) - max_rows),
        "row_range": f"Rows > {max_rows}",
        "sample_rows": [],
        "sample_values": []
    }


def validate_data(df, intent):
    """
    MULTI-rule validator
    Returns all violations in one run
    """

    violations = []

    schema_snapshot = {
        "columns": list(df.columns),
        "dtypes": {c: str(df[c].dtype) for c in df.columns},
        "row_count": len(df)
    }

    # -----------------------------
    # REQUIRED COLUMNS
    # -----------------------------
    for col in intent.get("presence", {}).get("required", []):
        if col not in df.columns:
            violations.append({
                "explanation": {
                    "rule": "REQUIRED_COLUMN_MISSING",
                    "field": col,
                    "severity": "HIGH",
                    "impact": "Execution stopped",
                    "message": f"Required column '{col}' is missing"
                },
                "diagnosis": _diagnose_missing_column(df, col)
            })

    # -----------------------------
    # UNIQUE CONSTRAINTS
    # -----------------------------
    for col in intent.get("identity", {}).get("unique", []):
        if col in df.columns and df[col].duplicated().any():
            violations.append({
                "explanation": {
                    "rule": "UNIQUE_CONSTRAINT_VIOLATION",
                    "field": col,
                    "severity": "HIGH",
                    "impact": "Execution stopped",
                    "message": f"Duplicate values found in column '{col}'"
                },
                "diagnosis": _diagnose_duplicates(df, col)
            })

    # -----------------------------
    # ROW LIMIT
    # -----------------------------
    max_rows = intent.get("risk", {}).get("max_rows")
    if max_rows is not None and len(df) > max_rows:
        violations.append({
            "explanation": {
                "rule": "ROW_LIMIT_EXCEEDED",
                "field": None,
                "severity": "MEDIUM",
                "impact": "Execution stopped",
                "message": f"Row count {len(df)} exceeds allowed maximum {max_rows}"
            },
            "diagnosis": _diagnose_row_limit(df, max_rows)
        })

    # -----------------------------
    # FINAL DECISION
    # -----------------------------
    if violations:
        highest_severity = max(
            (v["explanation"]["severity"] for v in violations),
            key=lambda s: SEVERITY_ORDER[s]
        )

        return {
            "ok": False,
            "violations": violations,
            "schema_snapshot": schema_snapshot,
            "highest_severity": highest_severity
        }

    return {"ok": True}
