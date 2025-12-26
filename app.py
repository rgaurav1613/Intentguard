import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.intake import load_input
from core.intent import parse_intent
from core.validator import validate_data
from core.cleaner import clean_data
from core.router import deliver_output
from core.memory import record_event

def run_intentguard(file, intent_input, output_path):

    df = load_input(file)

    intent = parse_intent(intent_input)

    validation = validate_data(df, intent)
    if not validation["ok"]:
        record_event("BLOCKED", validation["reason"])
        return {
            "status": "BLOCKED",
            "reason": validation["reason"]
        }

    clean_df = clean_data(df, intent)

    output_file = deliver_output(clean_df, output_path)

    record_event("SUCCESS", f"Output written to {output_file}")

    return {
        "status": "SUCCESS",
        "rows": len(clean_df),
        "output": output_file,
        "intent": intent
    }
