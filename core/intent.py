def parse_intent(user_intent: dict):
    """
    User-defined intent (authoritative).
    System does NOT guess business rules.
    """

    intent = {
        "identity": {
            "unique": user_intent.get("unique_columns", [])
        },
        "presence": {
            "required": user_intent.get("required_columns", [])
        },
        "quality": {
            "clean": user_intent.get("clean_required", True)
        },
        "risk": {
            "critical": user_intent.get("critical", False),
            "max_rows": user_intent.get("max_rows")
        }
    }

    return intent
