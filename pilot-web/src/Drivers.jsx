import { useEffect, useState } from "react";

export default function Drivers() {
  const [drivers, setDrivers] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/drivers/")
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