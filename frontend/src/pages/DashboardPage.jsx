import { useEffect, useMemo, useState, useContext } from "react";
import {
  LineChart,
  Line,
  CartesianGrid,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Cell,
} from "recharts";
import { ThemeContext } from "../context/ThemeContext";
import StatCard from "../components/StatCard";
import LogsTable from "../components/LogsTable";
import RulesPanel from "../components/RulesPanel";
import { getLogs, getOverview, getRules, getSeverity, getTrend, toggleRule } from "../services/dashboard";

const PIE_COLORS = ["#ef4444", "#f97316", "#38bdf8", "#22c55e"];

function parseHourValue(value) {
  if (!value) return null;
  const parsed = new Date(String(value).replace(" ", "T"));
  if (!Number.isNaN(parsed.getTime())) return parsed;
  return null;
}

function getHourKey(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  const h = String(date.getHours()).padStart(2, "0");
  return `${y}-${m}-${d} ${h}:00`;
}

function getHourLabel(date) {
  return `${String(date.getHours()).padStart(2, "0")}:00`;
}

function DashboardPage({ onLogout }) {
  const { isDark, toggleTheme } = useContext(ThemeContext);
  const [overview, setOverview] = useState(null);
  const [trend, setTrend] = useState([]);
  const [severity, setSeverity] = useState([]);
  const [logs, setLogs] = useState([]);
  const [rules, setRules] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const load = async (currentPage = page) => {
    const [o, t, s, l, r] = await Promise.all([
      getOverview(),
      getTrend(),
      getSeverity(),
      getLogs(currentPage, 10),
      getRules(),
    ]);
    setOverview(o);
    setTrend(t);
    setSeverity(s);
    setLogs(l.items);
    setTotal(l.total);
    setRules(r);
  };

  useEffect(() => {
    load();
    const timer = setInterval(() => load(page), 5000);
    return () => clearInterval(timer);
  }, [page]);

  const onToggle = async (ruleId, enabled) => {
    await toggleRule(ruleId, enabled);
    await load(page);
  };

  const trendChartData = useMemo(() => {
    const buckets = new Map();
    for (let i = 23; i >= 0; i -= 1) {
      const d = new Date();
      d.setMinutes(0, 0, 0);
      d.setHours(d.getHours() - i);
      const key = getHourKey(d);
      buckets.set(key, {
        hour: key,
        label: getHourLabel(d),
        attacks: 0,
      });
    }

    for (const point of trend) {
      const parsed = parseHourValue(point.hour);
      if (!parsed) continue;
      parsed.setMinutes(0, 0, 0);
      const key = getHourKey(parsed);
      if (buckets.has(key)) {
        buckets.set(key, {
          ...buckets.get(key),
          attacks: Number(point.attacks || 0),
        });
      }
    }

    return Array.from(buckets.values());
  }, [trend]);

  const pageCount = Math.max(1, Math.ceil(total / 10));
  const peak = trendChartData.reduce((acc, cur) => Math.max(acc, cur.attacks), 0);
  const avg = trendChartData.length
    ? (trendChartData.reduce((acc, cur) => acc + cur.attacks, 0) / trendChartData.length).toFixed(2)
    : "0.00";

  return (
    <main className="dashboard-shell">
      <header className="mb-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.35em] text-[var(--accent)]">CAFW Security Grid</p>
          <h1 className="font-display text-3xl font-bold text-[var(--text)]">Central Admin Dashboard</h1>
        </div>
        <div className="flex gap-3 items-center">
          <button
            onClick={toggleTheme}
            className="icon-btn"
            title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {isDark ? <span className="text-lg">☀</span> : <span className="text-lg">☾</span>}
          </button>
          <button
            className="icon-btn px-4"
            onClick={onLogout}
          >
            Logout
          </button>
        </div>
      </header>

      {overview && (
        <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-5">
          <StatCard label="Total Attacks" value={overview.total_attacks} tone="danger" delta={`${avg}/min`} />
          <StatCard label="Blocked" value={overview.blocked_last_24h} tone="warning" delta={`${avg}/min`} />
          <StatCard label="High/Critical" value={overview.high_severity_last_24h} tone="warning" delta={`${Number(avg) * 0.92 || 0}/min`} />
          <StatCard label="Peak Hour" value={peak} tone="info" delta={`${avg}/min`} />
          <StatCard label="Active Rules" value={overview.active_rules} tone="safe" />
        </section>
      )}

      <section className="mt-6 grid grid-cols-1 gap-4 xl:grid-cols-3">
        <div className="dash-card p-4 xl:col-span-2">
          <h3 className="panel-title">24h Attack Trend</h3>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%" minWidth={280} minHeight={280}>
              <LineChart data={trendChartData}>
                <CartesianGrid stroke={isDark ? "#253547" : "#d8deea"} strokeDasharray="3 3" />
                <XAxis
                  dataKey="label"
                  tick={{ fill: isDark ? "#cbd5e1" : "#6b7280", fontSize: 11 }}
                  minTickGap={24}
                />
                <YAxis tick={{ fill: isDark ? "#cbd5e1" : "#6b7280", fontSize: 11 }} />
                <Tooltip labelFormatter={(_, payload) => payload?.[0]?.payload?.hour || "Hour"} />
                <Line
                  type="monotone"
                  dataKey="attacks"
                  stroke="#f38b2a"
                  dot={{ fill: "#f38b2a", r: 4, strokeWidth: 2 }}
                  activeDot={{ r: 7 }}
                  strokeWidth={2.5}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="dash-card p-4">
          <h3 className="panel-title">Attack Breakdown</h3>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%" minWidth={280} minHeight={280}>
              <PieChart>
                <Pie data={severity} dataKey="count" nameKey="severity" outerRadius={100}>
                  {severity.map((entry, index) => (
                    <Cell key={entry.severity} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="mt-6 grid grid-cols-1 gap-4 xl:grid-cols-2">
        <div className="dash-card p-4">
          <h3 className="panel-title">Detection Rules</h3>
          <RulesPanel rules={rules} onToggle={onToggle} />
        </div>

        <div className="dash-card p-4">
          <h3 className="panel-title">Recent Activity</h3>
          <LogsTable logs={logs} />
          <div className="mt-3 flex items-center justify-end gap-2 text-sm text-[var(--text-dim)]">
            <button
              className="pager-btn"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              Prev
            </button>
            <span className="font-mono">{page} / {pageCount}</span>
            <button
              className="pager-btn"
              disabled={page >= pageCount}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}

export default DashboardPage;
