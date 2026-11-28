import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function AuditLog() {
  const [entries, setEntries] = useState([]);
  useEffect(() => { api.getAudit().then(setEntries).catch(() => {}); }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Audit Log</h2>
          <p className="page-desc">Timestamped log of all scheduler operations</p>
        </div>
      </div>

      <div className="card">
        {entries.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📝</div>
            <p>Audit log is empty</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Function</th>
                  <th>Summary</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((e, i) => (
                  <tr key={i}>
                    <td style={{ fontFamily: 'monospace', color: 'var(--accent)', fontWeight: 500 }}>
                      {e.time}
                    </td>
                    <td style={{ fontFamily: 'monospace', color: 'var(--accent-purple)' }}>
                      {e.function}
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>{e.summary}</td>
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
