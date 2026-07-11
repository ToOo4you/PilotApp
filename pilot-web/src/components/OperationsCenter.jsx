import { useEffect, useMemo, useState } from 'react';
import './OperationsCenter.css';
import { API_BASE_URL } from '../lib/api';

function OperationsCenter() {
  const [origin, setOrigin] = useState('Los Angeles, CA');
  const [destination, setDestination] = useState('Phoenix, AZ');
  const [waypoints, setWaypoints] = useState('');
  const [routeData, setRouteData] = useState(null);

  const [latitude, setLatitude] = useState('34.0522');
  const [longitude, setLongitude] = useState('-118.2437');
  const [speedResult, setSpeedResult] = useState(null);

  const [dotRules, setDotRules] = useState([]);
  const [scales, setScales] = useState([]);

  const [driverId, setDriverId] = useState('D-1001');
  const [status, setStatus] = useState('driving');
  const [location, setLocation] = useState('I-10 MM 112');
  const [notes, setNotes] = useState('Routine run');
  const [logbookEntries, setLogbookEntries] = useState([]);
  const [hosSummary, setHosSummary] = useState(null);

  const waypointList = useMemo(
    () => waypoints.split(',').map((w) => w.trim()).filter(Boolean),
    [waypoints]
  );

  const fetchDotAndScales = async () => {
    const [dotRes, scaleRes] = await Promise.all([
      fetch(`${API_BASE_URL}/ops/dot-regulations`),
      fetch(`${API_BASE_URL}/ops/scale-locations`),
    ]);

    const dotJson = await dotRes.json();
    const scaleJson = await scaleRes.json();

    setDotRules(dotJson.regulations || []);
    setScales(scaleJson.locations || []);
  };

  const fetchLogbooks = async () => {
    const response = await fetch(`${API_BASE_URL}/ops/logbooks`);
    const json = await response.json();
    setLogbookEntries(json.entries || []);
  };

  useEffect(() => {
    fetchDotAndScales().catch(console.error);
    fetchLogbooks().catch(console.error);
  }, []);

  const runRoute = async () => {
    const response = await fetch(`${API_BASE_URL}/ops/navigation/route`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ origin, destination, waypoints: waypointList }),
    });

    const json = await response.json();
    setRouteData(json.route || null);
  };

  const lookupSpeed = async () => {
    const response = await fetch(`${API_BASE_URL}/ops/speed-limits`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ latitude: Number(latitude), longitude: Number(longitude) }),
    });

    const json = await response.json();
    setSpeedResult(json.lookup || null);
  };

  const addLogbookEntry = async () => {
    const response = await fetch(`${API_BASE_URL}/ops/logbooks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        driver_id: driverId,
        status,
        location,
        notes,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to create logbook entry');
    }

    setNotes('');
    await fetchLogbooks();
  };

  const loadHosSummary = async () => {
    const response = await fetch(`${API_BASE_URL}/ops/logbooks/${driverId}/hos-summary`);
    const json = await response.json();
    setHosSummary(json);
  };

  return (
    <div className="ops-wrap">
      <h1>Operations Center</h1>
      <p className="subtitle">GPS navigation, speed checks, DOT compliance, scales, and electronic log books.</p>

      <section className="ops-grid">
        <article className="ops-panel">
          <h3>GPS Navigation Map</h3>
          <label>Origin</label>
          <input value={origin} onChange={(e) => setOrigin(e.target.value)} />
          <label>Destination</label>
          <input value={destination} onChange={(e) => setDestination(e.target.value)} />
          <label>Waypoints (comma separated)</label>
          <input value={waypoints} onChange={(e) => setWaypoints(e.target.value)} />
          <button onClick={runRoute}>Generate Route</button>

          {routeData && (
            <div className="ops-result">
              <p><strong>Distance:</strong> {routeData.distance_miles_estimate} mi</p>
              <p><strong>ETA:</strong> {routeData.eta_minutes_estimate} min</p>
              <a href={routeData.map_url} target="_blank" rel="noreferrer">Open Map</a>
            </div>
          )}
        </article>

        <article className="ops-panel">
          <h3>Speed Limits Lookup</h3>
          <label>Latitude</label>
          <input value={latitude} onChange={(e) => setLatitude(e.target.value)} />
          <label>Longitude</label>
          <input value={longitude} onChange={(e) => setLongitude(e.target.value)} />
          <button onClick={lookupSpeed}>Check Limit</button>

          {speedResult && (
            <div className="ops-result">
              <p><strong>Nearest Zone:</strong> {speedResult.nearest_zone}</p>
              <p><strong>Limit:</strong> {speedResult.speed_limit_mph} mph</p>
              <p><strong>Distance:</strong> {speedResult.distance_to_zone_miles} mi</p>
            </div>
          )}
        </article>
      </section>

      <section className="ops-grid">
        <article className="ops-panel">
          <h3>DOT Regulations</h3>
          {dotRules.map((rule) => (
            <div className="ops-item" key={rule.code}>
              <p><strong>{rule.code} - {rule.title}</strong></p>
              <p>{rule.summary}</p>
              <p className="ops-note">Rule: {rule.practical_rule}</p>
            </div>
          ))}
        </article>

        <article className="ops-panel">
          <h3>Scale Locations</h3>
          {scales.map((scale) => (
            <div className="ops-item" key={scale.id}>
              <p><strong>{scale.name}</strong></p>
              <p>{scale.state} | {scale.highway} | {scale.mile_marker}</p>
              <p>Status: {scale.status}</p>
            </div>
          ))}
        </article>
      </section>

      <section className="ops-panel">
        <h3>Electronic Log Book</h3>
        <div className="ops-form-row">
          <input placeholder="Driver ID" value={driverId} onChange={(e) => setDriverId(e.target.value)} />
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="driving">Driving</option>
            <option value="on_duty">On Duty</option>
            <option value="off_duty">Off Duty</option>
            <option value="sleeper">Sleeper Berth</option>
          </select>
          <input placeholder="Location" value={location} onChange={(e) => setLocation(e.target.value)} />
          <input placeholder="Notes" value={notes} onChange={(e) => setNotes(e.target.value)} />
          <button onClick={addLogbookEntry}>Add Entry</button>
        </div>

        <div className="ops-hos-row">
          <button onClick={loadHosSummary}>Check DOT HOS Summary</button>
        </div>

        {hosSummary && hosSummary.totals && (
          <div className="ops-result">
            <p><strong>Driver:</strong> {hosSummary.driver_id}</p>
            <p><strong>Driving (24h):</strong> {hosSummary.totals.driving_minutes} min</p>
            <p><strong>On Duty (24h):</strong> {hosSummary.totals.on_duty_minutes} min</p>
            <p><strong>Driving Remaining:</strong> {hosSummary.totals.remaining_driving_minutes} min</p>
            <p><strong>On Duty Remaining:</strong> {hosSummary.totals.remaining_on_duty_minutes} min</p>
            <p><strong>Compliant:</strong> {hosSummary.compliant ? 'Yes' : 'No'}</p>
            {!hosSummary.compliant && hosSummary.violations?.length > 0 && (
              <ul>
                {hosSummary.violations.map((violation) => (
                  <li key={violation}>{violation}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        <div>
          {logbookEntries.map((entry) => (
            <div className="ops-item" key={entry.id}>
              <p><strong>{entry.driver_id}</strong> - {entry.status}</p>
              <p>{entry.location}</p>
              <p>{entry.notes}</p>
              <p className="ops-note">{entry.created_at}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default OperationsCenter;
