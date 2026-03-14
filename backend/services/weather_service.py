import datetime

import requests

from backend.config import OPEN_METEO_URL, MAX_FORECAST_DAYS


class WeatherUnavailableError(Exception):
    """Raised when the requested date is beyond the forecast window."""


def get_weather_forecast(
    lat: float, lon: float, date: datetime.date
) -> dict:
    """Fetch hourly weather forecast for *date* and return the slice for that day.

    Raises ``WeatherUnavailableError`` when *date* is more than
    ``MAX_FORECAST_DAYS`` days in the future.
    """
    today = datetime.date.today()
    delta_days = (date - today).days

    if delta_days < 0:
        delta_days = 0
        date = today

    if delta_days >= MAX_FORECAST_DAYS:
        raise WeatherUnavailableError(
            f"Weather forecasts are only available up to {MAX_FORECAST_DAYS} days ahead. "
            f"Requested date is {delta_days} days from today."
        )

    forecast_days = max(delta_days + 1, 1)

    # Snap to 1-decimal-degree grid (~11 km) so nearby clicks always hit the
    # same Open-Meteo cell and return consistent weather values.
    query_lat = round(lat, 1)
    query_lon = round(lon, 1)

    params = {
        "latitude": query_lat,
        "longitude": query_lon,
        "hourly": ",".join([
            "cloud_cover_low",
            "cloud_cover_mid",
            "cloud_cover_high",
            "relative_humidity_2m",
        ]),
        "timezone": "auto",
        "forecast_days": forecast_days,
    }
    resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])

    date_prefix = date.isoformat()
    indices = [i for i, t in enumerate(times) if t.startswith(date_prefix)]

    if not indices:
        raise WeatherUnavailableError(
            f"No hourly data returned for {date_prefix}."
        )

    return {
        "time": [times[i] for i in indices],
        "cloud_cover_low": [hourly.get("cloud_cover_low", [])[i] for i in indices],
        "cloud_cover_mid": [hourly.get("cloud_cover_mid", [])[i] for i in indices],
        "cloud_cover_high": [hourly.get("cloud_cover_high", [])[i] for i in indices],
        "humidity": [hourly.get("relative_humidity_2m", [])[i] for i in indices],
        "timezone": data.get("timezone", "UTC"),
    }
