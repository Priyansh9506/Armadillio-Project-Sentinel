import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { socAPI } from '../api';

export default function SOC() {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  
  const graphContainer = useRef(null);
  const networkRef = useRef(null);

  const fetchData = async () => {
    try {
      const [alertsRes, sessionsRes, statsRes] = await Promise.all([
        socAPI.getAlerts(),
        socAPI.getSessions(),
        socAPI.getStats(),
      ]);
      setAlerts(alertsRes.data);
      setSessions(sessionsRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('SOC data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const drawGraph = async () => {
    try {
      const res = await socAPI.getFraudGraph();
      if (graphContainer.current && window.vis) {
        const data = {
          nodes: new window.vis.DataSet(res.data.nodes),
          edges: new window.vis.DataSet(res.data.edges)
        };
        const options = {
          nodes: {
            shape: 'dot',
            size: 20,
            font: { size: 13, color: '#FFFFFF', face: 'Inter, sans-serif', strokeWidth: 2, strokeColor: '#0a0e1a' },
            borderWidth: 3,
            shadow: { enabled: true, color: 'rgba(0,0,0,0.4)', size: 8 },
          },
          edges: {
            width: 2.5,
            font: { align: 'middle', size: 10, color: '#8892A8', face: 'Inter, sans-serif' },
            arrows: { to: { enabled: true, scaleFactor: 0.6 } },
            smooth: { type: 'curvedCW', roundness: 0.15 },
            shadow: { enabled: true, color: 'rgba(0,0,0,0.2)', size: 4 },
          },
          groups: {
            user: { color: { background: '#00D4AA', border: '#00A887' }, shape: 'dot', size: 22 },
            flagged_user: { color: { background: '#FF3B5C', border: '#D92A47' }, shape: 'dot', size: 24 },
            device: { color: { background: '#FFB800', border: '#CC9300' }, shape: 'diamond', size: 18 },
            ip: { color: { background: '#3B82F6', border: '#2563EB' }, shape: 'triangle', size: 16 },
            flagged_ip: { color: { background: '#FF6B35', border: '#D95A2A' }, shape: 'triangle', size: 18 },
            account: { color: { background: '#8B5CF6', border: '#7C3AED' }, shape: 'square', size: 18 },
            transaction: { color: { background: '#F59E0B', border: '#D97706' }, shape: 'star', size: 16 },
            unknown: { color: { background: '#6B7280', border: '#4B5563' }, shape: 'dot', size: 14 },
          },
          physics: {
            forceAtlas2Based: { gravitationalConstant: -80, centralGravity: 0.008, springLength: 140, springConstant: 0.06 },
            minVelocity: 0.75,
            solver: 'forceAtlas2Based',
            stabilization: { iterations: 150 },
          },
          interaction: { hover: true, tooltipDelay: 100 },
        };
        networkRef.current = new window.vis.Network(graphContainer.current, data, options);
      }
    } catch (err) {
      console.error('Failed to load fraud graph:', err);
    }
  };

  useEffect(() => {
    fetchData();
    drawGraph();
    const interval = setInterval(fetchData, 5000); // Auto-refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const getSeverityClass = (severity) => {
    if (!severity) return 'low';
    return severity.toLowerCase();
  };

  const statCards = [
    { label: 'Active Sessions', value: stats.active_sessions || 0, color: 'var(--trust-green)' },
    { label: 'Open Alerts', value: stats.total_alerts || 0, color: 'var(--trust-yellow)' },
    { label: 'Critical Alerts', value: stats.critical_alerts || 0, color: 'var(--trust-red)' },
    { label: 'Duress Transfers', value: stats.duress_transfers || 0, color: 'var(--trust-red)' },
  ];

  return (
    <div className="page">
      {/* Header */}
      <header className="header">
        <div className="header-logo">
          <img src="/bob-logo.png" alt="Bank of Baroda" style={{ height: 28, marginRight: 8, objectFit: 'contain' }} />
          <div style={{ width: 1, height: 20, background: 'var(--border-subtle)', marginRight: 8 }} />
          <img src="/armadillo-logo.png" alt="Armadillo" style={{ height: 28, marginRight: 16, objectFit: 'contain' }} />
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <h1 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--brand-navy)', lineHeight: 1.2, margin: 0 }}>
              Bank of Baroda SOC
            </h1>
            <span style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
              Security Operations Center
            </span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div style={{
            width: 8, height: 8, borderRadius: '50%',
            background: 'var(--trust-green)',
            boxShadow: '0 0 8px var(--trust-green)',
            animation: 'pulse 2s infinite',
          }} />
          <span className="text-muted" style={{ fontSize: '0.8rem' }}>Live Monitoring</span>
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/dashboard')}>
            Dashboard
          </button>
          <button className="btn btn-ghost btn-sm" onClick={async () => { 
            const sessionId = localStorage.getItem('sentinel_session');
            if (sessionId) {
              try {
                await fetch('http://localhost:8000/api/auth/logout', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('sentinel_token')}`
                  },
                  body: JSON.stringify({ session_id: sessionId })
                });
              } catch (err) {}
            }
            localStorage.clear(); 
            navigate('/'); 
          }}>
            Logout
          </button>
        </div>
      </header>

      <div style={{ padding: '24px 32px' }}>
        {/* Stats Row */}
        <div className="flex gap-4 mb-4" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)' }}>
          {statCards.map((s, i) => (
            <div className="glass-card p-4 text-center" key={i}>
              <div className="text-muted" style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                {s.label}
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: s.color, marginTop: 4 }}>
                {s.value}
              </div>
            </div>
          ))}
        </div>

        {/* Two Column Layout */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          {/* Alerts Feed */}
          <div className="glass-card p-6">
            <h3 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 16, color: 'var(--text-secondary)' }}>
              Security Alerts Feed
            </h3>
            {alerts.length === 0 ? (
              <p className="text-muted" style={{ fontSize: '0.85rem', textAlign: 'center', padding: '40px 0' }}>
                No alerts. System nominal.
              </p>
            ) : (
              <div style={{ maxHeight: 500, overflowY: 'auto' }}>
                {alerts.map((alert, i) => (
                  <div className={`alert-card ${getSeverityClass(alert.severity)}`} key={alert.id || i}
                    style={{ animation: `slideIn 0.3s ease-out ${i * 0.05}s both` }}>
                    <div className={`alert-dot ${getSeverityClass(alert.severity)}`} />
                    <div style={{ flex: 1 }}>
                      <div className="flex justify-between items-center">
                        <span style={{
                          fontSize: '0.7rem', fontWeight: 700,
                          textTransform: 'uppercase',
                          color: alert.severity === 'CRITICAL' ? 'var(--trust-red)' :
                            alert.severity === 'HIGH' ? 'var(--trust-yellow)' : 'var(--text-muted)',
                        }}>
                          {alert.severity} &bull; {alert.alert_type}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.85rem', marginTop: 4, color: 'var(--text-primary)' }}>
                        {alert.description}
                      </p>
                      <p className="text-muted" style={{ fontSize: '0.7rem', marginTop: 4 }}>
                        User: {alert.username || 'Unknown'} &bull; {alert.timestamp}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Active Sessions Monitor */}
          <div className="glass-card p-6">
            <h3 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 16, color: 'var(--text-secondary)' }}>
              Active Sessions Monitor
            </h3>
            {sessions.length === 0 ? (
              <p className="text-muted" style={{ fontSize: '0.85rem', textAlign: 'center', padding: '40px 0' }}>
                No active sessions.
              </p>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                      {['User', 'Trust', 'Decision', 'IP', 'Started'].map(h => (
                        <th key={h} style={{
                          textAlign: 'left', padding: '10px 12px',
                          fontSize: '0.7rem', textTransform: 'uppercase',
                          letterSpacing: '0.1em', color: 'var(--text-muted)',
                        }}>
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {sessions.map((s, i) => (
                      <tr key={s.session_id || i} style={{
                        borderBottom: '1px solid var(--border-subtle)',
                        animation: `slideIn 0.3s ease-out ${i * 0.05}s both`,
                      }}>
                        <td style={{ padding: '12px', fontSize: '0.85rem', fontWeight: 500 }}>
                          {s.username || 'Unknown'}
                        </td>
                        <td style={{ padding: '12px' }}>
                          <span style={{
                            fontWeight: 700, fontSize: '0.9rem',
                            fontFamily: "'JetBrains Mono', monospace",
                            color: (s.latest_trust_score || 100) > 85 ? 'var(--trust-green)' :
                              (s.latest_trust_score || 100) > 55 ? 'var(--trust-yellow)' : 'var(--trust-red)',
                          }}>
                            {Math.round(s.latest_trust_score || 100)}
                          </span>
                        </td>
                        <td style={{ padding: '12px' }}>
                          <span style={{
                            padding: '3px 10px', borderRadius: 'var(--radius-full)',
                            fontSize: '0.7rem', fontWeight: 600,
                            background: (s.latest_decision || 'ALLOW') === 'ALLOW'
                              ? 'rgba(0, 212, 170, 0.1)' : 'rgba(255, 59, 92, 0.1)',
                            color: (s.latest_decision || 'ALLOW') === 'ALLOW'
                              ? 'var(--trust-green)' : 'var(--trust-red)',
                          }}>
                            {s.latest_decision || 'ALLOW'}
                          </span>
                        </td>
                        <td className="text-muted font-mono" style={{ padding: '12px', fontSize: '0.8rem' }}>
                          {s.ip_address || '127.0.0.1'}
                        </td>
                        <td className="text-muted" style={{ padding: '12px', fontSize: '0.8rem' }}>
                          {s.start_time}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        <div className="glass-card p-6 mt-4">
          <h3 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 16, color: 'var(--text-secondary)' }}>
            Fraud Ring Graph (Neo4j)
          </h3>
          <div 
            id="neo4j-graph-container"
            ref={graphContainer}
            style={{
              height: 400,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: 'var(--bg-deepest)',
              borderRadius: 'var(--radius-md)',
              border: '1px dashed var(--border-subtle)',
            }}>
          </div>
        </div>
      </div>
    </div>
  );
}
