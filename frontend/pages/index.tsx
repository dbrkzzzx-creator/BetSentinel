import { useEffect, useState } from "react";
import axios from "axios";

export default function Home() {
  const [status, setStatus] = useState("loading");
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const s = await axios.get("http://localhost:5000/api/status");
        setStatus(s.data.status);
        const e = await axios.get("http://localhost:5000/api/events");
        setEvents(e.data);
      } catch {
        setStatus("error");
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold text-cyan-400">BetSentinel Dashboard</h1>
          <a
            href="/automation"
            className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 rounded-lg font-semibold transition-all transform hover:scale-105"
          >
            Automation →
          </a>
        </div>
        
        <div className="mb-6">
          <span className={`px-4 py-2 rounded-full font-bold ${status === "running" ? "bg-green-600 animate-pulse" : status === "error" ? "bg-red-600" : "bg-gray-600"}`}>
            {status.toUpperCase()}
          </span>
        </div>
        
        <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {events.map((event: any, i: number) => (
            <div key={i} className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-xl shadow-xl border border-cyan-500/20 hover:shadow-cyan-400/30 transition-all transform hover:scale-105">
              <h2 className="text-xl mb-4 font-semibold">{event.match}</h2>
              <div className="flex justify-between text-cyan-300">
                <div className="text-center">
                  <div className="text-xs text-slate-400 mb-1">Home</div>
                  <div className="text-lg font-bold">{event.odds.home}</div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-slate-400 mb-1">Draw</div>
                  <div className="text-lg font-bold">{event.odds.draw}</div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-slate-400 mb-1">Away</div>
                  <div className="text-lg font-bold">{event.odds.away}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

