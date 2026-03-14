import datetime
from zoneinfo import ZoneInfo

from astral import LocationInfo
from astral.sun import sun, azimuth


def get_sunset_time(
    lat: float, lon: float, date: datetime.date, timezone: str = "UTC"
) -> datetime.datetime:
    location = LocationInfo(latitude=lat, longitude=lon, timezone=timezone)
    s = sun(location.observer, date=date, tzinfo=ZoneInfo(timezone))
    return s["sunset"]


def get_sunset_azimuth(
    lat: float, lon: float, date: datetime.date, timezone: str = "UTC"
) -> float:
    location = LocationInfo(latitude=lat, longitude=lon, timezone=timezone)
    sunset_dt = get_sunset_time(lat, lon, date, timezone)
    return azimuth(location.observer, sunset_dt)
