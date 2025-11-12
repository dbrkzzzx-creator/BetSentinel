import { useEffect, useState } from "react";
import axios from "axios";

interface Rule {
  min_bet: number;
  max_bet: number;
  daily_cap: number;
  whitelist: string[];
  blacklist: string[];
  enabled: boolean;
}

interface LogEntry {
  timestamp: string;
  type: string;
  message: string;
  data?: any;
}

interface Status {
  running: boolean;
  total_spent: number;
  daily_cap: number;
  remaining: number;
  rules: Rule;
  log_count: number;
}

export default function Automation() {
  const [status, setStatus] = useState<Status | null>(null);
  const [rules, setRules] = useState<Rule>({
    min_bet: 10,
    max_bet: 100,
    daily_cap: 1000,
    whitelist: [],
    blacklist: [],
    enabled: false,
  });
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [whitelistInput, setWhitelistInput] = useState("");
  const [blacklistInput, setBlacklistInput] = useState("");
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const showToast = (message: string, type: "success" | "error") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const fetchStatus = async () => {
    try {
      const res = await axios.get("http://localhost:5000/api/automation/status");
      setStatus(res.data);
      setRules(res.data.rules);
    } catch (error) {
      console.error("Error fetching status:", error);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await axios.get("http://localhost:5000/api/automation/logs?limit=50");
      setLogs(res.data.logs.reverse());
    } catch (error) {
      console.error("Error fetching logs:", error);
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchLogs();
    const statusInterval = setInterval(fetchStatus, 5000);
    const logsInterval = setInterval(fetchLogs, 10000);
    return () => {
      clearInterval(statusInterval);
      clearInterval(logsInterval);
    };
  }, []);

  const saveRules = async () => {
    try {
      await axios.post("http://localhost:5000/api/automation/rules", rules);
      showToast("Rules saved successfully!", "success");
      fetchStatus();
    } catch (error) {
      showToast("Failed to save rules", "error");
    }
  };

  const startAutomation = async () => {
    try {
      await axios.post("http://localhost:5000/api/automation/start");
      showToast("Automation started!", "success");
      fetchStatus();
    } catch (error: any) {
      showToast(error.response?.data?.message || "Failed to start automation", "error");
    }
  };

  const stopAutomation = async () => {
    try {
      await axios.post("http://localhost:5000/api/automation/stop");
      showToast("Automation stopped!", "success");
      fetchStatus();
    } catch (error: any) {
      showToast(error.response?.data?.message || "Failed to stop automation", "error");
    }
  };

  const addToWhitelist = () => {
    if (whitelistInput.trim()) {
      setRules({
        ...rules,
        whitelist: [...rules.whitelist, whitelistInput.trim()],
      });
      setWhitelistInput("");
    }
  };

  const removeFromWhitelist = (item: string) => {
    setRules({
      ...rules,
      whitelist: rules.whitelist.filter((i) => i !== item),
    });
  };

  const addToBlacklist = () => {
    if (blacklistInput.trim()) {
      setRules({
        ...rules,
        blacklist: [...rules.blacklist, blacklistInput.trim()],
      });
      setBlacklistInput("");
    }
  };

  const removeFromBlacklist = (item: string) => {
    setRules({
      ...rules,
      blacklist: rules.blacklist.filter((i) => i !== item),
    });
  };

  return (
    <div className="bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white min-h-screen p-8">
      {toast && (
        <div
          className={`fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 ${
            toast.type === "success" ? "bg-green-600" : "bg-red-600"
          } animate-fade-in`}
        >
          {toast.message}
        </div>
      )}

      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-cyan-400 mb-8">Bet Automation System</h1>

        {/* Status Card */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 mb-6 shadow-xl border border-cyan-500/20">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-semibold mb-2">Automation Status</h2>
              <div className="flex items-center gap-4">
                <span
                  className={`px-4 py-2 rounded-full font-bold ${
                    status?.running
                      ? "bg-green-600 animate-pulse"
                      : status?.running === false
                      ? "bg-red-600"
                      : "bg-amber-600"
                  }`}
                >
                  {status?.running ? "RUNNING" : status?.running === false ? "STOPPED" : "PENDING"}
                </span>
                <span className="text-slate-300">
                  Spent: ${status?.total_spent.toFixed(2) || "0.00"} / ${status?.daily_cap || "1000.00"}
                </span>
                <span className="text-cyan-400">
                  Remaining: ${status?.remaining.toFixed(2) || "0.00"}
                </span>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={startAutomation}
                disabled={status?.running}
                className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold transition-all transform hover:scale-105"
              >
                Start
              </button>
              <button
                onClick={stopAutomation}
                disabled={!status?.running}
                className="px-6 py-3 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold transition-all transform hover:scale-105"
              >
                Stop
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Rule Editor */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 shadow-xl border border-cyan-500/20">
            <h2 className="text-2xl font-semibold mb-4 text-cyan-400">Rule Editor</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Minimum Bet ($)</label>
                <input
                  type="number"
                  value={rules.min_bet}
                  onChange={(e) => setRules({ ...rules, min_bet: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Maximum Bet ($)</label>
                <input
                  type="number"
                  value={rules.max_bet}
                  onChange={(e) => setRules({ ...rules, max_bet: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Daily Cap ($)</label>
                <input
                  type="number"
                  value={rules.daily_cap}
                  onChange={(e) => setRules({ ...rules, daily_cap: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Team Whitelist</label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={whitelistInput}
                    onChange={(e) => setWhitelistInput(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && addToWhitelist()}
                    placeholder="Enter team name"
                    className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                  <button
                    onClick={addToWhitelist}
                    className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg transition"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {rules.whitelist.map((item, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-green-600 rounded-full text-sm flex items-center gap-2"
                    >
                      {item}
                      <button onClick={() => removeFromWhitelist(item)} className="hover:text-red-300">
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Team Blacklist</label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={blacklistInput}
                    onChange={(e) => setBlacklistInput(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && addToBlacklist()}
                    placeholder="Enter team name"
                    className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                  <button
                    onClick={addToBlacklist}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {rules.blacklist.map((item, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-red-600 rounded-full text-sm flex items-center gap-2"
                    >
                      {item}
                      <button onClick={() => removeFromBlacklist(item)} className="hover:text-red-300">
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              <button
                onClick={saveRules}
                className="w-full px-6 py-3 bg-cyan-600 hover:bg-cyan-700 rounded-lg font-semibold transition-all transform hover:scale-105"
              >
                Save Rules
              </button>
            </div>
          </div>

          {/* Log Viewer */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 shadow-xl border border-cyan-500/20">
            <h2 className="text-2xl font-semibold mb-4 text-cyan-400">Activity Log</h2>
            <div className="bg-slate-900/50 rounded-lg p-4 max-h-96 overflow-y-auto">
              {logs.length === 0 ? (
                <p className="text-slate-400 text-center py-8">No logs yet</p>
              ) : (
                <div className="space-y-2">
                  {logs.map((log, idx) => (
                    <div
                      key={idx}
                      className="bg-slate-700/50 rounded-lg p-3 border-l-4 border-cyan-500"
                    >
                      <div className="flex justify-between items-start mb-1">
                        <span
                          className={`text-xs font-semibold px-2 py-1 rounded ${
                            log.type === "bet_placed"
                              ? "bg-green-600"
                              : log.type === "bet_rejected"
                              ? "bg-red-600"
                              : log.type === "automation_started"
                              ? "bg-blue-600"
                              : log.type === "automation_stopped"
                              ? "bg-amber-600"
                              : "bg-gray-600"
                          }`}
                        >
                          {log.type}
                        </span>
                        <span className="text-xs text-slate-400">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-sm text-slate-200">{log.message}</p>
                      {log.data && (
                        <pre className="text-xs text-slate-400 mt-2 overflow-x-auto">
                          {JSON.stringify(log.data, null, 2)}
                        </pre>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}

