export default function Directors({ onSelect }) {
  return (
    <div style={{ padding: "30px" }}>
      <h1>🤖 AI Directors</h1>
      <p>Your executive AI team for Highway Pilot AI.</p>

      <h2>🧠 Pilot</h2>
      <p>CEO AI - monitoring the business.</p>

      <button onClick={() =>onSelect("Jax" )}>
        🚚 Operations Director
      </button>
      <p>Dispatch and scheduling.</p>

      <h2>🛠 Fleet Director</h2>
      <p>Trucks, trailers, and maintenance.</p>

      <h2>💰 Finance Director</h2>
      <p>Revenue, billing, and invoices.</p>
    </div>
  );
}
const askJax = async (task) => {
  const response = await fetch("http://127.0.0.1:8000/jax/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ task }),
  });

  const data = await response.json();
  alert(data.message);
};