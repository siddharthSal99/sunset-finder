import math
import hashlib
from backend.config import TERRAIN_SAMPLE_DISTANCES_KM, BEST_SPOTS_GRID_STEP_KM, BEST_SPOTS_TOP_N


def _coordinate_hash(lat: float, lon: float) -> float:
    """Deterministic pseudo-random value in [0, 1) seeded by coordinates."""
    key = f"{lat:.6f},{lon:.6f}"
    h = hashlib.md5(key.encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def get_elevation(lat: float, lon: float) -> float:
    """Mock elevation provider. Returns a plausible elevation in metres."""
    base = _coordinate_hash(lat, lon) * 500
    return round(base, 1)


def _destination_point(lat: float, lon: float, azimuth_deg: float, distance_km: float):
    """Compute destination lat/lon given start, bearing, and distance."""
    R = 6371.0
    d = distance_km / R
    brng = math.radians(azimuth_deg)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(d)
        + math.cos(lat1) * math.sin(d) * math.cos(brng)
    )
    lon2 = lon1 + math.atan2(
        math.sin(brng) * math.sin(d) * math.cos(lat1),
        math.cos(d) - math.sin(lat1) * math.sin(lat2),
    )
    return math.degrees(lat2), math.degrees(lon2)


def sample_terrain_profile(
    lat: float, lon: float, azimuth: float
) -> list[dict]:
    user_elev = get_elevation(lat, lon)
    samples = []
    for dist_km in TERRAIN_SAMPLE_DISTANCES_KM:
        pt_lat, pt_lon = _destination_point(lat, lon, azimuth, dist_km)
        pt_elev = get_elevation(pt_lat, pt_lon)
        dist_m = dist_km * 1000
        angle = math.degrees(math.atan2(pt_elev - user_elev, dist_m))
        samples.append({
            "distance_km": dist_km,
            "lat": round(pt_lat, 6),
            "lon": round(pt_lon, 6),
            "elevation": pt_elev,
            "angle": round(angle, 4),
        })
    return samples


def compute_horizon_angle(
    lat: float, lon: float, azimuth: float
) -> float:
    profile = sample_terrain_profile(lat, lon, azimuth)
    if not profile:
        return 0.0
    return max(s["angle"] for s in profile)


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


def find_best_sunset_spots(
    lat: float, lon: float, radius_km: float = 20
) -> list[dict]:
    step = BEST_SPOTS_GRID_STEP_KM
    deg_step = step / 111.0

    candidates = []
    grid_lat = lat - radius_km / 111.0
    while grid_lat <= lat + radius_km / 111.0:
        grid_lon = lon - radius_km / (111.0 * max(math.cos(math.radians(lat)), 0.01))
        lon_limit = lon + radius_km / (111.0 * max(math.cos(math.radians(lat)), 0.01))
        while grid_lon <= lon_limit:
            dist = _haversine_km(lat, lon, grid_lat, grid_lon)
            if 0.5 < dist <= radius_km:
                elev = get_elevation(grid_lat, grid_lon)
                horizon = compute_horizon_angle(grid_lat, grid_lon, 270.0)
                location_score = (5 - horizon) + elev / 1000 - dist * 0.1
                candidates.append({
                    "lat": round(grid_lat, 5),
                    "lon": round(grid_lon, 5),
                    "horizon_angle": round(horizon, 2),
                    "elevation": round(elev, 1),
                    "distance_km": round(dist, 2),
                    "score": round(location_score, 2),
                })
            grid_lon += deg_step
        grid_lat += deg_step

    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates[:BEST_SPOTS_TOP_N]
