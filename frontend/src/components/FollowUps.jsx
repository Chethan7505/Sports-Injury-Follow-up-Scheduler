import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { useToast } from './Toast';

export default function FollowUps() {
  const [tab, setTab] = useState('upcoming');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const addToast = useToast();

  const load = async () => {
    setLoading(true);
    try {
      if (tab === 'upcoming')    setData(await api.getUpcoming());
      else if (tab === 'missed') setData(await api.getMissed());
      else if (tab === 'today')  setData(await api.getToday());
      else                       setData(await api.getAllFollowups());
    } catch (e) {
      addToast(e.message, 'error');
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, [tab]);

  const handleMarkDone = async (fid) => {
    try {
      const res = await api.markDone(fid);
      addToast(res.message, 'success');
      load();
    } catch (e) {
      addToast(e.message, 'error');
    }
  };

  const tabs = [
    { key: 'upcoming', label: 'Upcoming', icon: '📅' },
    { key: 'missed',   label: 'Missed',   icon: '⚠' },
    { key: 'today',    label: "Today's Queue", icon: '📋' },
    { key: 'all',      label: 'All',      icon: '📁' },
  ];

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Follow-ups</h2>
          <p className="page-desc">Track and manage scheduled appointments</p>
        </div>
      </div>

      {/* Tab bar */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        {tabs.map((t) => (
          <button
            key={t.key}
            className={`btn ${tab === t.key ? 'btn-primary' : ''}`}
            onClick={() => setTab(t.key)}
          >
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      <div className="card">
        {loading ? (
          <div className="empty-state"><p>Loading...</p></div>
        ) : data.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🎉</div>
            <p>No {tab} follow-ups</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>FID</th>
                  <th>Case</th>
                  <th>Patient</th>
                  <th>Sport</th>
                  <th>Injury</th>
                  <th>Severity</th>
                  <th>Due</th>
                  <th>Physio</th>
                  <th>Status</th>
                  <th>Tasks</th>
                  {(tab === 'upcoming' || tab === 'today') && <th>Action</th>}
                </tr>
              </thead>
              <tbody>
                {data.map((f) => (
                  <tr key={f.fid}>
                    <td style={{ color: 'var(--accent)', fontWeight: 600 }}>{f.fid}</td>
                    <td>{f.case_id}</td>
                    <td style={{ fontWeight: 500 }}>{f.name}</td>
                    <td style={{ textTransform: 'capitalize' }}>{f.sport}</td>
                    <td style={{ textTransform: 'capitalize' }}>{f.injury}</td>
                    <td>
                      <span className={`severity-badge severity-${f.severity}`}>{f.severity}</span>
                    </td>
                    <td>{f.due}</td>
                    <td>{f.physio}</td>
                    <td>
                      <span className={`badge badge-${f.status}`}>{f.status}</span>
                    </td>
                    <td>
                      <div className="task-chips">
                        {f.tasks.map((t) => <span key={t} className="task-chip">{t}</span>)}
                      </div>
                    </td>
                    {(tab === 'upcoming' || tab === 'today') && (
                      <td>
                        <button className="btn btn-sm btn-success" onClick={() => handleMarkDone(f.fid)}>
                          ✓ Done
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
