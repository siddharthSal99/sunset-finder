# Sunset Finder

A terrain-aware sunset prediction web app. Get sunset quality scores for any location and discover the best nearby spots to watch the sunset.

## Features

- **Sunset Quality Score** -- rates tonight's sunset on a 0-10 scale using cloud cover, humidity, and terrain data
- **Best Spot Finder** -- searches a grid of nearby locations to find the clearest sunset views
- **Interactive Map** -- click anywhere to get a prediction; best spots appear as markers
- **Weather Integration** -- pulls real-time cloud and humidity forecasts from Open-Meteo

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, Astral, NumPy
- **Frontend**: React, Vite, Tailwind CSS, React Leaflet
- **APIs**: Open-Meteo (weather), OpenStreetMap (map tiles)

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+

### Backend

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

The API server starts at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server starts at `http://localhost:5173` and proxies API requests to the backend.

### API Endpoints

| Endpoint | Description |
|---|---|
| `GET /sunset?lat=...&lon=...&date=...` | Sunset prediction for a location |
| `GET /best-sunset-spots?lat=...&lon=...&radius_km=...` | Top nearby sunset viewing spots |

### Example

```
http://localhost:8000/sunset?lat=37.77&lon=-122.42
```
