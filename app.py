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
from core.state import (
    init_state_store,
    create_state,
    load_state,
    mark_resumed
)

# -------------------------------------------------
# Initialize persistent execution state store
# -------------------------------------------------
init_state_store()


def run_intentguard(
    file,
    intent_input,
    output_path,
    execution_id=None
):
    """
    Main INTENTGUARD execution engine.
    Supports:
    - Fresh execution
    - Resume after correction (stateful)
    """

    # -----------------------------
    # LOAD INPUT
    # -----------------------------
    df = load_input(file)

    # -----------------------------
    # PARSE INTENT
    # -----------------------------
    intent = parse_intent(intent_input)

    # =================================================
    # RESUME FLOW (if execution_id provided)
    # =================================================
    if execution_id:
        state = load_state(execution_id)

        if not state:
            return {
                "status": "ERROR",
                "message": "Invalid execution_id"
            }

        validation = validate_data(df, state["intent"])

        if not validation["ok"]:
            return {
                "status": "BLOCKED",
                "explanation": validation["explanation"],
                "diagnosis": validation["diagnosis"],
                "execution_id": execution_id
            }

        # Resume allowed
        mark_resumed(execution_id)

    # =================================================
    # NORMAL VALIDATION FLOW
    # =================================================
    validation = validate_data(df, intent)

    if not validation["ok"]:
        execution_id = create_state(
            schema_snapshot=validation["schema_snapshot"],
            intent=intent,
            reason=validation["explanation"]["message"]
        )

        record_event(
            "BLOCKED",
            validation["explanation"]["message"]
        )

        return {
            "status": "BLOCKED",
            "explanation": validation["explanation"],
            "diagnosis": validation["diagnosis"],
            "schema_snapshot": validation["schema_snapshot"],
            "execution_id": execution_id
        }

    # =================================================
    # CLEAN DATA (SAFE PATH)
    # =================================================
    clean_df = clean_data(df, intent)

    # =================================================
    # DELIVER OUTPUT
    # =================================================
    output_file = deliver_output(clean_df, output_path)

    record_event(
        "SUCCESS",
        f"Output written to {output_file}"
    )

    return {
        "status": "SUCCESS",
        "rows_processed": len(clean_df),
        "output_path": output_file
    }
