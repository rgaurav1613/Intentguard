import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# app.py

from datetime import datetime

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
# Initialize execution state storage
# -------------------------------------------------
init_state_store()


# -------------------------------------------------
# SCHEMA v1.0 RESPONSE BUILDER
# -------------------------------------------------
def build_response(
    *,
    status,
    decision,
    execution_id=None,
    violations=None,
    schema_snapshot=None,
    output=None
):
    return {
        "contract_version": "1.0",
        "tool": "INTENTGUARD",
        "decision_time": datetime.utcnow().isoformat() + "Z",
        "status": status,
        "execution_id": execution_id,
        "decision": decision,
        "violations": violations or [],
        "schema_snapshot": schema_snapshot,
        "output": output
    }


# -------------------------------------------------
# MAIN EXECUTION ENGINE
# -------------------------------------------------
def run_intentguard(
    file,
    intent_input,
    output_path,
    execution_id=None
):
    """
    INTENTGUARD core engine

    Capabilities:
    - SCHEMA v1.0 compliant output
    - MULTI-rule validation
    - Stateful resume
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
    # RESUME FLOW
    # =================================================
    if execution_id:
        state = load_state(execution_id)

        if not state:
            return build_response(
                status="ERROR",
                execution_id=execution_id,
                decision={
                    "severity": "CRITICAL",
                    "action": "BLOCK",
                    "summary": "Invalid execution_id"
                }
            )

        validation = validate_data(df, state["intent"])

        if not validation["ok"]:
            return build_response(
                status="BLOCKED",
                execution_id=execution_id,
                decision={
                    "severity": validation["highest_severity"],
                    "action": "BLOCK",
                    "summary": f"{len(validation['violations'])} validation issues detected"
                },
                violations=validation["violations"],
                schema_snapshot=validation["schema_snapshot"]
            )

        mark_resumed(execution_id)

    # =================================================
    # NORMAL VALIDATION FLOW (MULTI-RULE)
    # =================================================
    validation = validate_data(df, intent)

    if not validation["ok"]:
        execution_id = create_state(
            schema_snapshot=validation["schema_snapshot"],
            intent=intent,
            reason="Multiple validation violations detected"
        )

        record_event(
            "BLOCKED",
            f"{len(validation['violations'])} validation issues detected"
        )

        return build_response(
            status="BLOCKED",
            execution_id=execution_id,
            decision={
                "severity": validation["highest_severity"],
                "action": "BLOCK",
                "summary": f"{len(validation['violations'])} validation issues detected"
            },
            violations=validation["violations"],
            schema_snapshot=validation["schema_snapshot"]
        )

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

    return build_response(
        status="SUCCESS",
        decision={
            "severity": "LOW",
            "action": "ALLOW",
            "summary": "Execution completed successfully"
        },
        output={
            "rows_processed": len(clean_df),
            "output_path": output_file
        }
    )
