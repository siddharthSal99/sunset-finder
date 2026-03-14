import math
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.config import BEST_SPOTS_TOP_N, BEST_SPOTS_MAX_CELLS
from backend.services.weather_service import get_weather_forecast, WeatherUnavailableError
from backend.utils.astronomy import get_sunset_time
from backend.utils.scoring import rate_conditions, conditions_quality_score


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _generate_grid_cells(lat: float, lon: float, radius_km: float) -> list[tuple[float, float]]:
    """Distinct 0.1-degree grid cells within *radius_km*, excluding the user's own cell."""
    user_cell = (round(lat, 1), round(lon, 1))
    step = 0.1
    half_range = radius_km / 111.0

    cells: set[tuple[float, float]] = set()
    current_lat = round(lat - half_range, 1)
    lat_end = round(lat + half_range, 1)

    while current_lat <= lat_end:
        lon_range = half_range / max(math.cos(math.radians(lat)), 0.01)
        current_lon = round(lon - lon_range, 1)
        lon_end = round(lon + lon_range, 1)

        while current_lon <= lon_end:
            cell = (round(current_lat, 1), round(current_lon, 1))
            if cell != user_cell:
                dist = _haversine_km(lat, lon, cell[0], cell[1])
                if dist <= radius_km:
                    cells.add(cell)
            current_lon = round(current_lon + step, 1)
        current_lat = round(current_lat + step, 1)

    ranked = sorted(cells, key=lambda c: _haversine_km(lat, lon, c[0], c[1]))
    return ranked[:BEST_SPOTS_MAX_CELLS]


def _find_nearest_hour_index(times: list[str], target) -> int:
    target_str = target.strftime("%Y-%m-%dT%H:00")
    for i, t in enumerate(times):
        if t >= target_str:
            return i
    return len(times) - 1


def find_best_sunset_spots(lat, lon, date, radius_km=20) -> list[dict]:
    """Sample nearby weather grid cells and rank by condition quality."""
    cells = _generate_grid_cells(lat, lon, radius_km)

    def _fetch(cell):
        cell_lat, cell_lon = cell
        try:
            weather = get_weather_forecast(cell_lat, cell_lon, date)
        except (WeatherUnavailableError, Exception):
            return None

        tz = weather.get("timezone", "UTC")
        sunset_dt = get_sunset_time(cell_lat, cell_lon, date, timezone=tz)
        idx = _find_nearest_hour_index(weather["time"], sunset_dt)

        low = weather["cloud_cover_low"][idx] if weather["cloud_cover_low"] else 30
        mid = weather["cloud_cover_mid"][idx] if weather["cloud_cover_mid"] else 30
        high = weather["cloud_cover_high"][idx] if weather["cloud_cover_high"] else 30
        humidity = weather["humidity"][idx] if weather["humidity"] else 50

        conditions = rate_conditions(low, mid, high, humidity)
        quality = conditions_quality_score(conditions)
        dist = _haversine_km(lat, lon, cell_lat, cell_lon)

        return {
            "lat": round(cell_lat, 5),
            "lon": round(cell_lon, 5),
            "distance_km": round(dist, 1),
            "conditions": conditions,
            "_quality": quality,
        }

    spots: list[dict] = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_fetch, c): c for c in cells}
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                spots.append(result)

    spots.sort(key=lambda s: (-s["_quality"], s["distance_km"]))

    return [
        {**{k: v for k, v in s.items() if k != "_quality"}, "spot_type": "weather"}
        for s in spots[:BEST_SPOTS_TOP_N]
    ]
