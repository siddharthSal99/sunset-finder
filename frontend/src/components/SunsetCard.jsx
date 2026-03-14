const ratingColors = {
  Spectacular: "from-sunset-400 to-pink-500",
  Great: "from-sunset-400 to-sunset-600",
  Good: "from-yellow-400 to-sunset-500",
  Fair: "from-yellow-300 to-yellow-500",
  Poor: "from-gray-400 to-gray-500",
};

export default function SunsetCard({ data }) {
  if (!data) return null;

  const pct = Math.min(100, Math.max(0, data.sunset_score * 10));
  const gradient = ratingColors[data.rating] || ratingColors.Fair;

  return (
    <div className="rounded-2xl bg-white/10 backdrop-blur-md border border-white/15 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-white">Sunset Prediction</h2>
        <span
          className={`rounded-full bg-gradient-to-r ${gradient} px-3 py-1 text-xs font-bold text-white shadow`}
        >
          {data.rating}
        </span>
      </div>

      {/* Score bar */}
      <div>
        <div className="flex justify-between text-sm text-white/70 mb-1">
          <span>Quality Score</span>
          <span className="font-semibold text-white">{data.sunset_score.toFixed(1)} / 10</span>
        </div>
        <div className="h-3 rounded-full bg-white/10 overflow-hidden">
          <div
            className={`h-full rounded-full bg-gradient-to-r ${gradient} transition-all duration-700`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* Info grid */}
      <div className="grid grid-cols-2 gap-3 text-sm">
        <InfoItem label="Sunset Time" value={data.sunset_time} />
        <InfoItem label="Adjusted Sunset" value={data.adjusted_sunset} />
        <InfoItem label="Horizon Angle" value={`${data.terrain_horizon_angle}\u00B0`} />
        <InfoItem label="Humidity" value={`${data.humidity}%`} />
        <InfoItem label="Low Cloud" value={`${data.cloud_cover_low}%`} />
        <InfoItem label="Mid Cloud" value={`${data.cloud_cover_mid}%`} />
        <InfoItem label="High Cloud" value={`${data.cloud_cover_high}%`} />
      </div>
    </div>
  );
}

function InfoItem({ label, value }) {
  return (
    <div className="rounded-lg bg-white/5 px-3 py-2">
      <p className="text-white/50 text-xs">{label}</p>
      <p className="text-white font-medium">{value}</p>
    </div>
  );
}
