from datetime import datetime, date

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.config import MAX_FORECAST_DAYS
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


def _parse_date(raw: str | None) -> date:
    """Parse a YYYY-MM-DD string, default to today, reject past dates."""
    if raw is None:
        return date.today()
    try:
        target = datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD.",
        )
    if target < date.today():
        raise HTTPException(
            status_code=400,
            detail="Date must not be in the past.",
        )
    return target


@app.get("/api/sunset", response_model=SunsetResponse)
def get_sunset(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    date: str | None = Query(
        None,
        description=f"ISO date (YYYY-MM-DD), today through +{MAX_FORECAST_DAYS} days for weather data",
    ),
):
    target_date = _parse_date(date)
    return get_sunset_prediction(lat, lon, target_date)


@app.get("/api/best-sunset-spots", response_model=BestSpotsResponse)
def get_best_spots(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(20, gt=0, le=100),
    date: str | None = Query(
        None,
        description="ISO date (YYYY-MM-DD), defaults to today",
    ),
):
    target_date = _parse_date(date)
    azimuth = get_sunset_azimuth(lat, lon, target_date)
    spots = find_best_sunset_spots(lat, lon, target_date, radius_km)
    return BestSpotsResponse(sunset_azimuth=round(azimuth, 1), spots=spots)
