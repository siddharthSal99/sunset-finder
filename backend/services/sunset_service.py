import datetime

from backend.utils.astronomy import get_sunset_time, get_sunset_azimuth
from backend.services.weather_service import (
    get_weather_forecast,
    WeatherUnavailableError,
)
from backend.services.terrain_service import compute_horizon_angle
from backend.utils.scoring import compute_sunset_score


def _find_nearest_hour_index(times: list[str], target: datetime.datetime) -> int:
    target_str = target.strftime("%Y-%m-%dT%H:00")
    for i, t in enumerate(times):
        if t >= target_str:
            return i
    return len(times) - 1


def _extract_weather_at_sunset(weather: dict, sunset_dt: datetime.datetime) -> dict:
    """Pick the hourly weather values closest to sunset, returned as 0-1 fractions."""
    idx = _find_nearest_hour_index(weather["time"], sunset_dt)
    return {
        "low": weather["cloud_cover_low"][idx] / 100 if weather["cloud_cover_low"] else 0.3,
        "mid": weather["cloud_cover_mid"][idx] / 100 if weather["cloud_cover_mid"] else 0.3,
        "high": weather["cloud_cover_high"][idx] / 100 if weather["cloud_cover_high"] else 0.3,
        "humidity": weather["humidity"][idx] / 100 if weather["humidity"] else 0.5,
    }


def compute_weather_base_score(w: dict) -> float:
    """Weather-only component of the sunset score (0-1, before terrain penalty).

    Uses the same weights as ``compute_sunset_score`` but without the
    horizon-angle deduction so it can be reused for the best-spots endpoint.
    """
    return (
        0.35 * w["mid"]
        + 0.30 * w["high"]
        + 0.20 * (1 - w["low"])
        + 0.15 * w["humidity"]
    )


def get_weather_context(lat: float, lon: float, date: datetime.date) -> dict | None:
    """Fetch weather and compute the base score for a location and date.

    Returns None when weather is unavailable (date too far out).
    """
    try:
        weather = get_weather_forecast(lat, lon, date)
    except WeatherUnavailableError:
        return None

    tz = weather.get("timezone", "UTC")
    sunset_dt = get_sunset_time(lat, lon, date, timezone=tz)
    w = _extract_weather_at_sunset(weather, sunset_dt)
    return {
        "weather": w,
        "base_score": compute_weather_base_score(w),
        "timezone": tz,
    }


def get_sunset_prediction(
    lat: float, lon: float, date: datetime.date
) -> dict:
    ctx = get_weather_context(lat, lon, date)
    weather_available = ctx is not None

    tz = ctx["timezone"] if ctx else "UTC"

    sunset_dt = get_sunset_time(lat, lon, date, timezone=tz)
    azimuth = get_sunset_azimuth(lat, lon, date, timezone=tz)
    horizon = compute_horizon_angle(lat, lon, azimuth)

    adjusted_sunset = sunset_dt - datetime.timedelta(
        minutes=max(0, horizon * 2)
    )

    if weather_available:
        w = ctx["weather"]
        result = compute_sunset_score(w["low"], w["mid"], w["high"], w["humidity"], horizon)

        return {
            "sunset_time": sunset_dt.strftime("%H:%M:%S"),
            "adjusted_sunset": adjusted_sunset.strftime("%H:%M:%S"),
            "sunset_score": result["score"],
            "rating": result["label"],
            "terrain_horizon_angle": round(horizon, 2),
            "cloud_cover_low": round(w["low"] * 100, 1),
            "cloud_cover_mid": round(w["mid"] * 100, 1),
            "cloud_cover_high": round(w["high"] * 100, 1),
            "humidity": round(w["humidity"] * 100, 1),
            "weather_available": True,
        }

    return {
        "sunset_time": sunset_dt.strftime("%H:%M:%S"),
        "adjusted_sunset": adjusted_sunset.strftime("%H:%M:%S"),
        "sunset_score": None,
        "rating": "Unknown (no weather data)",
        "terrain_horizon_angle": round(horizon, 2),
        "cloud_cover_low": None,
        "cloud_cover_mid": None,
        "cloud_cover_high": None,
        "humidity": None,
        "weather_available": False,
        "message": "Weather forecasts are not available for this date.",
    }
