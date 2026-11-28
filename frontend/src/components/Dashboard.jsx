import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { useToast } from './Toast';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [missed, setMissed] = useState([]);
  const [upcoming, setUpcoming] = useState([]);
  const [today, setToday] = useState([]);
  const addToast = useToast();

  const load = () => {
    api.getStats().then(setStats).catch(() => {});
    api.getMissed().then(setMissed).catch(() => {});
    api.getUpcoming().then(setUpcoming).catch(() => {});
    api.getToday().then(setToday).catch(() => {});
  };

  useEffect(load, []);

  const handleReschedule = async () => {
    try {
      const res = await api.autoReschedule();
      addToast(`Rescheduled ${res.count} follow-ups`, 'success');
      load();
    } catch (e) {
      addToast(e.message, 'error');
    }
  };

  const handleRegenerate = async () => {
    try {
      const res = await api.regenerate();
      addToast(res.message, 'success');
      load();
    } catch (e) {
      addToast(e.message, 'error');
    }
  };

  if (!stats) return <div className="empty-state"><p>Loading...</p></div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Dashboard</h2>
          <p className="page-desc">Sports Injury Follow-up Overview</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-danger" onClick={handleReschedule}>
            ⚡ Auto-Reschedule
          </button>
          <button className="btn" onClick={handleRegenerate}>
            🔄 Regenerate Data
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value cyan">{stats.upcoming}</div>
          <div className="stat-label">Upcoming</div>
        </div>
        <div className="stat-card">
          <div className="stat-value red">{stats.missed}</div>
          <div className="stat-label">Missed</div>
        </div>
        <div className="stat-card">
          <div className="stat-value green">{stats.done}</div>
          <div className="stat-label">Done</div>
        </div>
        <div className="stat-card">
          <div className="stat-value orange">{today.length}</div>
          <div className="stat-label">Today's Queue</div>
        </div>
      </div>

      {/* Today's Queue */}
      {today.length > 0 && (
        <div className="card">
          <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12, color: 'var(--accent-orange)' }}>
            📋 Today's Queue
          </h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Patient</th>
                  <th>Sport</th>
                  <th>Injury</th>
                  <th>Physio</th>
                  <th>Tasks</th>
                </tr>
              </thead>
              <tbody>
                {today.map((f) => (
                  <tr key={f.fid}>
                    <td style={{ color: 'var(--accent)', fontWeight: 600 }}>{f.fid}</td>
                    <td>{f.name}</td>
                    <td>{f.sport}</td>
                    <td>{f.injury}</td>
                    <td>{f.physio}</td>
                    <td>
                      <div className="task-chips">
                        {f.tasks.map((t) => <span key={t} className="task-chip">{t}</span>)}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Missed */}
      {missed.length > 0 && (
        <div className="card">
          <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12, color: 'var(--accent-red)' }}>
            ⚠ Missed Follow-ups ({missed.length})
          </h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Patient</th>
                  <th>Sport</th>
                  <th>Injury</th>
                  <th>Severity</th>
                  <th>Due</th>
                  <th>Physio</th>
                </tr>
              </thead>
              <tbody>
                {missed.map((f) => (
                  <tr key={f.fid}>
                    <td style={{ color: 'var(--accent-red)', fontWeight: 600 }}>{f.fid}</td>
                    <td>{f.name}</td>
                    <td>{f.sport}</td>
                    <td>{f.injury}</td>
                    <td><span className={`severity-badge severity-${f.severity}`}>{f.severity}</span></td>
                    <td>{f.due}</td>
                    <td>{f.physio}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Injury distribution */}
      {stats.injury_counts.length > 0 && (
        <div className="card">
          <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16, color: 'var(--accent)' }}>
            📊 Injury Distribution
          </h3>
          {stats.injury_counts.map(({ injury, count }) => {
            const maxCount = stats.injury_counts[0].count;
            const pct = (count / maxCount) * 100;
            return (
              <div key={injury} style={{ marginBottom: 10 }}>
                <div className="flex-between mb-8">
                  <span style={{ fontSize: 13, color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{injury}</span>
                  <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--accent)' }}>{count}</span>
                </div>
                <div style={{ height: 8, background: 'rgba(61,122,104,0.1)', borderRadius: 999, overflow: 'hidden' }}>
                  <div
                    style={{
                      height: '100%',
                      width: `${pct}%`,
                      background: 'linear-gradient(90deg, var(--accent), var(--accent-green))',
                      borderRadius: 999,
                      transition: 'width 0.5s ease',
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
