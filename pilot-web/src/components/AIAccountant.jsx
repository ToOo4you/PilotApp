import React, { useState } from 'react';
import './AIAccountant.css';
import { API_BASE_URL } from '../lib/api';

const formatCurrency = (value) => {
  const numeric = Number(value || 0);
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(numeric);
};

const AIAccountant = () => {
  const [companyId, setCompanyId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [summary, setSummary] = useState(null);
  const [recommendations, setRecommendations] = useState('');

  const runAnalysis = async () => {
    setLoading(true);
    setError('');
    try {
      const query = companyId ? `?company_id=${encodeURIComponent(companyId)}` : '';
      const response = await fetch(`${API_BASE_URL}/api/ai/accountant-summary${query}`);
      if (!response.ok) {
        throw new Error(`Request failed with ${response.status}`);
      }
      const data = await response.json();
      setSummary(data.summary || null);
      setRecommendations(data.recommendations || '');
    } catch (analysisError) {
      console.error('AI accountant error:', analysisError);
      setError('Unable to fetch accountant insights right now. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-accountant">
      <h2>AI Accountant</h2>
      <p className="subtitle">
        Track revenue, pending cash flow, utilization, and AI recommendations for healthier operations.
      </p>

      <div className="accountant-actions">
        <input
          type="number"
          placeholder="Optional company ID"
          value={companyId}
          onChange={(event) => setCompanyId(event.target.value)}
        />
        <button className="primary-button" onClick={runAnalysis} disabled={loading}>
          {loading ? 'Analyzing...' : 'Run AI Accountant'}
        </button>
      </div>

      {error && <p className="accountant-error">{error}</p>}

      {summary && (
        <div className="accountant-grid">
          <div className="metric-card">
            <h4>Total Revenue</h4>
            <p>{formatCurrency(summary.total_revenue)}</p>
          </div>
          <div className="metric-card">
            <h4>Pending Revenue</h4>
            <p>{formatCurrency(summary.pending_revenue)}</p>
          </div>
          <div className="metric-card">
            <h4>Completed Jobs</h4>
            <p>{summary.completed_jobs}</p>
          </div>
          <div className="metric-card">
            <h4>Pending Jobs</h4>
            <p>{summary.pending_jobs}</p>
          </div>
          <div className="metric-card">
            <h4>Average Job Value</h4>
            <p>{formatCurrency(summary.average_job_value)}</p>
          </div>
          <div className="metric-card">
            <h4>Utilization Ratio</h4>
            <p>{Math.round((summary.utilization_ratio || 0) * 100)}%</p>
          </div>
        </div>
      )}

      {summary?.subscription_status_counts && (
        <div className="status-card">
          <h3>Subscription Status Mix</h3>
          <div className="status-list">
            {Object.entries(summary.subscription_status_counts).map(([status, count]) => (
              <div key={status} className="status-item">
                <span>{status}</span>
                <strong>{count}</strong>
              </div>
            ))}
          </div>
        </div>
      )}

      {recommendations && (
        <div className="recommendations-card">
          <h3>AI Accounting Recommendations</h3>
          <p>{recommendations}</p>
        </div>
      )}
    </div>
  );
};

export default AIAccountant;
