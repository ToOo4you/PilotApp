import React, { useState } from 'react';
import './AIRecruiter.css';
import { API_BASE_URL } from '../lib/api';

const AIRecruiter = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [plan, setPlan] = useState('');
  const [customerTargets, setCustomerTargets] = useState([]);
  const [companyTargets, setCompanyTargets] = useState([]);
  const [clientTargets, setClientTargets] = useState([]);

  const loadRecruitingInsights = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/recruiter-intelligence`);
      if (!response.ok) {
        throw new Error(`Request failed with ${response.status}`);
      }
      const data = await response.json();
      setPlan(data.recruiting_plan || '');
      setCustomerTargets(Array.isArray(data.customer_targets) ? data.customer_targets : []);
      setCompanyTargets(Array.isArray(data.company_targets) ? data.company_targets : []);
      setClientTargets(Array.isArray(data.client_targets) ? data.client_targets : []);
    } catch (fetchError) {
      console.error('Recruiter intelligence error:', fetchError);
      setError('Unable to load recruiter intelligence right now. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderTargets = (items, type) => {
    if (!items.length) {
      return <p className="placeholder">No targets yet. Run recruiter AI.</p>;
    }

    return items.slice(0, 8).map((item) => (
      <div key={`${type}-${item.id}-${item.email || item.company_name}`} className="recruit-card">
        <div className="recruit-head">
          <strong>{item.company_name || item.name || 'Prospect'}</strong>
          <span className={`priority ${item.priority || 'low'}`}>{item.priority || 'low'}</span>
        </div>
        {item.contact && <p>Contact: {item.contact}</p>}
        {item.owner_name && <p>Owner: {item.owner_name}</p>}
        <p>Email: {item.email || 'N/A'}</p>
        <p>Phone: {item.phone || 'N/A'}</p>
        <p>Fit Score: {item.fit_score ?? 'N/A'}</p>
        {item.recommended_pitch && <p className="pitch">Pitch: {item.recommended_pitch}</p>}
      </div>
    ));
  };

  return (
    <div className="ai-recruiter">
      <h2>AI Recruiter</h2>
      <p className="subtitle">
        Recruit and convert customers, companies, and clients using AI-ranked target lists.
      </p>

      <div className="recruiter-actions">
        <button className="primary-button" onClick={loadRecruitingInsights} disabled={loading}>
          {loading ? 'Analyzing...' : 'Run Recruiter AI'}
        </button>
        {error && <span className="error">{error}</span>}
      </div>

      {plan && (
        <div className="plan-card">
          <h3>Weekly Recruiting Plan</h3>
          <p>{plan}</p>
        </div>
      )}

      <div className="recruit-grid">
        <section className="recruit-column">
          <h3>Customer Targets</h3>
          {renderTargets(customerTargets, 'customer')}
        </section>

        <section className="recruit-column">
          <h3>Company Targets</h3>
          {renderTargets(companyTargets, 'company')}
        </section>

        <section className="recruit-column">
          <h3>Client Targets</h3>
          {renderTargets(clientTargets, 'client')}
        </section>
      </div>
    </div>
  );
};

export default AIRecruiter;
