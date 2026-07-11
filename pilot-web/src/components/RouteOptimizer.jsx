import React, { useState } from 'react';
import './RouteOptimizer.css';
import { API_BASE_URL } from '../lib/api';

const RouteOptimizer = () => {
  const [stops, setStops] = useState([]);
  const [optimizedRoute, setOptimizedRoute] = useState(null);
  const [loading, setLoading] = useState(false);
  const [vehicleType, setVehicleType] = useState('standard');
  const [newStop, setNewStop] = useState({ address: '', lat: 0, lng: 0, priority: 5 });

  const addStop = () => {
    if (newStop.address) {
      setStops([...stops, { ...newStop, job_id: `JOB-${Date.now()}` }]);
      setNewStop({ address: '', lat: 0, lng: 0, priority: 5 });
    }
  };

  const removeStop = (idx) => {
    setStops(stops.filter((_, i) => i !== idx));
  };

  const optimizeRoute = async () => {
    if (stops.length < 2) {
      alert('Please add at least 2 stops');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/optimize-route`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          stops: stops.map(s => ({
            job_id: s.job_id,
            location: {
              lat: parseFloat(s.lat) || 0,
              lng: parseFloat(s.lng) || 0,
              address: s.address
            },
            priority: parseInt(s.priority)
          })),
          vehicle_type: vehicleType,
          avoid_areas: [],
          driver_preferences: {}
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        setOptimizedRoute(data.route);
      }
    } catch (error) {
      console.error('Optimization error:', error);
      alert('Failed to optimize route');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="route-optimizer">
      <h2>📍 Route Optimizer</h2>
      
      <div className="optimizer-grid">
        <div className="input-section">
          <h3>Add Stops</h3>
          
          <div className="vehicle-type">
            <label>Vehicle Type:</label>
            <select value={vehicleType} onChange={(e) => setVehicleType(e.target.value)}>
              <option value="standard">Standard</option>
              <option value="van">Van</option>
              <option value="truck">Truck</option>
              <option value="hazmat">Hazmat</option>
            </select>
          </div>

          <div className="stop-input">
            <input
              type="text"
              placeholder="Stop address"
              value={newStop.address}
              onChange={(e) => setNewStop({ ...newStop, address: e.target.value })}
            />
            <input
              type="number"
              placeholder="Latitude"
              step="0.0001"
              value={newStop.lat}
              onChange={(e) => setNewStop({ ...newStop, lat: e.target.value })}
            />
            <input
              type="number"
              placeholder="Longitude"
              step="0.0001"
              value={newStop.lng}
              onChange={(e) => setNewStop({ ...newStop, lng: e.target.value })}
            />
            <select
              value={newStop.priority}
              onChange={(e) => setNewStop({ ...newStop, priority: e.target.value })}
            >
              {[...Array(10)].map((_, i) => (
                <option key={i + 1} value={i + 1}>{i + 1}</option>
              ))}
            </select>
            <button onClick={addStop} className="add-btn">+ Add Stop</button>
          </div>

          <div className="stops-list">
            <h4>Stops ({stops.length})</h4>
            {stops.map((stop, idx) => (
              <div key={idx} className="stop-item">
                <span className="stop-num">{idx + 1}</span>
                <div className="stop-info">
                  <p className="stop-address">{stop.address}</p>
                  <p className="stop-coords">{stop.lat.toFixed(4)}, {stop.lng.toFixed(4)}</p>
                </div>
                <span className="priority-badge">P{stop.priority}</span>
                <button onClick={() => removeStop(idx)} className="remove-btn">×</button>
              </div>
            ))}
          </div>

          <button
            onClick={optimizeRoute}
            disabled={loading || stops.length < 2}
            className="optimize-btn"
          >
            {loading ? '⏳ Optimizing...' : '✨ Optimize Route'}
          </button>
        </div>

        <div className="result-section">
          {optimizedRoute ? (
            <div className="route-result">
              <h3>Optimized Route</h3>
              
              <div className="stats">
                <div className="stat">
                  <span className="label">Total Distance</span>
                  <span className="value">{optimizedRoute.total_distance.toFixed(2)} km</span>
                </div>
                <div className="stat">
                  <span className="label">Duration</span>
                  <span className="value">{optimizedRoute.estimated_duration_minutes} min</span>
                </div>
                <div className="stat">
                  <span className="label">Confidence</span>
                  <span className="value">{(optimizedRoute.confidence_score * 100).toFixed(0)}%</span>
                </div>
              </div>

              <div className="route-stops">
                <h4>Route Order</h4>
                {optimizedRoute.stops.map((stop, idx) => (
                  <div key={idx} className="route-stop">
                    <span className="step">{idx + 1}</span>
                    <div className="stop-detail">
                      <p className="address">{stop.address}</p>
                      <p className="jobid">ID: {stop.job_id}</p>
                    </div>
                  </div>
                ))}
              </div>

              {optimizedRoute.traffic_adjustments && (
                <div className="alerts">
                  <p className="alert-title">⚠️ Traffic Notes</p>
                  <p>{optimizedRoute.traffic_adjustments}</p>
                </div>
              )}

              {optimizedRoute.notes && (
                <div className="notes">
                  <p className="notes-title">📝 Optimization Notes</p>
                  <p>{optimizedRoute.notes}</p>
                </div>
              )}

              <button className="export-btn">📤 Export Route</button>
            </div>
          ) : (
            <div className="placeholder">
              <p>🗺️ Add stops and click \"Optimize Route\" to see results</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RouteOptimizer;
