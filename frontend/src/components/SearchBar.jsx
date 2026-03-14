import { useState } from "react";

export default function SearchBar({ onSearch, loading }) {
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    const la = parseFloat(lat);
    const lo = parseFloat(lon);
    if (!isNaN(la) && !isNaN(lo)) onSearch(la, lo);
  }

  function handleMyLocation() {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const la = pos.coords.latitude;
        const lo = pos.coords.longitude;
        setLat(la.toFixed(4));
        setLon(lo.toFixed(4));
        onSearch(la, lo);
      },
      () => alert("Could not get your location"),
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2">
      <div className="flex gap-2">
        <input
          type="number"
          step="any"
          placeholder="Latitude"
          value={lat}
          onChange={(e) => setLat(e.target.value)}
          className="flex-1 rounded-lg bg-white/10 border border-white/20 px-3 py-2 text-sm text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-sunset-400"
        />
        <input
          type="number"
          step="any"
          placeholder="Longitude"
          value={lon}
          onChange={(e) => setLon(e.target.value)}
          className="flex-1 rounded-lg bg-white/10 border border-white/20 px-3 py-2 text-sm text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-sunset-400"
        />
      </div>
      <div className="flex gap-2">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 rounded-lg bg-gradient-to-r from-sunset-500 to-sunset-600 px-4 py-2 text-sm font-semibold text-white shadow-md hover:from-sunset-600 hover:to-sunset-700 disabled:opacity-50 transition-all cursor-pointer"
        >
          {loading ? "Loading..." : "Find Sunset"}
        </button>
        <button
          type="button"
          onClick={handleMyLocation}
          className="rounded-lg bg-white/10 border border-white/20 px-3 py-2 text-sm text-white hover:bg-white/20 transition-all cursor-pointer"
          title="Use my location"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>
      </div>
      <p className="text-xs text-white/40 text-center">or click anywhere on the map</p>
    </form>
  );
}
