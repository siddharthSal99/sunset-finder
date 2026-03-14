import math

import requests

from backend.config import (
    OPEN_METEO_ELEVATION_URL,
    ELEVATION_BATCH_SIZE,
    ELEVATION_NUM_SECTORS,
)

R_EARTH = 6371.0

_COMPASS_LABELS = ["N", "NE", "E", "SE", "S", "SW"]
_SECTOR_DEGREE = 360.0 / len(_COMPASS_LABELS)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R_EARTH * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _destination_point(lat: float, lon: float, bearing_deg: float, dist_km: float):
    """Return (lat, lon) of a point at *dist_km* along *bearing_deg* from origin."""
    lat_r = math.radians(lat)
    lon_r = math.radians(lon)
    brng = math.radians(bearing_deg)
    d = dist_km / R_EARTH

    new_lat = math.asin(
        math.sin(lat_r) * math.cos(d)
        + math.cos(lat_r) * math.sin(d) * math.cos(brng)
    )
    new_lon = lon_r + math.atan2(
        math.sin(brng) * math.sin(d) * math.cos(lat_r),
        math.cos(d) - math.sin(lat_r) * math.sin(new_lat),
    )
    return (math.degrees(new_lat), math.degrees(new_lon))


def _bearing_to_label(bearing: float) -> str:
    idx = int((bearing + _SECTOR_DEGREE / 2) % 360 // _SECTOR_DEGREE)
    return _COMPASS_LABELS[idx % len(_COMPASS_LABELS)]


def _generate_sector_points(
    lat: float, lon: float, radius_km: float, num_sectors: int = 6
) -> list[list[tuple[float, float, int]]]:
    """Generate sample points grouped by sector.

    Returns a list of *num_sectors* lists.  Each inner list contains
    ``(lat, lon, sector_index)`` tuples for that sector.
    """
    sector_width = 360.0 / num_sectors
    radial_steps = 7
    angular_steps_per_sector = 5

    min_radius = max(1.0, radius_km * 0.1)
    radii = [
        min_radius + (radius_km - min_radius) * i / (radial_steps - 1)
        for i in range(radial_steps)
    ]

    sectors: list[list[tuple[float, float, int]]] = [[] for _ in range(num_sectors)]

    for s in range(num_sectors):
        start_angle = s * sector_width
        for a in range(angular_steps_per_sector):
            bearing = start_angle + sector_width * (a + 0.5) / angular_steps_per_sector
            for r in radii:
                pt_lat, pt_lon = _destination_point(lat, lon, bearing, r)
                sectors[s].append((round(pt_lat, 5), round(pt_lon, 5), s))

    return sectors


def _batch_fetch_elevations(points: list[tuple[float, float]]) -> list[float]:
    """Query Open-Meteo Elevation API in batches, returning metres for each point."""
    elevations: list[float] = []

    for start in range(0, len(points), ELEVATION_BATCH_SIZE):
        chunk = points[start : start + ELEVATION_BATCH_SIZE]
        lats = ",".join(str(p[0]) for p in chunk)
        lons = ",".join(str(p[1]) for p in chunk)

        resp = requests.get(
            OPEN_METEO_ELEVATION_URL,
            params={"latitude": lats, "longitude": lons},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        elevations.extend(data.get("elevation", []))

    return elevations


def find_elevation_viewpoints(
    lat: float,
    lon: float,
    radius_km: float = 20,
    num_sectors: int = ELEVATION_NUM_SECTORS,
) -> list[dict]:
    """Find the highest-elevation point in each angular sector around (lat, lon)."""
    sector_groups = _generate_sector_points(lat, lon, radius_km, num_sectors)

    all_points: list[tuple[float, float]] = []
    sector_indices: list[int] = []
    for group in sector_groups:
        for pt_lat, pt_lon, s_idx in group:
            all_points.append((pt_lat, pt_lon))
            sector_indices.append(s_idx)

    if not all_points:
        return []

    try:
        elevations = _batch_fetch_elevations(all_points)
    except Exception:
        return []

    best: dict[int, dict] = {}
    for i, elev in enumerate(elevations):
        s = sector_indices[i]
        pt_lat, pt_lon = all_points[i]
        if s not in best or elev > best[s]["elevation_m"]:
            bearing = math.degrees(
                math.atan2(
                    math.sin(math.radians(pt_lon - lon)) * math.cos(math.radians(pt_lat)),
                    math.cos(math.radians(lat)) * math.sin(math.radians(pt_lat))
                    - math.sin(math.radians(lat))
                    * math.cos(math.radians(pt_lat))
                    * math.cos(math.radians(pt_lon - lon)),
                )
            ) % 360

            best[s] = {
                "lat": round(pt_lat, 5),
                "lon": round(pt_lon, 5),
                "elevation_m": round(elev, 1),
                "distance_km": round(_haversine_km(lat, lon, pt_lat, pt_lon), 1),
                "direction": _bearing_to_label(bearing),
                "bearing": round(bearing, 1),
                "spot_type": "elevation",
            }

    return [best[s] for s in sorted(best)]
