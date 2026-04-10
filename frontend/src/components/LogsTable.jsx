import { useState } from "react";

function LogsTable({ logs }) {
  const [selectedLog, setSelectedLog] = useState(null);

  const closeInspector = () => setSelectedLog(null);

  const copyPayload = async () => {
    if (!selectedLog?.payload_snippet) return;
    try {
      await navigator.clipboard.writeText(selectedLog.payload_snippet);
    } catch {
      // Ignore clipboard errors in unsupported contexts.
    }
  };

  return (
    <div className="dash-card p-4">
      <h3 className="panel-title">Recent Activity</h3>
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full text-left text-sm text-[var(--text-dim)]">
          <thead className="border-b border-[var(--line)] text-[11px] uppercase tracking-wide text-[var(--muted)]">
            <tr>
              <th className="px-3 py-2">Time</th>
              <th className="px-3 py-2">Path</th>
              <th className="px-3 py-2">Rule</th>
              <th className="px-3 py-2">Severity</th>
              <th className="px-3 py-2">IP</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr
                key={log.id}
                className="cursor-pointer border-b border-[var(--line)]/70"
                onClick={() => setSelectedLog(log)}
                title="Open incident details"
              >
                <td className="px-3 py-2 font-mono text-xs">{new Date(log.timestamp).toLocaleString()}</td>
                <td className="px-3 py-2">{log.path}</td>
                <td className="px-3 py-2">{log.matched_rule}</td>
                <td className="px-3 py-2 capitalize">
                  <span
                    className={`rounded-full px-2 py-1 text-xs ${
                      ["critical", "high"].includes(log.severity)
                        ? "bg-red-500/20 text-red-300"
                        : "bg-orange-500/20 text-orange-300"
                    }`}
                  >
                    {log.severity}
                  </span>
                </td>
                <td className="px-3 py-2 font-mono text-xs">{log.ip}</td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr>
                <td colSpan={5} className="px-3 py-4 text-center text-[var(--muted)]">
                  No attacks logged yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {selectedLog && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/35 px-4 backdrop-blur-sm">
          <div className="w-full max-w-3xl rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-2xl">
            <div className="flex items-start justify-between gap-4 border-b border-[var(--line)] pb-4">
              <div>
                <h4 className="font-display text-xl font-bold text-[var(--text)]">Incident Inspector</h4>
                <p className="mt-1 text-sm text-[var(--muted)]">
                  Log #{selectedLog.id} • {new Date(selectedLog.timestamp).toLocaleString()}
                </p>
              </div>
              <button
                className="icon-btn"
                onClick={closeInspector}
              >
                Close
              </button>
            </div>

            <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
              <div className="rounded-lg border border-[var(--line)] bg-[var(--panel-soft)] p-3">
                <p className="text-xs uppercase text-[var(--muted)]">Method</p>
                <p className="font-mono text-sm text-[var(--text)]">{selectedLog.method}</p>
              </div>
              <div className="rounded-lg border border-[var(--line)] bg-[var(--panel-soft)] p-3">
                <p className="text-xs uppercase text-[var(--muted)]">Path</p>
                <p className="font-mono text-sm break-all text-[var(--text)]">{selectedLog.path}</p>
              </div>
              <div className="rounded-lg border border-[var(--line)] bg-[var(--panel-soft)] p-3">
                <p className="text-xs uppercase text-[var(--muted)]">Matched Rule</p>
                <p className="text-sm text-[var(--text)]">{selectedLog.matched_rule}</p>
              </div>
              <div className="rounded-lg border border-[var(--line)] bg-[var(--panel-soft)] p-3">
                <p className="text-xs uppercase text-[var(--muted)]">Severity / Action</p>
                <p className="text-sm capitalize text-[var(--text)]">
                  {selectedLog.severity} / {selectedLog.action}
                </p>
              </div>
              <div className="rounded-lg border border-[var(--line)] bg-[var(--panel-soft)] p-3 md:col-span-2">
                <p className="text-xs uppercase text-[var(--muted)]">Client</p>
                <p className="font-mono text-xs break-all text-[var(--text)]">{selectedLog.ip}</p>
                <p className="mt-2 font-mono text-xs break-all text-[var(--text-dim)]">{selectedLog.user_agent}</p>
              </div>
            </div>

            <div className="mt-4 rounded-lg border border-[var(--line)] bg-[var(--panel-soft)] p-3">
              <div className="mb-2 flex items-center justify-between gap-3">
                <p className="text-xs uppercase text-[var(--muted)]">Payload Snippet</p>
                <button
                  className="icon-btn px-2 py-1 text-xs"
                  onClick={copyPayload}
                >
                  Copy Payload
                </button>
              </div>
              <pre className="max-h-44 overflow-auto whitespace-pre-wrap break-words font-mono text-xs text-[var(--text-dim)]">
                {selectedLog.payload_snippet || "No payload snippet available."}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default LogsTable;
