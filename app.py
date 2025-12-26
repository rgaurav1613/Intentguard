import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# app.py

from core.intake import load_input
from core.intent import parse_intent
from core.validator import validate_data
from core.cleaner import clean_data
from core.router import deliver_output
from core.memory import record_event


def run_intentguard(file, intent_input, output_path):
    """
    Core execution engine for INTENTGUARD
    V2.2: Explainability + Diagnosis
    """

    # 1. Load input
    df = load_input(file)

    # 2. Parse intent (user-defined, authoritative)
    intent = parse_intent(intent_input)

    # 3. Validate against intent
    validation = validate_data(df, intent)

    if not validation["ok"]:
        explanation = validation["explanation"]
        diagnosis = validation.get("diagnosis")

        # Audit
        record_event(
            "BLOCKED",
            f"{explanation['rule']} - {explanation['message']}"
        )

        return {
            "status": "BLOCKED",
            "explanation": explanation,
            "diagnosis": diagnosis
        }

    # 4. Clean data (only if allowed)
    clean_df = clean_data(df, intent)

    # 5. Deliver output
    output_file = deliver_output(clean_df, output_path)

    # 6. Audit success
    record_event("SUCCESS", f"Output written to {output_file}")

    return {
        "status": "SUCCESS",
        "rows": len(clean_df),
        "output": output_file
    }
