def compute_sunset_score(
    low_cloud: float,
    mid_cloud: float,
    high_cloud: float,
    humidity: float,
    horizon_angle: float,
) -> dict:
    """Return sunset score (0-10) and rating label.

    Cloud / humidity values are expected as fractions in [0, 1].
    """
    score = (
        0.35 * mid_cloud
        + 0.30 * high_cloud
        + 0.20 * (1 - low_cloud)
        + 0.15 * humidity
    )

    score -= horizon_angle / 10
    score = max(0.0, min(1.0, score))

    rating = score * 10

    if rating >= 8:
        label = "Spectacular"
    elif rating >= 6:
        label = "Great"
    elif rating >= 4:
        label = "Good"
    elif rating >= 2:
        label = "Fair"
    else:
        label = "Poor"

    return {
        "score": round(rating, 2),
        "label": label,
    }
