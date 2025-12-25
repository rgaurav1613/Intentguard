def calculate_risk(df, intent):
    if intent["critical"]:
        return "HIGH"

    if len(df) > 10000:
        return "MEDIUM"

    return "LOW"
