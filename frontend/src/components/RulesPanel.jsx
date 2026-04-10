function RulesPanel({ rules, onToggle }) {
  return (
    <div className="dash-card p-4">
      <h3 className="panel-title">Detection Rules</h3>
      <div className="mt-4 space-y-3">
        {rules.map((rule) => (
          <div key={rule.id} className="rounded-xl border border-[var(--line)]/80 bg-[var(--panel-soft)] p-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-display text-base text-[var(--text)]">{rule.name}</p>
                <p className="mt-1 text-sm text-[var(--muted)]">{rule.description}</p>
                <p className="mt-1 font-mono text-xs text-[var(--muted)]/80">{rule.pattern}</p>
              </div>
              <button
                className={`rounded-md border px-3 py-1 text-[10px] font-semibold uppercase tracking-widest ${
                  rule.enabled
                    ? "border-emerald-500/50 bg-emerald-500/15 text-emerald-400"
                    : "border-[var(--line)] bg-[var(--panel)] text-[var(--muted)]"
                }`}
                onClick={() => onToggle(rule.id, !rule.enabled)}
              >
                {rule.enabled ? "Enabled" : "Disabled"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default RulesPanel;
