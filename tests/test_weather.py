import datetime
from unittest.mock import patch, MagicMock

import pytest

from backend.services.weather_service import (
    get_weather_forecast,
    WeatherUnavailableError,
)
from backend.config import MAX_FORECAST_DAYS


def _make_hourly_response(date: datetime.date, forecast_days: int = 1) -> dict:
    """Build a fake Open-Meteo JSON response for a given date range."""
    hours = []
    cloud_low, cloud_mid, cloud_high, humidity = [], [], [], []
    for day_offset in range(forecast_days):
        d = date + datetime.timedelta(days=day_offset)
        for h in range(24):
            hours.append(f"{d.isoformat()}T{h:02d}:00")
            cloud_low.append(30)
            cloud_mid.append(50)
            cloud_high.append(40)
            humidity.append(60)
    return {
        "hourly": {
            "time": hours,
            "cloud_cover_low": cloud_low,
            "cloud_cover_mid": cloud_mid,
            "cloud_cover_high": cloud_high,
            "relative_humidity_2m": humidity,
        },
        "timezone": "America/Los_Angeles",
    }


def test_too_far_in_future_raises():
    far_date = datetime.date.today() + datetime.timedelta(days=MAX_FORECAST_DAYS + 5)
    with pytest.raises(WeatherUnavailableError):
        get_weather_forecast(37.77, -122.42, far_date)


def test_exactly_at_limit_raises():
    boundary_date = datetime.date.today() + datetime.timedelta(days=MAX_FORECAST_DAYS)
    with pytest.raises(WeatherUnavailableError):
        get_weather_forecast(37.77, -122.42, boundary_date)


@patch("backend.services.weather_service.requests.get")
def test_today_forecast(mock_get: MagicMock):
    today = datetime.date.today()
    mock_resp = MagicMock()
    mock_resp.json.return_value = _make_hourly_response(today)
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    result = get_weather_forecast(37.77, -122.42, today)

    assert len(result["time"]) == 24
    assert all(t.startswith(today.isoformat()) for t in result["time"])
    assert "timezone" in result

    call_params = mock_get.call_args[1]["params"]
    assert call_params["forecast_days"] >= 1


@patch("backend.services.weather_service.requests.get")
def test_future_date_sets_correct_forecast_days(mock_get: MagicMock):
    today = datetime.date.today()
    target = today + datetime.timedelta(days=5)

    mock_resp = MagicMock()
    mock_resp.json.return_value = _make_hourly_response(today, forecast_days=6)
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    get_weather_forecast(37.77, -122.42, target)

    call_params = mock_get.call_args[1]["params"]
    assert call_params["forecast_days"] == 6


@patch("backend.services.weather_service.requests.get")
def test_filters_to_target_date_only(mock_get: MagicMock):
    today = datetime.date.today()
    target = today + datetime.timedelta(days=2)

    mock_resp = MagicMock()
    mock_resp.json.return_value = _make_hourly_response(today, forecast_days=3)
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    result = get_weather_forecast(37.77, -122.42, target)

    assert all(t.startswith(target.isoformat()) for t in result["time"])
    assert len(result["time"]) == 24
