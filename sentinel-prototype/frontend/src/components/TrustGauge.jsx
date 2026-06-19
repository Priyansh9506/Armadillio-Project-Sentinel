import { useEffect } from 'react';

/**
 * Trust Score Gauge — Animated SVG circle that reflects real-time trust.
 * Color transitions: Green (>85) → Yellow (55-85) → Red (<55)
 */
export default function TrustGauge({ score = 100, subScores = {} }) {
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const getColor = (val) => {
    if (val > 85) return 'var(--trust-green)';
    if (val > 55) return 'var(--trust-yellow)';
    return 'var(--trust-red)';
  };

  const getGlow = (val) => {
    if (val > 85) return 'var(--shadow-glow-green)';
    if (val > 55) return '0 0 40px rgba(255, 184, 0, 0.15)';
    return '0 0 40px rgba(255, 59, 92, 0.2)';
  };

  const getLabel = (val) => {
    if (val > 85) return 'TRUSTED';
    if (val > 55) return 'CAUTION';
    return 'BLOCKED';
  };

  const subScoreEntries = [
    { key: 'behavioral', label: 'Behavioral' },
    { key: 'device', label: 'Device' },
    { key: 'session', label: 'Session' },
    { key: 'graph', label: 'Graph' },
    { key: 'transaction', label: 'Transaction' },
    { key: 'geo_velocity', label: 'Geo' },
  ];

  return (
    <div className="glass-card p-6" style={{ textAlign: 'center' }}>
      {/* Main Gauge */}
      <div className="trust-gauge" style={{ margin: '0 auto 20px', boxShadow: getGlow(score) }}>
        <svg width="200" height="200" viewBox="0 0 200 200">
          <circle
            className="trust-gauge-circle-bg"
            cx="100" cy="100" r={radius}
          />
          <circle
            className="trust-gauge-circle"
            cx="100" cy="100" r={radius}
            stroke={getColor(score)}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="trust-gauge-value">
          <div className="trust-gauge-number" style={{ color: getColor(score) }}>
            {Math.round(score)}
          </div>
          <div className="trust-gauge-label">{getLabel(score)}</div>
        </div>
      </div>

      <h3 style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: 16, color: 'var(--text-secondary)' }}>
        Trust Score Breakdown
      </h3>

      {/* Sub-Score Bars */}
      {subScoreEntries.map(({ key, label }) => {
        const val = subScores[key] ?? 100;
        return (
          <div className="sub-score-bar" key={key}>
            <span className="label">{label}</span>
            <div className="bar-track">
              <div
                className="bar-fill"
                style={{
                  width: `${val}%`,
                  background: getColor(val),
                }}
              />
            </div>
            <span className="value" style={{ color: getColor(val) }}>{Math.round(val)}</span>
          </div>
        );
      })}
    </div>
  );
}
