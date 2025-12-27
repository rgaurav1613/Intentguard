import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# app.py

# app.py

# app.py

# app.py

from core.intake import load_input
from core.intent import parse_intent
from core.validator import validate_data
from core.cleaner import clean_data
from core.router import deliver_output
from core.memory import record_event
from core.state import (
    init_state_store,
    create_state,
    load_state,
    mark_resumed
)

# Initialize execution state storage
init_state_store()


def run_intentguard(
    file,
    intent_input,
    output_path,
    execution_id=None
):
    """
    Main execution engine.
    Supports fresh execution and resume flow.
    """

    # Load input
    df = load_input(file)

    # Parse intent
    intent = parse_intent(intent_input)

    # -------------------------
    # RESUME FLOW
    # -------------------------
    if execution_id:
        state = load_state(execution_id)

        if not state:
            return {
                "status": "ERROR",
                "reason": "Invalid execution_id"
            }

        validation = validate_data(df, state["intent"])

        if not validation["ok"]:
            return {
                "status": "BLOCKED",
                "reason": validation["reason"],
                "execution_id": execution_id
            }

        mark_resumed(execution_id)

    # -------------------------
    # NORMAL VALIDATION FLOW
    # -------------------------
    validation = validate_data(df, intent)

    if not validation["ok"]:
        execution_id = create_state(
            schema_snapshot=validation["schema_snapshot"],
            intent=intent,
            reason=validation["reason"]
        )

        record_event("BLOCKED", validation["reason"])

        return {
            "status": "BLOCKED",
            "reason": validation["reason"],
            "schema_snapshot": validation["schema_snapshot"],
            "execution_id": execution_id
        }

    # -------------------------
    # CLEAN & DELIVER
    # -------------------------
    clean_df = clean_data(df, intent)

    output_file = deliver_output(clean_df, output_path)

    record_event(
        "SUCCESS",
        f"Output written to {output_file}"
    )

    return {
        "status": "SUCCESS",
        "rows": len(clean_df),
        "output": output_file
    }
