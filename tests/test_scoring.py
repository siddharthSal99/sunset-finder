from backend.utils.scoring import compute_sunset_score


def test_perfect_conditions():
    result = compute_sunset_score(
        low_cloud=0.0, mid_cloud=1.0, high_cloud=1.0,
        humidity=1.0, horizon_angle=0.0,
    )
    assert result["score"] == 10.0
    assert result["label"] == "Spectacular"


def test_terrible_conditions():
    result = compute_sunset_score(
        low_cloud=1.0, mid_cloud=0.0, high_cloud=0.0,
        humidity=0.0, horizon_angle=5.0,
    )
    assert result["score"] == 0.0
    assert result["label"] == "Poor"


def test_score_clamped_between_0_and_10():
    result = compute_sunset_score(
        low_cloud=1.0, mid_cloud=0.0, high_cloud=0.0,
        humidity=0.0, horizon_angle=20.0,
    )
    assert result["score"] >= 0.0
    assert result["score"] <= 10.0


def test_terrain_penalty_reduces_score():
    flat = compute_sunset_score(0.2, 0.5, 0.5, 0.5, horizon_angle=0.0)
    hilly = compute_sunset_score(0.2, 0.5, 0.5, 0.5, horizon_angle=3.0)
    assert flat["score"] > hilly["score"]


def test_rating_labels():
    thresholds = [
        (0.9, "Spectacular"),
        (0.7, "Great"),
        (0.5, "Good"),
        (0.3, "Fair"),
        (0.0, "Poor"),
    ]
    for mid_cloud, expected_min_label in thresholds:
        result = compute_sunset_score(0.0, mid_cloud, 0.0, 0.0, 0.0)
        assert result["label"] in ("Spectacular", "Great", "Good", "Fair", "Poor")
