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
    <div className="bg-slate-900 text-white min-h-screen p-8">
      <h1 className="text-3xl font-bold text-cyan-400 mb-6">BetSentinel Dashboard</h1>
      <div className="mb-6">
        <span className={`px-3 py-1 rounded-full ${status === "running" ? "bg-green-600" : status === "error" ? "bg-red-600" : "bg-gray-600"}`}>
          {status.toUpperCase()}
        </span>
      </div>
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {events.map((event, i) => (
          <div key={i} className="bg-slate-800 p-4 rounded-lg shadow-md hover:shadow-cyan-400/30 transition">
            <h2 className="text-xl mb-2">{event.match}</h2>
            <div className="flex justify-between text-cyan-300">
              <span>Home: {event.odds.home}</span>
              <span>Draw: {event.odds.draw}</span>
              <span>Away: {event.odds.away}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

