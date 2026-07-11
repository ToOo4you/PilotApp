import { useEffect, useState } from "react";
import { API_BASE_URL } from './lib/api';

export default function Drivers() {
  const [drivers, setDrivers] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE_URL}/drivers/`)
      .then((res) => res.json())
      .then((data) => setDrivers(data))
      .catch((err) => console.error("Drivers error:", err));
  }, []);

  return (
    <div>
      <h1>Drivers</h1>

      {drivers.map((driver) => (
        <div key={driver.id}>
          <h3>{driver.first_name} {driver.last_name}</h3>
          <p>CDL: {driver.cdl_number}</p>
          <p>Phone: {driver.phone}</p>
        </div>
      ))}
    </div>
  );
}