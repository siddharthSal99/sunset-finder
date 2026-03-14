# Sunset App – Cursor Implementation Plan

This document is designed for **AI-assisted development using Cursor**.
Follow the steps sequentially to implement a terrain-aware sunset prediction service.

The system will:

1. Predict sunset quality for a location
2. Efficiently Compute terrain horizon along sunset azimuth
3. Adjust sunset timing based on terrain
4. Find nearby locations with clearer sunset views

---

# Tech Stack

Backend:

* Python 3.11
* FastAPI
* numpy
* requests
* astral

Optional later:

* rasterio (terrain data)
* shapely (geo operations)

---

# Repository Structure

Create the following project layout:

```
sunset-app/
│
├─ backend/
│  ├─ main.py
│  ├─ config.py
│  │
│  ├─ services/
│  │   ├─ sunset_service.py
│  │   ├─ weather_service.py
│  │   ├─ terrain_service.py
│  │
│  ├─ models/
│  │   ├─ sunset_models.py
│  │
│  ├─ utils/
│  │   ├─ astronomy.py
│  │   ├─ scoring.py
│
├─ data/
│
├─ tests/
│
└─ requirements.txt
```

---

# requirements.txt

```
fastapi
uvicorn
requests
numpy
astral
pydantic
```

---

# Implementation Steps

Cursor should follow these steps sequentially.

---

# Step 1 — Create FastAPI Server

File:

```
backend/main.py
```

Responsibilities:

* initialize FastAPI
* register endpoints
* call services

Required endpoints:

```
GET /sunset
GET /best-sunset-spots
```

Example endpoint signature:

```python
@app.get("/sunset")
def get_sunset(lat: float, lon: float, date: str | None = None):
    ...
```

---

# Step 2 — Astronomy Utilities

File:

```
backend/utils/astronomy.py
```

Responsibilities:

* compute sunset time
* compute sunset azimuth

Required functions:

```python
def get_sunset_time(lat: float, lon: float, date: datetime.date) -> datetime.datetime:
    pass


def get_sunset_azimuth(lat: float, lon: float, date: datetime.date) -> float:
    pass
```

Use the Astral library.

---

# Step 3 — Weather Service

File:

```
backend/services/weather_service.py
```

Purpose:

Fetch forecast data from Open-Meteo.

API endpoint:

```
https://api.open-meteo.com/v1/forecast
```

Required weather variables:

* cloudcover_low
* cloudcover_mid
* cloudcover_high
* relativehumidity_2m

Function signature:

```python
def get_weather_forecast(lat: float, lon: float) -> dict:
    pass
```

The function should return hourly weather data.

---

# Step 4 — Terrain Service

File:

```
backend/services/terrain_service.py
```

Responsibilities:

* sample terrain elevations
* compute horizon angle

For MVP, implement a **mock elevation provider**.

Later it will use SRTM or terrain tiles.

Required functions:

```python
def get_elevation(lat: float, lon: float) -> float:
    pass


def sample_terrain_profile(
    lat: float,
    lon: float,
    azimuth: float
) -> list:
    pass


def compute_horizon_angle(
    lat: float,
    lon: float,
    azimuth: float
) -> float:
    pass
```

---

# Terrain Sampling Algorithm

Terrain samples should be taken along the sunset azimuth.

Distances:

```
0.5 km
1 km
2 km
5 km
10 km
20 km
```

For each sample:

1. Compute geographic coordinate
2. Retrieve elevation
3. Calculate horizon angle

Formula:

```
angle = arctan((elevation_point - elevation_user) / distance)
```

Return the **maximum angle**.

---

# Step 5 — Sunset Scoring

File:

```
backend/utils/scoring.py
```

Purpose:

Compute sunset quality score.

Function signature:

```python
def compute_sunset_score(
    low_cloud: float,
    mid_cloud: float,
    high_cloud: float,
    humidity: float,
    horizon_angle: float
) -> float:
    pass
```

Scoring formula:

```
score =
  0.35 * mid +
  0.30 * high +
  0.20 * (1 - low) +
  0.15 * humidity
```

Terrain penalty:

```
score -= horizon_angle / 10
```

Clamp result between 0 and 1.

Final rating:

```
rating = score * 10
```

---

# Step 6 — Sunset Service

File:

```
backend/services/sunset_service.py
```

This service orchestrates the entire pipeline.

Required function:

```python
def get_sunset_prediction(
    lat: float,
    lon: float,
    date: datetime.date
) -> dict:
```

Steps inside:

1. compute sunset time
2. compute sunset azimuth
3. fetch weather forecast
4. sample weather near sunset
5. compute terrain horizon
6. compute sunset score
7. return structured response

---

# Step 7 — Best Sunset Spot Finder

Function location:

```
terrain_service.py
```

Signature:

```python
def find_best_sunset_spots(
    lat: float,
    lon: float,
    radius_km: float = 20
) -> list:
```

Algorithm:

1. Generate grid points within radius
2. For each point:

   * compute horizon angle
   * compute elevation
   * compute score
3. Sort by score
4. Return top results

Location scoring:

```
location_score =
  (5 - horizon_angle)
  + elevation / 1000
  - distance_km * 0.1
```

---

# Step 8 — API Response Models

File:

```
backend/models/sunset_models.py
```

Define Pydantic models.

Example:

```python
class SunsetResponse(BaseModel):
    sunset_time: str
    adjusted_sunset: str
    sunset_score: float
    rating: str
    terrain_horizon_angle: float
```

Example spot model:

```python
class SunsetSpot(BaseModel):
    lat: float
    lon: float
    horizon_angle: float
    distance_km: float
    score: float
```

---

# Step 9 — Best Sunset Spot Endpoint

Endpoint:

```
GET /best-sunset-spots
```

Example:

```
/best-sunset-spots?lat=37.77&lon=-122.42
```

Response:

```
{
  "sunset_azimuth": 296,
  "spots": [...]
}
```

---

# Step 10 — Testing

Create tests for:

* sunset azimuth calculation
* terrain horizon calculation
* scoring algorithm

Example test file:

```
tests/test_scoring.py
```

---

# Development Commands

Start API server:

```
uvicorn backend.main:app --reload
```

Example request:

```
http://localhost:8000/sunset?lat=37.77&lon=-122.42
```

---

# Cursor Prompt Workflow

Use these prompts inside Cursor sequentially.

Prompt 1:

```
Create the project structure defined in CURSOR_IMPLEMENTATION_PLAN.md.
```

Prompt 2:

```
Implement astronomy utilities using Astral.
```

Prompt 3:

```
Implement the weather service using Open-Meteo.
```

Prompt 4:

```
Implement terrain sampling and horizon angle computation.
```

Prompt 5:

```
Implement the sunset scoring algorithm.
```

Prompt 6:

```
Create FastAPI endpoints and wire services together.
```

Prompt 7:

```
Implement the best sunset spots search algorithm.
```

---

# Future Enhancements

Potential upgrades:

* SRTM terrain tiles
* satellite cloud imagery
* marine layer detection
* machine learning sunset prediction
* interactive map UI
* push sunset alerts

---

# Final Goal

The finished system should answer two questions:

1. **Will tonight’s sunset be good?**
2. **Where nearby is the best place to watch it?**
