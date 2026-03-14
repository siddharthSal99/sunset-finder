from backend.utils.scoring import (
    rate_low_cloud,
    rate_mid_cloud,
    rate_high_cloud,
    rate_humidity,
    rate_conditions,
    conditions_quality_score,
)


def test_rate_low_cloud():
    assert rate_low_cloud(5) == "Ideal"
    assert rate_low_cloud(15) == "Excellent"
    assert rate_low_cloud(35) == "Good"
    assert rate_low_cloud(60) == "Fair"
    assert rate_low_cloud(85) == "Poor"


def test_rate_mid_cloud():
    assert rate_mid_cloud(80) == "Ideal"
    assert rate_mid_cloud(55) == "Excellent"
    assert rate_mid_cloud(35) == "Good"
    assert rate_mid_cloud(15) == "Fair"
    assert rate_mid_cloud(5) == "Poor"


def test_rate_high_cloud():
    assert rate_high_cloud(70) == "Ideal"
    assert rate_high_cloud(50) == "Excellent"
    assert rate_high_cloud(30) == "Good"
    assert rate_high_cloud(12) == "Fair"
    assert rate_high_cloud(5) == "Poor"


def test_rate_humidity():
    assert rate_humidity(45) == "Ideal"
    assert rate_humidity(30) == "Excellent"
    assert rate_humidity(60) == "Excellent"
    assert rate_humidity(20) == "Good"
    assert rate_humidity(5) == "Fair"
    assert rate_humidity(95) == "Poor"


def test_rate_conditions_returns_four_items():
    result = rate_conditions(10, 70, 50, 45)
    assert len(result) == 4
    for c in result:
        assert "field" in c
        assert "value" in c
        assert "rating" in c


def test_perfect_conditions_all_ideal():
    result = rate_conditions(5, 80, 65, 45)
    for c in result:
        assert c["rating"] == "Ideal"


def test_terrible_conditions_all_poor():
    result = rate_conditions(90, 5, 3, 95)
    for c in result:
        assert c["rating"] == "Poor"


def test_quality_score_higher_for_better_conditions():
    good = rate_conditions(5, 80, 65, 45)
    bad = rate_conditions(90, 5, 3, 95)
    assert conditions_quality_score(good) > conditions_quality_score(bad)


def test_deterministic():
    a = rate_conditions(20, 55, 40, 50)
    b = rate_conditions(20, 55, 40, 50)
    assert a == b
