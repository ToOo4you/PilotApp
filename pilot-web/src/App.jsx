
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
import { API_BASE_URL } from './lib/api';

function App() {
  const [page, setPage] = useState('Dashboard');
  const [companies, setCompanies] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [subscription, setSubscription] = useState(null);
  const [billingEmail, setBillingEmail] = useState('');

  // Check if returning from Stripe Checkout success redirect
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('subscribed') === 'true') {
      const plan = params.get('plan') || '';
      const email = params.get('email') || '';
      setBillingEmail(email);
      fetch(`${API_BASE_URL}/subscriptions/status?email=${encodeURIComponent(email)}`)
        .then((response) => response.json())
        .then((status) => setSubscription({ ...status, email, plan: status.plan || plan }))
        .catch(() => setSubscription({ subscribed: false, plan, status: 'pending', email }));
      // Clean up URL
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

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
      return <BillingSupport defaultEmail={billingEmail} />;
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

    if (page === 'Directors') {
      return <AIChat />;
    }

    if (page === 'Jax') {
      return <MaintenancePredictor />;
    }

    return <h1>Page not found</h1>;
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <h2>Pilot</h2>
        <button onClick={() => setPage('Dashboard')}>Dashboard</button>
        <button onClick={() => setPage('Companies')}>Companies</button>
        <button onClick={() => setPage('Customers')}>Customers</button>
        <button onClick={() => setPage('Trucks')}>Trucks</button>
        <button onClick={() => setPage('Drivers')}>Drivers</button>
        <button onClick={() => setPage('Jobs')}>Jobs</button>
        <button onClick={() => setPage('Dispatch')}>Dispatch</button>
        <button onClick={() => setPage('Operations')}>Operations</button>
        <button onClick={() => setPage('Directors')}>AI Directors</button>
        <button onClick={() => setPage('Jax')}>🚚 Operations Director</button>
        <div className="sidebar-divider" />
        <button className="sidebar-subscribe-btn" onClick={() => setPage('Subscribe')}>
          💳 Subscribe
        </button>
        <button onClick={() => setPage('Billing Support')}>Billing Support</button>
      </aside>

      <main className="main">{renderPage()}</main>
    </div>
  );
}

export default App;
