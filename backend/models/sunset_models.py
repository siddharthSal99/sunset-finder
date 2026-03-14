from pydantic import BaseModel


class SunsetResponse(BaseModel):
    sunset_time: str
    adjusted_sunset: str
    sunset_score: float
    rating: str
    terrain_horizon_angle: float
    cloud_cover_low: float
    cloud_cover_mid: float
    cloud_cover_high: float
    humidity: float


class SunsetSpot(BaseModel):
    lat: float
    lon: float
    horizon_angle: float
    elevation: float
    distance_km: float
    score: float


class BestSpotsResponse(BaseModel):
    sunset_azimuth: float
    spots: list[SunsetSpot]
