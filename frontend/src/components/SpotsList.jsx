const ratingDot = {
  Ideal: "bg-emerald-400",
  Excellent: "bg-sky-400",
  Good: "bg-yellow-400",
  Fair: "bg-orange-400",
  Poor: "bg-red-400",
};

function MountainIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className="w-3.5 h-3.5 text-teal-400 inline-block"
    >
      <path d="M8 21l4.5-9 3.5 5 4-8" />
      <path d="M2 21h20" />
    </svg>
  );
}

function WeatherSpotContent({ spot }) {
  return (
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
  );
}

function ElevationSpotContent({ spot }) {
  return (
    <div className="flex items-center gap-2 text-xs text-white/60">
      <MountainIcon />
      <span className="text-teal-300 font-medium">
        {spot.elevation_m?.toLocaleString()}m
      </span>
      <span>&middot;</span>
      <span>{spot.direction}</span>
    </div>
  );
}

export default function SpotsList({ spots, onFlyTo }) {
  if (!spots || spots.length === 0) return null;

  const weatherSpots = spots.filter((s) => s.spot_type !== "elevation");
  const elevationSpots = spots.filter((s) => s.spot_type === "elevation");

  return (
    <div className="rounded-2xl bg-white/10 backdrop-blur-md border border-white/15 p-5 space-y-3">
      <h2 className="text-lg font-bold text-white">Nearby Conditions</h2>
      <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
        {weatherSpots.map((spot, i) => (
          <SpotButton key={`w-${i}`} spot={spot} index={i} onFlyTo={onFlyTo}>
            <WeatherSpotContent spot={spot} />
          </SpotButton>
        ))}

        {elevationSpots.length > 0 && (
          <div className="pt-2 mt-2 border-t border-white/10">
            <p className="text-xs text-white/40 uppercase tracking-wider mb-2">
              High Elevation Viewpoints
            </p>
            {elevationSpots.map((spot, i) => (
              <SpotButton
                key={`e-${i}`}
                spot={spot}
                index={weatherSpots.length + i}
                onFlyTo={onFlyTo}
              >
                <ElevationSpotContent spot={spot} />
              </SpotButton>
            ))}
          </div>
        )}
      </div>
      <Legend />
    </div>
  );
}

function SpotButton({ spot, index, onFlyTo, children }) {
  return (
    <button
      onClick={() => onFlyTo([spot.lat, spot.lon])}
      className="w-full rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 px-4 py-3 text-left transition-all cursor-pointer"
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-white font-semibold text-sm">
          #{index + 1} &middot; {spot.distance_km} km away
        </span>
      </div>
      {children}
    </button>
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
