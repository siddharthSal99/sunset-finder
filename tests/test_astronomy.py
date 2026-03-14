import datetime

from backend.utils.astronomy import get_sunset_time, get_sunset_azimuth


def test_sunset_time_returns_datetime():
    dt = get_sunset_time(37.77, -122.42, datetime.date(2026, 6, 21))
    assert isinstance(dt, datetime.datetime)


def test_sunset_time_future_date():
    """Astral must work for dates far in the future."""
    dt = get_sunset_time(40.71, -74.01, datetime.date(2028, 12, 25))
    assert isinstance(dt, datetime.datetime)
    assert dt.hour >= 16  # NYC winter sunset is late afternoon


def test_sunset_azimuth_range():
    az = get_sunset_azimuth(37.77, -122.42, datetime.date(2026, 6, 21))
    assert 200 <= az <= 340, f"azimuth {az} out of expected range"


def test_summer_vs_winter_azimuth():
    """Summer sunset should be further north (higher azimuth) than winter."""
    summer_az = get_sunset_azimuth(37.77, -122.42, datetime.date(2026, 6, 21))
    winter_az = get_sunset_azimuth(37.77, -122.42, datetime.date(2026, 12, 21))
    assert summer_az > winter_az
