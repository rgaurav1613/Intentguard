from datetime import datetime

def validate_data(df, intent):
    if "run_date" not in df.columns:
        return {"ok": False, "reason": "Missing run_date column"}

    for d in df["run_date"].astype(str):
        if d in intent["blocked_dates"]:
            return {"ok": False, "reason": f"Blocked date detected: {d}"}

    return {"ok": True}
