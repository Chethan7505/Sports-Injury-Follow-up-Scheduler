import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { useToast } from './Toast';

export default function Reschedule() {
  const [results, setResults] = useState(null);
  const [missed, setMissed] = useState([]);
  const [loading, setLoading] = useState(false);
  const addToast = useToast();

  const loadMissed = () => {
    api.getMissed().then(setMissed).catch(() => {});
  };
  useEffect(() => { loadMissed(); }, []);

  const handleReschedule = async () => {
    setLoading(true);
    try {
      const res = await api.autoReschedule();
      setResults(res);
      addToast(`Rescheduled ${res.count} follow-ups`, 'success');
      loadMissed();
    } catch (e) {
      addToast(e.message, 'error');
    }
    setLoading(false);
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Auto-Reschedule</h2>
          <p className="page-desc">Self-healing schedule: reschedule all missed follow-ups with rule explanations</p>
        </div>
        <button
          className="btn btn-danger"
          onClick={handleReschedule}
          disabled={loading || missed.length === 0}
        >
          {loading ? '⏳ Working...' : '⚡ Run Auto-Reschedule'}
        </button>
      </div>

      {/* Missed count */}
      <div className="stat-grid" style={{ marginBottom: 24 }}>
        <div className="stat-card">
          <div className="stat-value red">{missed.length}</div>
          <div className="stat-label">Missed Follow-ups</div>
        </div>
      </div>

      {/* Results */}
      {results && (
        <div className="card">
          <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16, color: 'var(--accent)' }}>
            🔄 Reschedule Results ({results.count} rebooked)
          </h3>
          {results.explanations.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">✅</div>
              <p>No follow-ups needed rescheduling</p>
            </div>
          ) : (
            results.explanations.map((block, i) => (
              <div key={i} className="explanation-block">{block}</div>
            ))
          )}
        </div>
      )}

      {!results && missed.length > 0 && (
        <div className="card">
          <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12, color: 'var(--accent-red)' }}>
            ⚠ Pending Missed Follow-ups
          </h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>FID</th>
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
                    <td style={{ textTransform: 'capitalize' }}>{f.sport}</td>
                    <td style={{ textTransform: 'capitalize' }}>{f.injury}</td>
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
    </div>
  );
}
