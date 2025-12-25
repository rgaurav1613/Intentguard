import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.intake import load_input
from core.intent import parse_intent
from core.validator import validate_data
from core.risk_engine import calculate_risk
from core.cleaner import clean_data
from core.router import deliver_output
from core.memory import record_event

def run_intentguard(file, blocked_dates, critical, output_path):

    df = load_input(file)

    intent = parse_intent(blocked_dates, critical)

    validation_result = validate_data(df, intent)
    if not validation_result["ok"]:
        return {"status": "BLOCKED", "reason": validation_result["reason"]}

    risk = calculate_risk(df, intent)

    if risk == "HIGH":
        record_event("BLOCKED", "High risk execution")
        return {"status": "BLOCKED", "risk": risk}

    clean_df = clean_data(df)

    output_file = deliver_output(clean_df, output_path)

    record_event("SUCCESS", f"Delivered to {output_file}")

    return {
        "status": "SUCCESS",
        "risk": risk,
        "output": output_file
    }
