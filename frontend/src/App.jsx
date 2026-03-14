import { useState, useCallback } from "react";
import MapView from "./components/MapView";
import SearchBar from "./components/SearchBar";
import SunsetCard from "./components/SunsetCard";
import SpotsList from "./components/SpotsList";
import { fetchSunsetPrediction, fetchBestSpots } from "./api/sunset";

export default function App() {
  const [position, setPosition] = useState(null);
  const [sunsetData, setSunsetData] = useState(null);
  const [spots, setSpots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [flyTo, setFlyTo] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleSearch = useCallback(async (lat, lon) => {
    setPosition([lat, lon]);
    setFlyTo([lat, lon]);
    setLoading(true);
    setError(null);
    setSunsetData(null);
    setSpots([]);

    try {
      const [sunset, spotsRes] = await Promise.all([
        fetchSunsetPrediction(lat, lon),
        fetchBestSpots(lat, lon),
      ]);
      setSunsetData(sunset);
      setSpots(spotsRes.spots || []);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }, []);

  const handleMapClick = useCallback(
    (latlng) => {
      handleSearch(
        parseFloat(latlng.lat.toFixed(4)),
        parseFloat(latlng.lng.toFixed(4)),
      );
    },
    [handleSearch],
  );

  const handleFlyTo = useCallback((coords) => {
    setFlyTo(coords);
  }, []);

  return (
    <div className="relative h-screen w-screen overflow-hidden bg-night-900">
      {/* Map */}
      <MapView
        position={position}
        spots={spots}
        onMapClick={handleMapClick}
        flyTo={flyTo}
      />

      {/* Toggle button (mobile) */}
      <button
        onClick={() => setSidebarOpen((v) => !v)}
        className="absolute top-4 right-4 z-20 rounded-xl bg-night-800/80 backdrop-blur-md border border-white/10 px-3 py-2 text-white text-sm md:hidden cursor-pointer"
      >
        {sidebarOpen ? "Hide" : "Show Panel"}
      </button>

      {/* Sidebar */}
      <div
        className={`absolute top-0 right-0 z-10 h-full w-full max-w-sm transition-transform duration-300 ${
          sidebarOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="h-full overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-night-900/95 via-night-800/90 to-twilight-900/90 backdrop-blur-lg">
          {/* Header */}
          <div className="pt-2 pb-2">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-sunset-300 to-sunset-500 bg-clip-text text-transparent">
              Sunset Finder
            </h1>
            <p className="text-sm text-white/40 mt-1">
              Discover the best sunset views near you
            </p>
          </div>

          {/* Search */}
          <SearchBar onSearch={handleSearch} loading={loading} />

          {/* Error */}
          {error && (
            <div className="rounded-xl bg-red-500/20 border border-red-500/30 px-4 py-3 text-sm text-red-200">
              {error}
            </div>
          )}

          {/* Results */}
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-sunset-400 border-t-transparent" />
            </div>
          )}

          <SunsetCard data={sunsetData} />
          <SpotsList spots={spots} onFlyTo={handleFlyTo} />

          {!sunsetData && !loading && (
            <div className="text-center py-12 text-white/30 text-sm">
              <p>Click on the map or enter coordinates</p>
              <p>to get a sunset prediction</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
