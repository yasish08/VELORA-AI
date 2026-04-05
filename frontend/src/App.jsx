import React, { useState, useEffect, useRef, useMemo } from "react";
import axios from "axios";
import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Legend,
} from "recharts";
import "./App.css";

const isNative = Boolean(window?.Capacitor?.isNativePlatform?.());
const API_URL =
  import.meta.env.VITE_API_URL ||
  (isNative
    ? "http://10.0.2.2:8000"
    : `http://${window.location.hostname}:8000`);

const DATASET_YEAR_START = 2020;
const DATASET_YEAR_END = 2026;

const buildExampleQueries = (startYear, endYear) => {
  const safeStart = Number.isInteger(startYear) ? startYear : 2018;
  const safeEnd = Number.isInteger(endYear) ? endYear : 2022;
  const midYear = Math.floor((safeStart + safeEnd) / 2);

  return [
    `Show temperature trend in Indian Ocean from ${safeStart} to ${safeEnd}`,
    `What is the salinity in Pacific Ocean from ${safeStart} to ${safeEnd}?`,
    `Atlantic Ocean temperature in ${midYear}`,
    `How warm is the Arctic Ocean in ${safeEnd}?`,
  ];
};

const REGION_EMOJIS = {
  "Indian Ocean":   "🌊",
  "Pacific Ocean":  "🌏",
  "Atlantic Ocean": "🌎",
  "Arctic Ocean":   "🧊",
};

const CustomTooltip = ({ active, payload, label, parameter }) => {
  if (!active || !payload?.length) return null;
  const unit = parameter === "temperature" ? "°C" : "PSU";
  return (
    <div className="chart-tooltip">
      <div className="tooltip-year">{label}</div>
      <div className="tooltip-value">
        {payload[0]?.value?.toFixed(2)}
        <span className="tooltip-unit">{unit}</span>
      </div>
    </div>
  );
};

export default function App() {
  const [connected, setConnected]   = useState(false);
  const [input, setInput]           = useState("");
  const [messages, setMessages]     = useState([]);
  const [result, setResult]         = useState(null);
  const [loading, setLoading]       = useState(false);
  const [globalStats, setGlobalStats] = useState(null);
  const [showStats, setShowStats]   = useState(false);
  const chatEndRef                  = useRef(null);
  const queryCache                  = useRef({}); // Cache for query results

  const exampleQueries = useMemo(() => buildExampleQueries(DATASET_YEAR_START, DATASET_YEAR_END), []);

  const inputPlaceholder = useMemo(
    () => `e.g. Show temperature in Indian Ocean from ${DATASET_YEAR_START}–${DATASET_YEAR_END}`,
    []
  );

  // Health check
  useEffect(() => {
    axios.get(`${API_URL}/`).then(() => setConnected(true)).catch(() => setConnected(false));
  }, []);

  // Auto-scroll messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchGlobalStats = async () => {
    try {
      setShowStats(true);
      if (globalStats) return;
      const res = await axios.get(`${API_URL}/stats/summary`);
      setGlobalStats(res.data);
    } catch (err) {
      console.error("Failed to fetch global stats", err);
    }
  };

  const sendQuery = async (question) => {
    if (!question.trim()) return;

    const userMsg = { role: "user", text: question };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setResult(null);

    try {
      // Check cache first
      if (queryCache.current[question]) {
        const data = queryCache.current[question];
        if (data.chat_only && data.answer?.text) {
          setMessages((prev) => [...prev, { role: "ai", text: data.answer.text }]);
          setLoading(false);
          return;
        }
        if (data.render_chart === false) {
          setMessages((prev) => [...prev, { role: "ai", text: data.answer?.text || "" }]);
          setLoading(false);
          return;
        }
        setResult(data);
        const aiText = data.answer?.text
          ? data.answer.text
          : `Analysed **${data.region}** (${data.start_year}–${data.end_year}) — ` +
            `${data.parameter} · Mean: **${data.stats.mean}** · ` +
            `Trend: **${data.trend?.direction || "stable"}** · Insight cached`;
        setMessages((prev) => [...prev, { role: "ai", text: aiText }]);
        setLoading(false);
        return;
      }

      const res = await axios.post(`${API_URL}/query`, { question });
      const data = res.data;

      if (data.error) {
        setMessages((prev) => [
          ...prev,
          { role: "ai", text: data.message || data.error, isError: true },
        ]);
      } else {
        if (data.chat_only && data.answer?.text) {
          queryCache.current[question] = data;
          setMessages((prev) => [...prev, { role: "ai", text: data.answer.text }]);
          return;
        }
        if (data.render_chart === false) {
          queryCache.current[question] = data;
          setMessages((prev) => [...prev, { role: "ai", text: data.answer?.text || "" }]);
          return;
        }
        // Cache the result
        queryCache.current[question] = data;
        setResult(data);
        const aiText = data.answer?.text
          ? data.answer.text
          : `Analysed **${data.region}** (${data.start_year}–${data.end_year}) — ` +
            `${data.parameter} · Mean: **${data.stats.mean}** · ` +
            `Trend: **${data.trend?.direction || "stable"}** · Insight ready`;
        setMessages((prev) => [...prev, { role: "ai", text: aiText }]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "ai", text: "⚠️ Backend unreachable. Make sure the FastAPI server is running.", isError: true },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Merge historical + prediction into one chart array
  const chartData = useMemo(() => {
    if (result?.timeseries?.length) {
      return result.timeseries.map((point) => ({
        label: point.label,
        [result.parameter]: point.value,
        predicted: null,
      }));
    }

    if (!result?.yearly_data?.length) return [];

    const hist = result.yearly_data.map((point) => ({
      label: String(point.year),
      [result.parameter]: point.value,
      predicted: null,
    }));

    const predPoints = (result.prediction || []).map((p) => ({
      label: String(p.year),
      [result.parameter]: null,
      predicted: parseFloat(p.value.toFixed(2)),
    }));

    return [...hist, ...predPoints];
  }, [result]);

  const handleSubmit = (e) => {
    e.preventDefault();
    sendQuery(input);
  };

  const trendDir  = result?.trend?.direction;
  const trendIcon = trendDir === "rising" ? "↑" : trendDir === "falling" ? "↓" : "→";
  const risk = result?.risk;
  const riskClass = risk?.level_key ? `risk-${risk.level_key}` : "risk-low";

  return (
    <div className="app">

      {/* ── HEADER ── */}
      <header className="header">
        <div className="header-brand">
          <div className="header-logo">🌊</div>
          <div>
            <div className="header-title">Velora AI</div>
            <div className="header-subtitle">Ocean Intelligence Platform</div>
          </div>
        </div>
        <div className="header-status">
          <button className="stats-btn" onClick={fetchGlobalStats}>
            📊 Global Stats
          </button>
          <div className={`status-dot ${connected ? "connected" : ""}`} />
          {connected ? "Backend Connected" : "Backend Offline"}
        </div>
      </header>

      {/* ── MAIN ── */}
      <main className="main">

        {/* ── LEFT: Chat Interface ── */}
        <aside className="chat-panel">
          <div className="glass chat-card">
            <div className="chat-label">Ask Velora</div>

            {/* Message feed */}
            <div className="chat-feed">
              {messages.length === 0 && (
                <div className="chat-welcome">
                  <div className="chat-welcome-icon">🤖</div>
                  <div className="chat-welcome-title">Ask me about ocean data</div>

                  <div className="example-list">
                    {exampleQueries.map((q, i) => (
                      <button
                        key={i}
                        className="example-chip"
                        onClick={() => sendQuery(q)}
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map((msg, i) => (
                <div key={i} className={`message ${msg.role} ${msg.isError ? "error" : ""}`}>
                  <div className="message-avatar">
                    {msg.role === "user" ? "👤" : "🌊"}
                  </div>
                  <div className="message-bubble">
                    <FormattedText text={msg.text} />
                  </div>
                </div>
              ))}

              {loading && (
                <div className="message ai">
                  <div className="message-avatar">🌊</div>
                  <div className="message-bubble loading-bubble">
                    <span className="dot-1">●</span>
                    <span className="dot-2">●</span>
                    <span className="dot-3">●</span>
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>

            {/* Input */}
            <form className="chat-input-row" onSubmit={handleSubmit}>
              <input
                type="text"
                className="chat-input"
                placeholder={inputPlaceholder}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading}
              />
              <button className="send-btn" type="submit" disabled={loading || !input.trim()}>
                {loading ? <span className="mini-spinner" /> : "→"}
              </button>
            </form>
          </div>
        </aside>

        {/* ── RIGHT: Dashboard ── */}
        <section className="dashboard">

          {/* Hero empty */}
          {!result && !loading && (
            <div className="hero-empty">
              <div className="hero-icon">🌐</div>
              <h2 className="hero-title">Select a Region to Explore</h2>
              <p className="hero-desc">
                Type a natural language question in the chat panel — Velora will parse your
                intent and visualize the ARGO float data instantly.
              </p>
              <div className="quick-pills">
                {["Indian Ocean", "Pacific Ocean", "Atlantic Ocean", "Arctic Ocean"].map((r) => (
                  <button
                    key={r}
                    className="quick-pill"
                    onClick={() => sendQuery(`Show temperature in ${r}`)}
                  >
                    {REGION_EMOJIS[r]} {r}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Loading placeholder */}
          {loading && !result && (
            <div className="glass loading-card">
              <div className="loading-state">
                <div className="spinner" />
                Analyzing query & fetching ocean data…
              </div>
            </div>
          )}

          {/* ── Parsed Query Badge ── */}
          {result && (
            <div className="parsed-badge glass" style={{ animation: "fadeInUp 0.3s ease" }}>
              <span className="parsed-label">Parsed as</span>
              <span className="parsed-chip">{REGION_EMOJIS[result.region]} {result.region}</span>
              <span className="parsed-chip">{result.parameter}</span>
              {result.parsed?.start_year && (
                <span className="parsed-chip">
                  {result.parsed.start_year} – {result.parsed.end_year}
                </span>
              )}
            </div>
          )}

          {/* ── Stats row ── */}
          {result?.stats && (
            <div className="stats-row" style={{ animation: "fadeInUp 0.35s ease" }}>
              {[
                { label: "Min",     value: result.stats.min,   unit: result.parameter === "temperature" ? "°C" : " PSU" },
                { label: "Max",     value: result.stats.max,   unit: result.parameter === "temperature" ? "°C" : " PSU" },
                { label: "Mean",    value: result.stats.mean,  unit: result.parameter === "temperature" ? "°C" : " PSU" },
                { label: "Records", value: result.stats.count, unit: "" },
              ].map(({ label, value, unit }) => (
                <div key={label} className="glass stat-card">
                  <div className="stat-value">{value}{unit}</div>
                  <div className="stat-label">{label}</div>
                </div>
              ))}

              {result.trend && (
                <div className={`glass stat-card trend-card ${result.trend.direction}`}>
                  <div className="stat-value">{trendIcon} {Math.abs(result.trend.per_year)}</div>
                  <div className="stat-label">
                    {result.parameter === "temperature" ? "°C" : " PSU"}/yr · {result.trend.direction}
                  </div>
                </div>
              )}
            </div>
          )}

          {risk && (
            <div className={`glass risk-card ${riskClass}`} style={{ animation: "fadeInUp 0.38s ease" }}>
              <div className="risk-header">
                <div className="risk-title">🌡 Marine Risk Index</div>
                <div className={`risk-level ${riskClass}`}>{risk.level}</div>
              </div>
              <div className="risk-score">
                <span className="risk-score-value">{risk.score}</span>
                <span className="risk-score-label">/ 7</span>
              </div>
              <div className="risk-factors">
                <span className={`risk-factor ${risk.factors?.temperature_anomaly ? "active" : ""}`}>
                  Temp anomaly +2
                </span>
                <span className={`risk-factor ${risk.factors?.rapid_warming ? "active" : ""}`}>
                  Rapid warming +3
                </span>
                <span className={`risk-factor ${risk.factors?.salinity_imbalance ? "active" : ""}`}>
                  Salinity imbalance +2
                </span>
              </div>
            </div>
          )}


          {/* ── Area Chart ── */}
          {result?.data?.length > 0 && (
            <div className="glass chart-card" style={{ animation: "fadeInUp 0.4s ease" }}>
              <div className="chart-header">
                <div>
                  <div className="chart-title">
                    {REGION_EMOJIS[result.region]} {result.region} —{" "}
                    {result.parameter === "temperature" ? "Temperature (°C)" : "Salinity (PSU)"}
                  </div>
                  <div className="chart-subtitle">
                    {result.start_year}–{result.end_year} · {result.stats.count.toLocaleString()} measurements
                    {result.prediction?.length > 0 && (
                      <>
                        <span style={{ color: "#a78bfa", marginLeft: 8 }}>
                          + {result.prediction.length}yr forecast
                        </span>
                        {result.prediction_accuracy?.r_squared != null && (
                          <span style={{ 
                            color: result.prediction_accuracy.confidence === "high" ? "#10b981" : 
                                   result.prediction_accuracy.confidence === "medium" ? "#f59e0b" : "#ef4444",
                            marginLeft: 8,
                            fontSize: "0.85rem"
                          }}>
                            (R²={result.prediction_accuracy.r_squared.toFixed(2)} · {result.prediction_accuracy.confidence} confidence)
                          </span>
                        )}
                      </>
                    )}
                  </div>
                </div>
                <div className="chart-badge">ARGO Floats</div>
              </div>

              <div className="chart-wrapper" style={{ width: '100%', height: '320px', minHeight: '320px', display: 'flex' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={chartData} margin={{ top: 6, right: 6, left: -12, bottom: 0 }}>
                    <defs>
                      <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="#00C2A8" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#00C2A8" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid stroke="rgba(0,194,168,0.07)" strokeDasharray="4 4" />
                    <XAxis
                      dataKey="label"
                      stroke="#4a6fa8"
                      tick={{ fill: "#8ab4c8", fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      stroke="#4a6fa8"
                      tick={{ fill: "#8ab4c8", fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip content={<CustomTooltip parameter={result.parameter} />} />
                    <ReferenceLine
                      y={result.stats.mean}
                      stroke="rgba(0,194,168,0.35)"
                      strokeDasharray="6 3"
                      label={{ value: "avg", fill: "#4a6fa8", fontSize: 11, position: "right" }}
                    />
                    <Area
                      type="monotone"
                      dataKey={result.parameter}
                      stroke="#00C2A8"
                      strokeWidth={2.5}
                      fill="url(#areaGrad)"
                      dot={{ fill: "#00C2A8", r: 4, strokeWidth: 0 }}
                      activeDot={{ r: 6, fill: "#4FD1C5", stroke: "#fff", strokeWidth: 2 }}
                      connectNulls={false}
                      name="Historical"
                    />
                    {result.prediction?.length > 0 && (
                      <Line
                        type="monotone"
                        dataKey="predicted"
                        stroke="#a78bfa"
                        strokeWidth={2}
                        strokeDasharray="6 4"
                        dot={{ fill: "#a78bfa", r: 3, strokeWidth: 0 }}
                        activeDot={{ r: 5, fill: "#c4b5fd", stroke: "#fff", strokeWidth: 2 }}
                        connectNulls={false}
                        name="Forecast"
                      />
                    )}
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* ── AI Insight Card ── */}
          {result?.insight && (
            <div className="glass insight-card" style={{ animation: "fadeInUp 0.45s ease" }}>
              <div className="insight-header">
                <div className="insight-title">🧠 AI Insight</div>
                <span className={`ai-badge ${result.insight.source}`}>
                  {result.insight.source === "llm" ? "⚡ LLaMA-3 70B" : "📋 Template"}
                </span>
              </div>
              <p className="insight-text">{result.insight.text}</p>
            </div>
          )}

          {/* ── Data Table ── */}
          {result?.data?.length > 0 && (
            <div className="glass table-card" style={{ animation: "fadeInUp 0.5s ease" }}>
              <div className="table-header">
                <div className="table-title">📋 Raw Data Records</div>
                <span className="record-count">showing {result.data.length} / {result.stats.count} records</span>
              </div>
              <div style={{ overflowX: "auto" }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Latitude</th>
                      <th>Longitude</th>
                      <th>Temperature (°C)</th>
                      <th>Salinity (PSU)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.data.map((row, i) => (
                      <tr key={i}>
                        <td>{row.date}</td>
                        <td>{row.latitude != null ? row.latitude.toFixed(2) : "—"}</td>
                        <td>{row.longitude != null ? row.longitude.toFixed(2) : "—"}</td>
                        <td className="temp-cell">{row.temperature != null ? row.temperature.toFixed(2) : "—"}</td>
                        <td className="sal-cell">{row.salinity != null ? row.salinity.toFixed(2) : "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* No results */}
          {result && result.data?.length === 0 && (
            <div className="glass" style={{ padding: "40px", textAlign: "center" }}>
              <div style={{ fontSize: "2.5rem", marginBottom: 12 }}>🔍</div>
              <div style={{ color: "var(--text-secondary)", fontWeight: 600 }}>No data found</div>
              <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginTop: 6 }}>
                {result.message || "Try adjusting your region or year range."}
              </div>
            </div>
          )}
        </section>
      </main>

      <footer className="footer">
        Built with <span>React</span> + <span>FastAPI</span> + <span>ARGO Float Data</span> · Velora AI © 2025
      </footer>

      {/* ── GLOBAL STATS MODAL ── */}
      {showStats && (
        <div className="modal-overlay" onClick={() => setShowStats(false)}>
          <div className="modal-content glass" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>🌎 Global Dataset Summary</h3>
              <button className="close-btn" onClick={() => setShowStats(false)}>×</button>
            </div>
            {!globalStats ? (
              <div className="modal-loading">
                <div className="mini-spinner"></div> Loading telemetry counts...
              </div>
            ) : (
              <div className="modal-body">
                <div className="total-badge">
                  <strong>{globalStats.total.toLocaleString()}</strong> Total Measurements
                </div>
                <div className="region-grid">
                  {Object.entries(globalStats.summary).map(([region, count]) => (
                    <div key={region} className="region-stat-item">
                      <span className="region-name">{REGION_EMOJIS[region]} {region}</span>
                      <span className="region-count">{count.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Mini helper to bold **text** in AI messages ──────────────────────────────
function FormattedText({ text }) {
  const parts = text.split(/\*\*(.*?)\*\*/g);
  return (
    <span>
      {parts.map((part, i) =>
        i % 2 === 1 ? <strong key={i} style={{ color: "var(--teal)" }}>{part}</strong> : part
      )}
    </span>
  );
}
