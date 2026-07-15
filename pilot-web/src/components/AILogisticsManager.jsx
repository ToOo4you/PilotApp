import React, { useState } from 'react';
import './AILogisticsManager.css';
import { API_BASE_URL } from '../lib/api';

const AILogisticsManager = () => {
  const [companyId, setCompanyId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [summary, setSummary] = useState(null);
  const [actionPlan, setActionPlan] = useState('');

  const runManager = async () => {
    setLoading(true);
    setError('');
    try {
      const query = companyId ? `?company_id=${encodeURIComponent(companyId)}` : '';
      const response = await fetch(`${API_BASE_URL}/api/ai/logistics-manager${query}`);
      if (!response.ok) {
        throw new Error(`Request failed with ${response.status}`);
      }

      const data = await response.json();
      setSummary(data.summary || null);
      setActionPlan(data.action_plan || '');
    } catch (managerError) {
      console.error('AI logistics manager error:', managerError);
      setError('Unable to run AI logistics manager right now. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-logistics-manager">
      <h2>AI Logistics Manager</h2>
      <p className="subtitle">
        Monitor dispatch load, completion rate, and driver utilization with AI operations priorities.
      </p>

      <div className="manager-actions">
        <input
          type="number"
          placeholder="Optional company ID"
          value={companyId}
          onChange={(event) => setCompanyId(event.target.value)}
        />
        <button className="primary-button" onClick={runManager} disabled={loading}>
          {loading ? 'Analyzing...' : 'Run Logistics Manager'}
        </button>
      </div>

      {error && <p className="manager-error">{error}</p>}

      {summary && (
        <div className="manager-grid">
          <div className="manager-metric">
            <h4>Total Jobs</h4>
            <p>{summary.total_jobs}</p>
          </div>
          <div className="manager-metric">
            <h4>Completed Jobs</h4>
            <p>{summary.completed_jobs}</p>
          </div>
          <div className="manager-metric">
            <h4>Waiting Jobs</h4>
            <p>{summary.waiting_jobs}</p>
          </div>
          <div className="manager-metric">
            <h4>In-Flight Jobs</h4>
            <p>{summary.active_jobs}</p>
          </div>
          <div className="manager-metric">
            <h4>Active Drivers</h4>
            <p>{summary.active_drivers}</p>
          </div>
          <div className="manager-metric">
            <h4>Completion Rate</h4>
            <p>{summary.completion_rate}%</p>
          </div>
          <div className="manager-metric">
            <h4>Backlog Pressure</h4>
            <p>{summary.backlog_pressure}</p>
          </div>
        </div>
      )}

      {actionPlan && (
        <div className="manager-plan">
          <h3>AI Operations Priorities</h3>
          <p>{actionPlan}</p>
        </div>
      )}
    </div>
  );
};

export default AILogisticsManager;
