LABELS = ("Poor", "Fair", "Good", "Excellent", "Ideal")
LABEL_RANK = {label: i for i, label in enumerate(LABELS)}


def rate_low_cloud(pct: float) -> str:
    """Lower is better -- low clouds block the sun at the horizon."""
    if pct <= 10:
        return "Ideal"
    if pct <= 25:
        return "Excellent"
    if pct <= 45:
        return "Good"
    if pct <= 70:
        return "Fair"
    return "Poor"


def rate_mid_cloud(pct: float) -> str:
    """Higher is better -- mid-altitude clouds catch vivid colours."""
    if pct >= 70:
        return "Ideal"
    if pct >= 50:
        return "Excellent"
    if pct >= 30:
        return "Good"
    if pct >= 15:
        return "Fair"
    return "Poor"


def rate_high_cloud(pct: float) -> str:
    """Higher is better -- high cirrus creates dramatic colour streaks."""
    if pct >= 60:
        return "Ideal"
    if pct >= 40:
        return "Excellent"
    if pct >= 25:
        return "Good"
    if pct >= 10:
        return "Fair"
    return "Poor"


def rate_humidity(pct: float) -> str:
    """Moderate (~35-55 %) is best -- enhances scattering without haze."""
    deviation = abs(pct - 45)
    if deviation <= 10:
        return "Ideal"
    if deviation <= 20:
        return "Excellent"
    if deviation <= 30:
        return "Good"
    if deviation <= 40:
        return "Fair"
    return "Poor"


def rate_conditions(
    low_cloud_pct: float,
    mid_cloud_pct: float,
    high_cloud_pct: float,
    humidity_pct: float,
) -> list[dict]:
    """Rate each sunset condition independently.

    All values are expected as percentages (0-100).
    """
    return [
        {"field": "Low Clouds", "value": round(low_cloud_pct, 1), "rating": rate_low_cloud(low_cloud_pct)},
        {"field": "Mid Clouds", "value": round(mid_cloud_pct, 1), "rating": rate_mid_cloud(mid_cloud_pct)},
        {"field": "High Clouds", "value": round(high_cloud_pct, 1), "rating": rate_high_cloud(high_cloud_pct)},
        {"field": "Humidity", "value": round(humidity_pct, 1), "rating": rate_humidity(humidity_pct)},
    ]


def conditions_quality_score(conditions: list[dict]) -> int:
    """Numeric quality for ranking spots internally (not shown to users)."""
    return sum(LABEL_RANK.get(c["rating"], 0) for c in conditions)
