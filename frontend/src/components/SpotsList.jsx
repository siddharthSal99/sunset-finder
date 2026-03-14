const ratingDot = {
  Ideal: "bg-emerald-400",
  Excellent: "bg-sky-400",
  Good: "bg-yellow-400",
  Fair: "bg-orange-400",
  Poor: "bg-red-400",
};

export default function SpotsList({ spots, onFlyTo }) {
  if (!spots || spots.length === 0) return null;

  return (
    <div className="rounded-2xl bg-white/10 backdrop-blur-md border border-white/15 p-5 space-y-3">
      <h2 className="text-lg font-bold text-white">Nearby Conditions</h2>
      <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
        {spots.map((spot, i) => (
          <button
            key={i}
            onClick={() => onFlyTo([spot.lat, spot.lon])}
            className="w-full rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 px-4 py-3 text-left transition-all cursor-pointer"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-semibold text-sm">
                #{i + 1} &middot; {spot.distance_km} km away
              </span>
            </div>
            <div className="flex gap-3 flex-wrap">
              {(spot.conditions || []).map((c) => (
                <span
                  key={c.field}
                  className="flex items-center gap-1.5 text-xs text-white/60"
                  title={`${c.field}: ${c.value}% (${c.rating})`}
                >
                  <span
                    className={`inline-block w-2 h-2 rounded-full ${ratingDot[c.rating]}`}
                  />
                  {c.field.replace(" Clouds", "")}
                </span>
              ))}
            </div>
          </button>
        ))}
      </div>
      <Legend />
    </div>
  );
}

function Legend() {
  return (
    <div className="flex gap-3 justify-center pt-2 border-t border-white/10">
      {Object.entries(ratingDot).map(([label, color]) => (
        <span
          key={label}
          className="flex items-center gap-1 text-xs text-white/40"
        >
          <span className={`inline-block w-2 h-2 rounded-full ${color}`} />
          {label}
        </span>
      ))}
    </div>
  );
}
