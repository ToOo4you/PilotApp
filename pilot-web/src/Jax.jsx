import { useEffect, useState } from "react";
import { API_BASE_URL } from './lib/api';

const askJax = async (task) => {
  const response = await fetch(`${API_BASE_URL}/jax/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ task }),
  });

  const data = await response.json();
  alert(data.message);
};

export default function Jax() {
  const [drivers, setDrivers] = useState([]);
  const [trucks, setTrucks] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [customers, setCustomers] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE_URL}/drivers/`)
      .then((res) => res.json())
      .then(setDrivers);

    fetch(`${API_BASE_URL}/trucks/`)
      .then((res) => res.json())
      .then(setTrucks);

    fetch(`${API_BASE_URL}/companies/`)
      .then((res) => res.json())
      .then(setCompanies);

    fetch(`${API_BASE_URL}/customers/`)
      .then((res) => res.json())
      .then(setCustomers);
  }, []);
  return (
    <div className="page">
      <h1>🤖 JAX - Operations Director</h1>

      <p>Your AI dispatch manager.</p>

      <div className="card">
        <h2>Morning Brief</h2>

        <ul>
        <li>✅ Fleet Status: {trucks.length} Trucks Online</li>
        <li>🚛 Active Loads: 7</li>
        <li>👷 Drivers Available: {drivers.length}</li>
        <li>🏢 Companies: {companies.length}</li>
        <li>👥 Customers: {customers.length}</li>
        <li>⚠️ Truck 579 needs maintenance</li>
        <li>💰 Two invoices overdue</li>
        </ul>
      </div>

      <div className="card">
        <h2>Ask JAX</h2>

    <button onClick={() => askJax("Dispatch Loads")}>Dispatch Loads</button>
    <button onClick={() => askJax("Assign Drivers")}>Assign Drivers</button>
    <button onClick={() => askJax("Fleet Status")}>Fleet Status</button>
    <button onClick={() => askJax("Customer Updates")}>Customer Updates</button>
      </div>
    </div>
  );
}