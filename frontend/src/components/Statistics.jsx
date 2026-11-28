import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function Statistics() {
  const [stats, setStats] = useState(null);
  useEffect(() => { api.getStats().then(setStats).catch(() => {}); }, []);

  if (!stats) return <div className="empty-state"><p>Loading...</p></div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Statistics</h2>
          <p className="page-desc">Follow-up analytics and injury distribution</p>
        </div>
      </div>

      {/* Overview */}
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
      </div>

      {/* Injury counts */}
      <div className="card">
        <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 20, color: 'var(--accent)' }}>
          Injury Distribution (by follow-up count)
        </h3>
        {stats.injury_counts.map(({ injury, count }) => {
          const maxCount = stats.injury_counts[0]?.count || 1;
          const pct = (count / maxCount) * 100;
          return (
            <div key={injury} style={{ marginBottom: 14 }}>
              <div className="flex-between" style={{ marginBottom: 6 }}>
                <span style={{ fontSize: 13, textTransform: 'capitalize', color: 'var(--text-secondary)' }}>{injury}</span>
                <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--accent)' }}>{count}</span>
              </div>
              <div style={{ height: 10, background: 'rgba(61,122,104,0.1)', borderRadius: 999, overflow: 'hidden' }}>
                <div
                  style={{
                    height: '100%',
                    width: `${pct}%`,
                    background: 'linear-gradient(90deg, var(--accent), var(--accent-green))',
                    borderRadius: 999,
                    transition: 'width 0.6s ease',
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Missed by physio */}
      {Object.keys(stats.missed_by_physio).length > 0 && (
        <div className="card">
          <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16, color: 'var(--accent-red)' }}>
            Missed Follow-ups by Physio
          </h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Physio</th>
                  <th>Missed Follow-up IDs</th>
                  <th>Count</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(stats.missed_by_physio).map(([physio, fids]) => (
                  <tr key={physio}>
                    <td style={{ fontWeight: 500 }}>{physio}</td>
                    <td>
                      <div className="task-chips">
                        {fids.map((f) => <span key={f} className="task-chip">{f}</span>)}
                      </div>
                    </td>
                    <td style={{ fontWeight: 600, color: 'var(--accent-red)' }}>{fids.length}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
