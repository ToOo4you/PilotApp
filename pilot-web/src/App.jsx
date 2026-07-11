
import React, { useState, useEffect } from 'react';
import './App.css';
import AIChat from './components/AIChat';
import RouteOptimizer from './components/RouteOptimizer';
import DispatchDashboard from './components/DispatchDashboard';
import DriverAnalytics from './components/DriverAnalytics';
import MaintenancePredictor from './components/MaintenancePredictor';
import OperationsCenter from './components/OperationsCenter';

const resolveApiBaseUrl = () => {
  const envBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  if (envBaseUrl) {
    return envBaseUrl.replace(/\/$/, '');
  }

  if (typeof window !== 'undefined') {
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    if (isLocalhost) {
      return 'http://127.0.0.1:8000';
    }

    return window.location.origin.replace(/\/$/, '');
  }

  return 'http://127.0.0.1:8000';
};

const API_BASE_URL = resolveApiBaseUrl();

function App() {
  const [page, setPage] = useState('AI Dashboard');
const [companies, setCompanies] = useState([]);
const [customers, setCustomers] = useState([]);
useEffect(() => {
fetch(`${API_BASE_URL}/customers/`)
  .then((response) => response.json())
  .then((data) => setCustomers(data))
  .catch((error) => console.error(error));  
  fetch(`${API_BASE_URL}/companies/`)
    .then((response) => response.json())
  .then((data) => {
  console.log("Companies from API:", data);
  setCompanies(data);
})
    .catch((error) => console.error(error));
}, []);
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
        <button onClick={() => setPage("Jax")}>
       🚚 Operations Director
        </button>
      </aside>

      <main className="main">
        {page === 'Dashboard' && (
          <>
            <h1>Highway Pilot AI</h1>
            <p className="subtitle">
            AI-powered transportation operations platform
            </p>

            <div className="cards">
              <div className="card"><h3>Companies</h3><p>1</p></div>
              <div className="card"><h3>Drivers</h3><p>1</p></div>
              <div className="card"><h3>Jobs</h3><p>1</p></div>
              <div className="card"><h3>Revenue</h3><p>$175</p></div>
            </div>
          </>
        )}
{page === "Companies" && <Companies />}
{page === "Customers" && <Customers />}
{page === "Trucks" && <Trucks />}
{page === "Drivers" && <Drivers />}
{page === "Jobs" && <Jobs />}
{page === "Dispatch" && <Dispatch />}
{page === "Operations" && <OperationsCenter />}
{page === "Directors" && <Directors />}
{page === "Jax" && <Jax />}
      {page === 'Companies' && (
  <>
    <h1>Companies</h1>
    <p className="subtitle">Manage towing companies, trucking companies, and business accounts.</p>

    <button className="primary-button">+ Add Company</button>

    {companies.map((company) => (
      <div className="list-card" key={company.id}>
        <h3>{company.company_name}</h3>
        <p>Owner: {company.owner_name}</p>
        <p>Phone: {company.phone}</p>
        <p>Email: {company.email}</p>
        <p>Status: Active</p>
      </div>
    ))}
  </>
)}
{page === "Customers" && (
  <>
    <h1>Customers</h1>
    <p className="subtitle">Manage customers</p>
  </>
)}

{page === "Trucks" && (
  <>
    <h1>Trucks</h1>
    <p className="subtitle">Manage fleet</p>
  </>
)}

{page === "Drivers" && (
  <>
    <h1>Drivers</h1>
    <p className="subtitle">Manage drivers</p>
  </>
)}

{page === "Jobs" && (
  <>
    <h1>Jobs</h1>
    <p className="subtitle">Manage towing jobs</p>
  </>
)}

{page === "Dispatch" && (
  <>
    <h1>Dispatch</h1>
    <p className="subtitle">Live dispatch center</p>
  </>
)}

{page === "Directors" && (
  <>
    <h1>AI Directors</h1>
    <p className="subtitle">AI management team</p>
  </>
)}

{page === "Jax" && (
  <>
    <h1>Jax</h1>
    <p className="subtitle">Operations Director</p>
  </>
)}
      {page === 'Customers' && (
  <>
    <h1>Customers</h1>
    <p className="subtitle">
      Manage your customers and business accounts.
    </p>

    <div className="card">
      <h3>ABC Logistics</h3>
      <p>Contact: John Smith</p>
      <p>Phone: (555) 123-4567</p>
      <p>Email: dispatch@abclogistics.com</p>
    </div>
  </>
)}
      {page === 'Trucks' && (
  <>
    <h1>Trucks</h1>
    <p className="subtitle">Manage your truck fleet.</p>

    <div className="card">
      <h3>T-101</h3>
      <p>Make: Peterbilt</p>
      <p>Model: 579</p>
      <p>Year: 2023</p>
      <p>Status: Available</p>
    </div>
  </>
)}
        {page === "Jax" && (
            <Jax />
        )}
        {page === 'Drivers' && <Drivers />}
        {page === 'Jobs' && <h1>Jobs Page</h1>}
        {page === 'Dispatch' && <h1>Dispatch Board</h1>}
        {page === 'Directors' && (
        <Directors onSelect={setPage} />
        )}

      </main>
    </div>
  );
}

export default App;