import React, { useState, useEffect } from 'react';
import WebThreads from './components/WebThreads';
import Dashboard from './components/Dashboard';
import Cases from './components/Cases';
import FollowUps from './components/FollowUps';
import Reschedule from './components/Reschedule';
import Statistics from './components/Statistics';
import AuditLog from './components/AuditLog';
import { ToastProvider } from './components/Toast';
import { api } from './api';

const NAV = [
  { section: 'Overview' },
  { key: 'dashboard',  icon: '🏠', label: 'Dashboard' },
  { section: 'Management' },
  { key: 'cases',      icon: '🏥', label: 'Cases' },
  { key: 'followups',  icon: '📅', label: 'Follow-ups' },
  { key: 'reschedule', icon: '⚡', label: 'Auto-Reschedule' },
  { section: 'Analytics' },
  { key: 'stats',      icon: '📊', label: 'Statistics' },
  { key: 'audit',      icon: '📝', label: 'Audit Log' },
];

function Sidebar({ active, setActive, counts }) {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1>Ngrok</h1>
        <p className="subtitle">Caring Follow-up Studio</p>
      </div>
      <nav className="sidebar-nav">
        {NAV.map((item, i) => {
          if (item.section) {
            return <div key={i} className="nav-section-title">{item.section}</div>;
          }
          const badge = item.key === 'followups' && counts.missed > 0
            ? <span className="nav-badge danger">{counts.missed}</span>
            : item.key === 'dashboard' && counts.today > 0
            ? <span className="nav-badge">{counts.today}</span>
            : null;
          return (
            <div
              key={item.key}
              className={`nav-item ${active === item.key ? 'active' : ''}`}
              onClick={() => setActive(item.key)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
              {badge}
            </div>
          );
        })}
      </nav>
    </div>
  );
}

export default function App() {
  const [active, setActive] = useState('dashboard');
  const [counts, setCounts] = useState({ missed: 0, today: 0 });

  useEffect(() => {
    const loadCounts = async () => {
      try {
        const [missed, today] = await Promise.all([api.getMissed(), api.getToday()]);
        setCounts({ missed: missed.length, today: today.length });
      } catch {}
    };
    loadCounts();
    const interval = setInterval(loadCounts, 5000);
    return () => clearInterval(interval);
  }, []);

  const renderPage = () => {
    switch (active) {
      case 'dashboard':  return <Dashboard />;
      case 'cases':      return <Cases />;
      case 'followups':  return <FollowUps />;
      case 'reschedule': return <Reschedule />;
      case 'stats':      return <Statistics />;
      case 'audit':      return <AuditLog />;
      default:           return <Dashboard />;
    }
  };

  return (
    <ToastProvider>
      <div className="app-wrapper">
        {/* WebThreads animated background */}
        <div className="webthreads-bg">
          <div style={{ width: '100%', height: '100%', position: 'relative' }}>
            <WebThreads
              colors={["#c9b194", "#7db5a3"]}
              coreColor="#fff7eb"
              threadCount={5}
              spread={0.18}
              frequency={3.8}
            />
          </div>
        </div>

        {/* App UI */}
        <div className="app-content">
          <Sidebar active={active} setActive={setActive} counts={counts} />
          <main className="main-panel" key={active}>
            {renderPage()}
          </main>
        </div>
      </div>
    </ToastProvider>
  );
}
