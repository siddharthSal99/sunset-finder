from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from backend.services.sunset_service import get_sunset_prediction
from backend.services.terrain_service import find_best_sunset_spots
from backend.utils.astronomy import get_sunset_azimuth
from backend.models.sunset_models import SunsetResponse, BestSpotsResponse

app = FastAPI(title="Sunset Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/sunset", response_model=SunsetResponse)
def get_sunset(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    date: str | None = Query(None, description="ISO date string (YYYY-MM-DD)"),
):
    target_date = (
        datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.now().date()
    )
    return get_sunset_prediction(lat, lon, target_date)


@app.get("/api/best-sunset-spots", response_model=BestSpotsResponse)
def get_best_spots(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(20, gt=0, le=100),
):
    today = datetime.now().date()
    azimuth = get_sunset_azimuth(lat, lon, today)
    spots = find_best_sunset_spots(lat, lon, radius_km)
    return BestSpotsResponse(sunset_azimuth=round(azimuth, 1), spots=spots)
