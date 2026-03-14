from pydantic import BaseModel


class ConditionDetail(BaseModel):
    field: str
    value: float
    rating: str


class SunsetResponse(BaseModel):
    sunset_time: str
    sunset_azimuth: float
    conditions: list[ConditionDetail] | None = None
    weather_available: bool = True
    message: str | None = None


class SunsetSpot(BaseModel):
    lat: float
    lon: float
    distance_km: float
    conditions: list[ConditionDetail]


class BestSpotsResponse(BaseModel):
    sunset_azimuth: float
    spots: list[SunsetSpot]
