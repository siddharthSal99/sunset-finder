export async function fetchSunsetPrediction(lat, lon, date = null) {
  const params = new URLSearchParams({ lat, lon });
  if (date) params.set("date", date);
  const res = await fetch(`/api/sunset?${params}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function fetchBestSpots(lat, lon, radiusKm = 20) {
  const params = new URLSearchParams({ lat, lon, radius_km: radiusKm });
  const res = await fetch(`/api/best-sunset-spots?${params}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
