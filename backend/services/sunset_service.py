import datetime

from backend.utils.astronomy import get_sunset_time, get_sunset_azimuth
from backend.services.weather_service import get_weather_forecast
from backend.services.terrain_service import compute_horizon_angle
from backend.utils.scoring import compute_sunset_score


def _find_nearest_hour_index(times: list[str], target: datetime.datetime) -> int:
    target_str = target.strftime("%Y-%m-%dT%H:00")
    for i, t in enumerate(times):
        if t >= target_str:
            return i
    return len(times) - 1


def get_sunset_prediction(
    lat: float, lon: float, date: datetime.date
) -> dict:
    weather = get_weather_forecast(lat, lon)
    tz = weather.get("timezone", "UTC")

    sunset_dt = get_sunset_time(lat, lon, date, timezone=tz)
    azimuth = get_sunset_azimuth(lat, lon, date, timezone=tz)

    idx = _find_nearest_hour_index(weather["time"], sunset_dt)

    low = weather["cloudcover_low"][idx] / 100 if weather["cloudcover_low"] else 0.3
    mid = weather["cloudcover_mid"][idx] / 100 if weather["cloudcover_mid"] else 0.3
    high = weather["cloudcover_high"][idx] / 100 if weather["cloudcover_high"] else 0.3
    hum = weather["humidity"][idx] / 100 if weather["humidity"] else 0.5

    horizon = compute_horizon_angle(lat, lon, azimuth)

    adjusted_sunset = sunset_dt - datetime.timedelta(
        minutes=max(0, horizon * 2)
    )

    result = compute_sunset_score(low, mid, high, hum, horizon)

    return {
        "sunset_time": sunset_dt.strftime("%H:%M:%S"),
        "adjusted_sunset": adjusted_sunset.strftime("%H:%M:%S"),
        "sunset_score": result["score"],
        "rating": result["label"],
        "terrain_horizon_angle": round(horizon, 2),
        "cloud_cover_low": round(low * 100, 1),
        "cloud_cover_mid": round(mid * 100, 1),
        "cloud_cover_high": round(high * 100, 1),
        "humidity": round(hum * 100, 1),
    }
