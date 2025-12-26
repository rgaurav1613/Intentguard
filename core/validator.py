def validate_data(df, intent):

    # Required columns
    for col in intent["presence"]["required"]:
        if col not in df.columns:
            return {
                "ok": False,
                "reason": f"Missing required column: {col}"
            }

    # Unique constraints
    for col in intent["identity"]["unique"]:
        if col in df.columns and df[col].duplicated().any():
            return {
                "ok": False,
                "reason": f"Duplicate values found in column: {col}"
            }

    # Risk: max rows
    max_rows = intent["risk"]["max_rows"]
    if max_rows and len(df) > max_rows:
        return {
            "ok": False,
            "reason": f"Row count exceeds allowed maximum ({max_rows})"
        }

    return {"ok": True}
