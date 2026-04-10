function StatCard({ label, value, tone = "info", subtext = "LAST 24H", delta = null }) {
  const toneClass = {
    info: "card-info",
    danger: "card-danger",
    warning: "card-warning",
    safe: "card-safe",
  }[tone];

  return (
    <article className={`stats-card ${toneClass}`}>
      <p className="stats-label">{label}</p>
      <div className="stats-main-row">
        <p className="stats-value">{value}</p>
        <p className="stats-subtext">{subtext}</p>
      </div>
      {delta !== null && <p className="stats-delta">{delta}</p>}
    </article>
  );
}

export default StatCard;
