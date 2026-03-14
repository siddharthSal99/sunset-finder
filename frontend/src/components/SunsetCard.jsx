const ratingColors = {
  Ideal: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
  Excellent: "bg-sky-500/20 text-sky-300 border-sky-500/30",
  Good: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
  Fair: "bg-orange-500/20 text-orange-300 border-orange-500/30",
  Poor: "bg-red-500/20 text-red-300 border-red-500/30",
};

export default function SunsetCard({ data }) {
  if (!data) return null;

  return (
    <div className="rounded-2xl bg-white/10 backdrop-blur-md border border-white/15 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-white">Sunset Prediction</h2>
        <span className="text-white/60 text-sm">
          {data.sunset_time} &middot; {data.sunset_azimuth}&deg;
        </span>
      </div>

      {data.conditions ? (
        <div className="space-y-2">
          {data.conditions.map((c) => (
            <ConditionRow key={c.field} condition={c} />
          ))}
        </div>
      ) : (
        <p className="text-white/50 text-sm">{data.message}</p>
      )}
    </div>
  );
}

function ConditionRow({ condition }) {
  const colorClass = ratingColors[condition.rating] || ratingColors.Fair;
  return (
    <div className="flex items-center justify-between rounded-lg bg-white/5 px-3 py-2">
      <span className="text-white/70 text-sm">{condition.field}</span>
      <div className="flex items-center gap-3">
        <span className="text-white font-medium text-sm">{condition.value}%</span>
        <span
          className={`rounded-full border px-2 py-0.5 text-xs font-semibold ${colorClass}`}
        >
          {condition.rating}
        </span>
      </div>
    </div>
  );
}
