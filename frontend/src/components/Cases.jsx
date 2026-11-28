import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { useToast } from './Toast';

export default function Cases({ onNavigate }) {
  const [cases, setCases] = useState([]);
  const [config, setConfig] = useState(null);
  const [showAdd, setShowAdd] = useState(false);
  const [showSchedule, setShowSchedule] = useState(null);
  const [showOverride, setShowOverride] = useState(null);
  const [showHistory, setShowHistory] = useState(null);
  const [historyData, setHistoryData] = useState(null);
  const [form, setForm] = useState({ name: '', age: '', sport: '', injury: '', severity: '', physio: '' });
  const [overrideDays, setOverrideDays] = useState(7);
  const addToast = useToast();

  const load = () => {
    api.getCases().then(setCases);
    api.getConfig().then(setConfig);
  };
  useEffect(load, []);

  const handleAdd = async () => {
    try {
      const res = await api.addCase(form);
      addToast(res.message, 'success');
      setShowAdd(false);
      setForm({ name: '', age: '', sport: '', injury: '', severity: '', physio: '' });
      load();
    } catch (e) {
      addToast(e.message, 'error');
    }
  };

  const handleSchedule = async (cid) => {
    try {
      const res = await api.schedule(cid);
      if (res.ok) {
        addToast(`Scheduled ${res.followup.fid} on ${res.followup.due}`, 'success');
      }
      setShowSchedule(null);
    } catch (e) {
      addToast(e.message, 'error');
    }
  };

  const handleOverride = async (cid) => {
    try {
      const res = await api.setOverride(cid, overrideDays);
      addToast(res.message, 'success');
      setShowOverride(null);
    } catch (e) {
      addToast(e.message, 'error');
    }
  };

  const handleHistory = async (cid) => {
    try {
      const res = await api.getHistory(cid);
      setHistoryData(res);
      setShowHistory(cid);
    } catch (e) {
      addToast(e.message, 'error');
    }
  };

  if (!config) return <div className="empty-state"><p>Loading...</p></div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Cases</h2>
          <p className="page-desc">Manage injury cases ({cases.length} total)</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAdd(true)}>
          + Add Case
        </button>
      </div>

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Age</th>
                <th>Sport</th>
                <th>Injury</th>
                <th>Severity</th>
                <th>Physio</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((c) => (
                <tr key={c.case_id}>
                  <td style={{ color: 'var(--accent)', fontWeight: 600 }}>{c.case_id}</td>
                  <td style={{ fontWeight: 500 }}>{c.name}</td>
                  <td>{c.age}</td>
                  <td style={{ textTransform: 'capitalize' }}>{c.sport}</td>
                  <td style={{ textTransform: 'capitalize' }}>{c.injury}</td>
                  <td><span className={`severity-badge severity-${c.severity}`}>{c.severity}</span></td>
                  <td>{c.physio}</td>
                  <td>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <button className="btn btn-sm btn-primary" onClick={() => handleSchedule(c.case_id)}>
                        📅 Schedule
                      </button>
                      <button className="btn btn-sm" onClick={() => { setShowOverride(c.case_id); setOverrideDays(7); }}>
                        ⚙ Override
                      </button>
                      <button className="btn btn-sm" onClick={() => handleHistory(c.case_id)}>
                        📜 History
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Case Modal */}
      {showAdd && (
        <div className="modal-overlay" onClick={() => setShowAdd(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>➕ Add New Case</h3>
            <div className="form-row">
              <div className="form-group">
                <label>Name</label>
                <input className="form-control" value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Patient name" />
              </div>
              <div className="form-group">
                <label>Age (10-60)</label>
                <input className="form-control" type="number" min="10" max="60" value={form.age}
                  onChange={(e) => setForm({ ...form, age: e.target.value })} />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Sport</label>
                <select className="form-control" value={form.sport}
                  onChange={(e) => setForm({ ...form, sport: e.target.value })}>
                  <option value="">Select sport</option>
                  {config.sports.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Injury</label>
                <select className="form-control" value={form.injury}
                  onChange={(e) => setForm({ ...form, injury: e.target.value })}>
                  <option value="">Select injury</option>
                  {config.injuries.map((i) => <option key={i} value={i}>{i}</option>)}
                </select>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Severity</label>
                <select className="form-control" value={form.severity}
                  onChange={(e) => setForm({ ...form, severity: e.target.value })}>
                  <option value="">Select severity</option>
                  {config.severities.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Physio</label>
                <select className="form-control" value={form.physio}
                  onChange={(e) => setForm({ ...form, physio: e.target.value })}>
                  <option value="">Select physio</option>
                  {config.physios.map((p) => <option key={p} value={p}>{p}</option>)}
                </select>
              </div>
            </div>
            <div className="modal-actions">
              <button className="btn" onClick={() => setShowAdd(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleAdd}>Create Case</button>
            </div>
          </div>
        </div>
      )}

      {/* Override Modal */}
      {showOverride && (
        <div className="modal-overlay" onClick={() => setShowOverride(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>⚙ Set Interval Override — {showOverride}</h3>
            <div className="form-group">
              <label>Custom Interval (days, 1-30)</label>
              <input className="form-control" type="number" min="1" max="30"
                value={overrideDays} onChange={(e) => setOverrideDays(Number(e.target.value))} />
            </div>
            <div className="modal-actions">
              <button className="btn" onClick={() => setShowOverride(null)}>Cancel</button>
              <button className="btn btn-primary" onClick={() => handleOverride(showOverride)}>Set Override</button>
            </div>
          </div>
        </div>
      )}

      {/* History Modal */}
      {showHistory && historyData && (
        <div className="modal-overlay" onClick={() => setShowHistory(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>📜 History — {showHistory}</h3>
            <div className="timeline">
              {historyData.events.map((ev) => (
                <div className="timeline-item" key={ev.seq}>
                  <span style={{ color: 'var(--text-muted)', fontSize: 11, marginRight: 8 }}>#{ev.seq}</span>
                  {ev.event}
                </div>
              ))}
            </div>
            <div className="modal-actions">
              <button className="btn" onClick={() => setShowHistory(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
