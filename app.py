import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# app.py

# app.py

# app.py

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
        explanation = validation["explanation"]

        record_event(
            "BLOCKED",
            f"{explanation['rule']} - {explanation['message']}"
        )

        return {
            "status": "BLOCKED",
            "explanation": explanation,
            "diagnosis": validation.get("diagnosis"),
            "detected_columns": list(df.columns)   # ⭐ KEY ADDITION
        }

    clean_df = clean_data(df, intent)
    output_file = deliver_output(clean_df, output_path)

    record_event("SUCCESS", f"Output written to {output_file}")

    return {
        "status": "SUCCESS",
        "rows": len(clean_df),
        "output": output_file
    }

