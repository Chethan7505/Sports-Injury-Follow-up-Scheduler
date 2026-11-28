// API helper - all requests to the Flask backend

const BASE = '/api';

async function request(url, options = {}) {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Request failed');
  return data;
}

export const api = {
  getConfig:      ()        => request('/config'),
  getCases:       ()        => request('/cases'),
  addCase:        (body)    => request('/cases',       { method: 'POST', body: JSON.stringify(body) }),
  getUpcoming:    ()        => request('/followups/upcoming'),
  getMissed:      ()        => request('/followups/missed'),
  getToday:       ()        => request('/followups/today'),
  getAllFollowups: ()       => request('/followups/all'),
  schedule:       (caseId)  => request('/schedule',    { method: 'POST', body: JSON.stringify({ case_id: caseId }) }),
  markDone:       (fid)     => request('/mark-done',   { method: 'POST', body: JSON.stringify({ fid }) }),
  autoReschedule: ()        => request('/auto-reschedule', { method: 'POST' }),
  setOverride:    (caseId, days) => request('/override', { method: 'POST', body: JSON.stringify({ case_id: caseId, interval_days: days }) }),
  getHistory:     (caseId)  => request(`/history/${caseId}`),
  getStats:       ()        => request('/stats'),
  getAudit:       ()        => request('/audit'),
  regenerate:     ()        => request('/regenerate',  { method: 'POST' }),
};
