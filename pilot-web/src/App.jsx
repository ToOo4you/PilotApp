
import React, { useState, useEffect } from 'react';
import './App.css';
import heroBg from './assets/hero.png';
import AIChat from './components/AIChat';
import RouteOptimizer from './components/RouteOptimizer';
import DispatchDashboard from './components/DispatchDashboard';
import DriverAnalytics from './components/DriverAnalytics';
import MaintenancePredictor from './components/MaintenancePredictor';
import OperationsCenter from './components/OperationsCenter';
import Pricing from './components/Pricing';
import BillingSupport from './components/BillingSupport';
import SubscriptionManager from './components/SubscriptionManager';
import DailyTripChecklists from './components/DailyTripChecklists';
import AIRecruiter from './components/AIRecruiter';
import AIAccountant from './components/AIAccountant';
import AILogisticsManager from './components/AILogisticsManager';
import { API_BASE_URL } from './lib/api';

function App() {
  const [page, setPage] = useState('Dashboard');
  const [companies, setCompanies] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [subscriberCustomers, setSubscriberCustomers] = useState([]);
  const [subscriberSummary, setSubscriberSummary] = useState('');
  const [subscriberLeads, setSubscriberLeads] = useState([]);
  const [leadStrategy, setLeadStrategy] = useState('');
  const [highRatedOnly, setHighRatedOnly] = useState(false);
  const [ratingThreshold, setRatingThreshold] = useState('0');
  const [subscribersLoading, setSubscribersLoading] = useState(false);
  const [subscription, setSubscription] = useState(null);
  const [billingVerificationError, setBillingVerificationError] = useState('');
  const [marketingMode, setMarketingMode] = useState(false);

  // Check if returning from Stripe Checkout success redirect
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const view = (params.get('view') || '').toLowerCase();

    if (view === 'landing') {
      setMarketingMode(true);
      setPage('Landing');
    } else if (view === 'subscribe') {
      setMarketingMode(true);
      setPage('Subscribe');
    } else if (view === 'billing-support') {
      setMarketingMode(true);
      setPage('Billing Support');
    }

    if (params.get('subscribed') === 'true') {
      const plan = params.get('plan') || '';
      const email = params.get('email') || '';
      fetch(`${API_BASE_URL}/subscriptions/status?email=${encodeURIComponent(email)}`)
        .then((response) => {
          if (!response.ok) throw new Error('Subscription status unavailable');
          return response.json();
        })
        .then((status) => {
          setBillingVerificationError('');
          setSubscription({ ...status, email, plan: status.plan || plan });
        })
        .catch((error) => {
          console.error('Subscription verification failed:', error);
          setBillingVerificationError('We could not verify your subscription access yet. Please try again or contact billing support.');
          setSubscription({ subscribed: false, plan, status: 'pending', email });
        });
      // Clean up URL
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  const minRating = Number(ratingThreshold);
  const passesThreshold = (rating) => Number(rating ?? 0) >= minRating;

  const visibleSubscriberCustomers = subscriberCustomers.filter((customer) => {
    const highRatedPass = !highRatedOnly || customer.high_rating;
    return highRatedPass && passesThreshold(customer.customer_rating);
  });

  const visibleSubscriberLeads = subscriberLeads.filter((lead) => {
    const highRatedPass = !highRatedOnly || lead.high_rating;
    return highRatedPass && passesThreshold(lead.customer_rating);
  });

  const fetchSubscriberCustomersAI = async () => {
    setSubscribersLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/customer-fetch-subscribers`);
      const data = await response.json();
      if (data.status === 'success') {
        setSubscriberCustomers(Array.isArray(data.subscriber_customers) ? data.subscriber_customers : []);
        setSubscriberSummary(data.ai_summary || '');
        setSubscriberLeads(Array.isArray(data.non_subscriber_leads) ? data.non_subscriber_leads : []);
        setLeadStrategy(data.lead_strategy || '');
      }
    } catch (error) {
      console.error('Subscriber fetch AI error:', error);
      setSubscriberSummary('Unable to fetch subscriber customers right now.');
      setSubscriberCustomers([]);
      setSubscriberLeads([]);
      setLeadStrategy('');
    } finally {
      setSubscribersLoading(false);
    }
  };

  const exportLeadCsv = () => {
    if (!subscriberLeads.length) {
      return;
    }

    const escapeCsv = (value) => {
      const safe = String(value ?? '').replace(/"/g, '""');
      return `"${safe}"`;
    };

    const headers = ['Name', 'Contact', 'Phone', 'Email', 'Conversion Score', 'Priority', 'Recommended Offer'];
    const rows = subscriberLeads.map((lead) => [
      lead.name,
      lead.contact,
      lead.phone,
      lead.email,
      lead.conversion_score,
      lead.priority,
      lead.recommended_offer,
    ]);

    const csv = [headers, ...rows]
      .map((row) => row.map(escapeCsv).join(','))
      .join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `highway-pilot-leads-${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const exportSubscriberCsv = () => {
    if (!subscriberCustomers.length) {
      return;
    }

    const escapeCsv = (value) => {
      const safe = String(value ?? '').replace(/"/g, '""');
      return `"${safe}"`;
    };

    const headers = ['Name', 'Contact', 'Phone', 'Email', 'Plan', 'Status', 'Customer Rating', 'High Rating'];
    const rows = subscriberCustomers.map((customer) => [
      customer.name,
      customer.contact,
      customer.phone,
      customer.email,
      customer.subscription?.plan,
      customer.subscription?.status,
      customer.customer_rating,
      customer.high_rating ? 'Yes' : 'No',
    ]);

    const csv = [headers, ...rows]
      .map((row) => row.map(escapeCsv).join(','))
      .join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `highway-pilot-subscribers-${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  useEffect(() => {
    fetch(`${API_BASE_URL}/customers/`)
      .then((response) => response.json())
      .then((data) => setCustomers(Array.isArray(data) ? data : []))
      .catch((error) => console.error(error));

    fetch(`${API_BASE_URL}/companies/`)
      .then((response) => response.json())
      .then((data) => setCompanies(Array.isArray(data) ? data : []))
      .catch((error) => console.error(error));
  }, []);

  const renderPage = () => {
    if (page === 'Landing') {
      return (
        <div className="wix-landing">
          <div className="wix-hero">
            <h1>Move Freight Faster With Highway Pilot AI</h1>
            <p>
              Automate dispatch, route planning, and driver operations from one AI-powered platform.
            </p>
            <div className="wix-hero-actions">
              <button
                className="wix-primary-btn"
                onClick={() => {
                  setMarketingMode(true);
                  setPage('Subscribe');
                }}
              >
                Start Paid Plan
              </button>
              <button
                className="wix-secondary-btn"
                onClick={() => {
                  setMarketingMode(false);
                  setPage('Dashboard');
                }}
              >
                View Product Dashboard
              </button>
            </div>
          </div>

          <div className="wix-proof-grid">
            <div className="wix-proof-card">
              <h3>AI Dispatching</h3>
              <p>Auto-assign jobs by location, rating, and capacity in real time.</p>
            </div>
            <div className="wix-proof-card">
              <h3>Route Optimization</h3>
              <p>Reduce miles, fuel spend, and late arrivals with dynamic route planning.</p>
            </div>
            <div className="wix-proof-card">
              <h3>Predictive Operations</h3>
              <p>Spot maintenance and retention risk before it impacts revenue.</p>
            </div>
          </div>

          <div className="wix-bottom-cta">
            <strong>Ready to turn your Wix traffic into paying subscribers?</strong>
            <button
              className="wix-primary-btn"
              onClick={() => {
                setMarketingMode(true);
                setPage('Subscribe');
              }}
            >
              Subscribe Now
            </button>
          </div>
        </div>
      );
    }

    if (page === 'Dashboard') {
      return (
        <>
          <div className="hero-banner" style={{ backgroundImage: `url(${heroBg})` }}>
            <div className="hero-overlay">
              <h1 className="hero-title">Highway Pilot AI</h1>
              <p className="hero-subtitle">AI-powered transportation operations — fully autonomous, always on</p>
            </div>
          </div>

          {subscription?.subscribed && (
            <div className="subscription-banner">
              ✅ Active subscription · <strong>{subscription.plan ? subscription.plan.charAt(0).toUpperCase() + subscription.plan.slice(1) : 'Plan'}</strong> plan
            </div>
          )}

          {billingVerificationError && (
            <div className="subscription-cta">
              <span>{billingVerificationError}</span>
              <button className="subscription-cta-btn" onClick={() => setPage('Billing Support')}>
                Billing Support
              </button>
            </div>
          )}

          {!subscription?.subscribed && (
            <div className="subscription-cta">
              <span>🚀 Ready to automate your operations?</span>
              <button className="subscription-cta-btn" onClick={() => setPage('Subscribe')}>
                Subscribe Now
              </button>
            </div>
          )}

          <div className="cards">
            <div className="card"><h3>Companies</h3><p>{companies.length}</p></div>
            <div className="card"><h3>Customers</h3><p>{customers.length}</p></div>
            <div className="card"><h3>AI Tools</h3><p>5</p></div>
            <div className="card"><h3>Status</h3><p>Live</p></div>
          </div>
        </>
      );
    }

    if (page === 'Subscribe') {
      return <Pricing onSubscribed={(sub) => { setSubscription(sub); setPage('Dashboard'); }} />;
    }

    if (page === 'Billing Support') {
      return <BillingSupport defaultEmail={subscription?.email || ''} />;
    }

    if (page === 'Companies') {
      return (
        <>
          <h1>Companies</h1>
          <p className="subtitle">Manage towing companies, trucking companies, and business accounts.</p>

          {companies.length === 0 ? (
            <p>No companies found yet.</p>
          ) : (
            companies.map((company) => (
              <div className="list-card" key={company.id || company.company_name}>
                <h3>{company.company_name || 'Unknown Company'}</h3>
                <p>Owner: {company.owner_name || 'N/A'}</p>
                <p>Phone: {company.phone || 'N/A'}</p>
                <p>Email: {company.email || 'N/A'}</p>
              </div>
            ))
          )}
        </>
      );
    }

    if (page === 'Customers') {
      return (
        <>
          <h1>Customers</h1>
          <p className="subtitle">Manage your customers and business accounts.</p>
          <div className="card"><h3>Total Customers</h3><p>{customers.length}</p></div>

          <div style={{ marginTop: '18px', marginBottom: '18px' }}>
            <button className="primary-button" onClick={fetchSubscriberCustomersAI} disabled={subscribersLoading}>
              {subscribersLoading ? 'Fetching...' : 'Fetch Subscriber Customers (AI)'}
            </button>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label>
              <input
                type="checkbox"
                checked={highRatedOnly}
                onChange={(event) => setHighRatedOnly(event.target.checked)}
                style={{ marginRight: '8px' }}
              />
              Show only high-rated customers
            </label>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ marginRight: '10px' }}>Minimum Rating:</label>
            <select value={ratingThreshold} onChange={(event) => setRatingThreshold(event.target.value)}>
              <option value="0">All</option>
              <option value="4.0">4.0+</option>
              <option value="4.5">4.5+</option>
              <option value="4.8">4.8+</option>
            </select>
          </div>

          {subscriberSummary && (
            <div className="list-card" style={{ marginBottom: '16px', maxWidth: '100%' }}>
              <h3>AI Revenue Summary</h3>
              <p>{subscriberSummary}</p>
            </div>
          )}

          {leadStrategy && (
            <div className="list-card" style={{ marginBottom: '16px', maxWidth: '100%' }}>
              <h3>AI Lead Strategy</h3>
              <p>{leadStrategy}</p>
            </div>
          )}

          {visibleSubscriberCustomers.length > 0 && (
            <>
              <h3>Subscriber Customers</h3>
              <div style={{ marginTop: '8px', marginBottom: '12px' }}>
                <button className="primary-button" onClick={exportSubscriberCsv}>
                  Export Subscribers CSV
                </button>
              </div>
              {visibleSubscriberCustomers.map((customer) => (
                <div className="list-card" key={`sub-${customer.id || customer.email}`}>
                  <h3>{customer.name || 'Customer'}</h3>
                  <p>Contact: {customer.contact || 'N/A'}</p>
                  <p>Email: {customer.email || 'N/A'}</p>
                  <p>Plan: {customer.subscription?.plan || 'N/A'}</p>
                  <p>Status: {customer.subscription?.status || 'N/A'}</p>
                  <p>Customer Rating: {customer.customer_rating ?? 'N/A'} / 5</p>
                  <p>High Rating: {customer.high_rating ? 'Yes' : 'No'}</p>
                </div>
              ))}
            </>
          )}

          {visibleSubscriberLeads.length > 0 && (
            <>
              <h3>Best Leads to Convert</h3>
              <div style={{ marginTop: '8px', marginBottom: '12px' }}>
                <button className="primary-button" onClick={exportLeadCsv}>
                  Export Leads CSV
                </button>
              </div>
              {visibleSubscriberLeads.map((lead) => (
                <div className="list-card" key={`lead-${lead.id || lead.email}`}>
                  <h3>{lead.name || 'Lead'}</h3>
                  <p>Contact: {lead.contact || 'N/A'}</p>
                  <p>Email: {lead.email || 'N/A'}</p>
                  <p>Customer Rating: {lead.customer_rating ?? 'N/A'} / 5</p>
                  <p>High Rating: {lead.high_rating ? 'Yes' : 'No'}</p>
                  <p>Conversion Score: {lead.conversion_score ?? 'N/A'}</p>
                  <p>Priority: {lead.priority || 'N/A'}</p>
                  <p>Recommended Offer: {lead.recommended_offer || 'N/A'}</p>
                </div>
              ))}
            </>
          )}
        </>
      );
    }

    if (page === 'Trucks') {
      return (
        <>
          <h1>Trucks</h1>
          <p className="subtitle">Manage your truck fleet.</p>
        </>
      );
    }

    if (page === 'Drivers') {
      return <DriverAnalytics />;
    }

    if (page === 'Jobs') {
      return <RouteOptimizer />;
    }

    if (page === 'Dispatch') {
      return <DispatchDashboard />;
    }

    if (page === 'Operations') {
      return <OperationsCenter />;
    }

    if (page === 'Daily Trips') {
      return <DailyTripChecklists />;
    }

    if (page === 'AI Recruiter') {
      return <AIRecruiter />;
    }

    if (page === 'AI Accountant') {
      return <AIAccountant />;
    }

    if (page === 'AI Logistics Manager') {
      return <AILogisticsManager />;
    }

    if (page === 'Directors') {
      return <AIChat />;
    }

    if (page === 'Jax') {
      return <MaintenancePredictor />;
    }

    if (page === 'Subscription') {
      return <SubscriptionManager />;
    }

    return <h1>Page not found</h1>;
  };

  return (
    <div className="app">
      {!marketingMode && (
        <aside className="sidebar">
        <div className="brand-head">
          <img src="/logo-mark.svg" alt="Highway Pilot" className="brand-mark" />
          <h2>Highway Pilot</h2>
        </div>
        <button onClick={() => setPage('Dashboard')}>Dashboard</button>
        <button onClick={() => setPage('Companies')}>Companies</button>
        <button onClick={() => setPage('Customers')}>Customers</button>
        <button onClick={() => setPage('Trucks')}>Trucks</button>
        <button onClick={() => setPage('Drivers')}>Drivers</button>
        <button onClick={() => setPage('Jobs')}>Jobs</button>
        <button onClick={() => setPage('Dispatch')}>Dispatch</button>
        <button onClick={() => setPage('Operations')}>Operations</button>
        <button onClick={() => setPage('Daily Trips')}>Daily Trips</button>
        <button onClick={() => setPage('AI Recruiter')}>AI Recruiter</button>
        <button onClick={() => setPage('AI Accountant')}>AI Accountant</button>
        <button onClick={() => setPage('AI Logistics Manager')}>AI Logistics Manager</button>
        <button onClick={() => setPage('Directors')}>AI Directors</button>
        <button onClick={() => setPage('Jax')}>🚚 Operations Director</button>
        <div className="sidebar-divider" />
        <button className="sidebar-subscribe-btn" onClick={() => setPage('Subscribe')}>
          💳 Subscribe
        </button>
        <button onClick={() => setPage('Billing Support')}>Billing Support</button>
        <button onClick={() => setPage('Subscription')}>Subscription</button>
        </aside>
      )}

      <main className="main">{renderPage()}</main>
    </div>
  );
}

export default App;
