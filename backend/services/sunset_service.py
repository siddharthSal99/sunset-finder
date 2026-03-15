import datetime

from backend.utils.astronomy import get_sunset_time, get_sunset_azimuth
from backend.services.weather_service import (
    get_weather_forecast,
    WeatherUnavailableError,
)
from backend.utils.scoring import rate_conditions


def _find_nearest_hour_index(times: list[str], target: datetime.datetime) -> int:
    target_str = target.strftime("%Y-%m-%dT%H:00")
    for i, t in enumerate(times):
        if t >= target_str:
            return i
    return len(times) - 1


def _extract_weather_at_sunset(weather: dict, sunset_dt: datetime.datetime) -> dict:
    """Pick the hourly weather percentages closest to sunset."""
    idx = _find_nearest_hour_index(weather["time"], sunset_dt)
    return {
        "low": weather["cloud_cover_low"][idx] if weather["cloud_cover_low"] else 30,
        "mid": weather["cloud_cover_mid"][idx] if weather["cloud_cover_mid"] else 30,
        "high": weather["cloud_cover_high"][idx] if weather["cloud_cover_high"] else 30,
        "humidity": weather["humidity"][idx] if weather["humidity"] else 50,
    }


def get_sunset_prediction(
    lat: float, lon: float, date: datetime.date
) -> dict:
    try:
        weather = get_weather_forecast(lat, lon, date)
    except WeatherUnavailableError:
        weather = None

    tz = weather.get("timezone", "UTC") if weather else "UTC"
    effective_date = weather.get("effective_date", date) if weather else date
    sunset_dt = get_sunset_time(lat, lon, effective_date, timezone=tz)
    azimuth = get_sunset_azimuth(lat, lon, effective_date, timezone=tz)

    if weather is not None:
        w = _extract_weather_at_sunset(weather, sunset_dt)
        conditions = rate_conditions(w["low"], w["mid"], w["high"], w["humidity"])

        return {
            "sunset_time": sunset_dt.strftime("%H:%M:%S"),
            "sunset_azimuth": round(azimuth, 1),
            "conditions": conditions,
            "weather_available": True,
        }

    return {
        "sunset_time": sunset_dt.strftime("%H:%M:%S"),
        "sunset_azimuth": round(azimuth, 1),
        "conditions": None,
        "weather_available": False,
        "message": "Weather forecasts are not available for this date.",
    }
