
import React, { useState, useEffect } from 'react';
import './App.css';
import AIChat from './components/AIChat';
import RouteOptimizer from './components/RouteOptimizer';
import DispatchDashboard from './components/DispatchDashboard';
import DriverAnalytics from './components/DriverAnalytics';
import MaintenancePredictor from './components/MaintenancePredictor';
import OperationsCenter from './components/OperationsCenter';
import { API_BASE_URL } from './lib/api';

function App() {
  const [page, setPage] = useState('Dashboard');
  const [companies, setCompanies] = useState([]);
  const [customers, setCustomers] = useState([]);

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
          <h1>Highway Pilot AI</h1>
          <p className="subtitle">AI-powered transportation operations platform</p>

          <div className="cards">
            <div className="card"><h3>Companies</h3><p>{companies.length}</p></div>
            <div className="card"><h3>Customers</h3><p>{customers.length}</p></div>
            <div className="card"><h3>AI Tools</h3><p>5</p></div>
            <div className="card"><h3>Status</h3><p>Live</p></div>
          </div>
        </>
      );
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
      </aside>

      <main className="main">{renderPage()}</main>
    </div>
  );
}

export default App;