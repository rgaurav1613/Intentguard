def parse_intent(blocked_dates, critical):
    dates = [d.strip() for d in blocked_dates.split(",") if d.strip()]
    return {
        "blocked_dates": dates,
        "critical": critical
    }
