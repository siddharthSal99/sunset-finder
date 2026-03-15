from datetime import datetime, date, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import MAX_FORECAST_DAYS
from backend.services.sunset_service import get_sunset_prediction
from backend.services.terrain_service import find_best_sunset_spots
from backend.services.elevation_service import find_elevation_viewpoints
from backend.utils.astronomy import get_sunset_azimuth
from backend.models.sunset_models import SunsetResponse, BestSpotsResponse

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

app = FastAPI(title="Sunset Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api")
def health_check():
    return {"status": "ok"}


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
    if target < date.today() - timedelta(days=1):
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
    weather_spots = find_best_sunset_spots(lat, lon, target_date, radius_km)
    elevation_spots = find_elevation_viewpoints(lat, lon, radius_km)
    return BestSpotsResponse(
        sunset_azimuth=round(azimuth, 1),
        spots=weather_spots + elevation_spots,
    )


# --- Serve the Vite-built frontend (only when the build exists, i.e. on Vercel) ---

if FRONTEND_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="static_assets")

    @app.get("/{path:path}")
    def serve_frontend(path: str):
        file = FRONTEND_DIR / path
        if path and file.is_file():
            return FileResponse(file)
        return FileResponse(FRONTEND_DIR / "index.html")
