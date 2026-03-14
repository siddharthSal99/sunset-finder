export default function SpotsList({ spots, onFlyTo }) {
  if (!spots || spots.length === 0) return null;

  return (
    <div className="rounded-2xl bg-white/10 backdrop-blur-md border border-white/15 p-5 space-y-3">
      <h2 className="text-lg font-bold text-white">Best Nearby Spots</h2>
      <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
        {spots.map((spot, i) => (
          <button
            key={i}
            onClick={() => onFlyTo([spot.lat, spot.lon])}
            className="w-full rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 px-4 py-3 text-left transition-all cursor-pointer"
          >
            <div className="flex items-center justify-between">
              <span className="text-white font-semibold text-sm">
                #{i + 1}
              </span>
              <span className="text-sunset-300 text-sm font-bold">
                {spot.score.toFixed(1)} pts
              </span>
            </div>
            <div className="flex gap-4 mt-1 text-xs text-white/50">
              <span>{spot.distance_km} km away</span>
              <span>Horizon {spot.horizon_angle}&deg;</span>
              <span>Elev {spot.elevation}m</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
