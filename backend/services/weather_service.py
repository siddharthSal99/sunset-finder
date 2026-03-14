import requests
from backend.config import OPEN_METEO_URL


def get_weather_forecast(lat: float, lon: float) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join([
            "cloudcover_low",
            "cloudcover_mid",
            "cloudcover_high",
            "relativehumidity_2m",
        ]),
        "timezone": "auto",
        "forecast_days": 1,
    }
    resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    hourly = data.get("hourly", {})
    return {
        "time": hourly.get("time", []),
        "cloudcover_low": hourly.get("cloudcover_low", []),
        "cloudcover_mid": hourly.get("cloudcover_mid", []),
        "cloudcover_high": hourly.get("cloudcover_high", []),
        "humidity": hourly.get("relativehumidity_2m", []),
        "timezone": data.get("timezone", "UTC"),
    }
