import React, { useState } from 'react';
import './MaintenancePredictor.css';

const MaintenancePredictor = () => {
  const [vehicles, setVehicles] = useState([
    { id: 'VEH-001', make: 'Peterbilt', model: '579', mileage: 245000 },
    { id: 'VEH-002', make: 'Freightliner', model: 'Cascadia', mileage: 189000 }
  ]);
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);

  const predictMaintenance = async (vehicle) => {
    setSelectedVehicle(vehicle);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/ai/predict-maintenance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vehicle_data: {
            vehicle_id: vehicle.id,
            mileage: vehicle.mileage,
            engine_hours: Math.floor(vehicle.mileage / 6),
            fuel_consumption: 5.2,
            tire_pressure_readings: [100, 102, 98, 101],
            engine_temperature: 185,
            oil_pressure: 45,
            battery_voltage: 13.8,
            diagnostics_codes: [],
            last_service_date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
            service_interval: 180,
            utilization_percentage: 78
          }
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        setPredictions(data.predictions);
      }
    } catch (error) {
      console.error('Prediction error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'low': return '#28a745';
      case 'medium': return '#ffc107';
      case 'high': return '#ff9800';
      case 'critical': return '#dc3545';
      default: return '#999';
    }
  };

  return (
    <div className="maintenance-predictor">
      <h2>🔧 Predictive Maintenance</h2>

      <div className="maintenance-grid">
        <div className="vehicles-section">
          <h3>Select Vehicle</h3>
          <div className="vehicles-list">
            {vehicles.map(vehicle => (
              <div
                key={vehicle.id}
                className={`vehicle-card ${selectedVehicle?.id === vehicle.id ? 'active' : ''}`}
                onClick={() => predictMaintenance(vehicle)}
              >
                <div className="vehicle-info">
                  <p className="vehicle-name">{vehicle.make} {vehicle.model}</p>
                  <p className="vehicle-id">{vehicle.id}</p>
                  <p className="vehicle-mileage">📊 {vehicle.mileage.toLocaleString()} km</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="predictions-section">
          {loading ? (
            <div className="loading">⏳ Analyzing vehicle condition...</div>
          ) : predictions && predictions.length > 0 ? (
            <div className="predictions-result">
              <h3>Maintenance Predictions - {selectedVehicle.make} {selectedVehicle.model}</h3>

              <div className="predictions-list">
                {predictions.map((pred, idx) => (
                  <div key={idx} className="prediction-card">
                    <div className="prediction-header">
                      <span className="issue">{pred.issue}</span>
                      <span
                        className="urgency-badge"
                        style={{ backgroundColor: getUrgencyColor(pred.urgency) }}
                      >
                        {pred.urgency.toUpperCase()}
                      </span>
                    </div>

                    <div className="prediction-details">
                      <div className="detail-row">
                        <span className="label">⏰ Days to Failure:</span>
                        <span className="value">{pred.days_to_failure} days</span>
                      </div>
                      <div className="detail-row">
                        <span className="label">💰 Estimated Cost:</span>
                        <span className="value">${pred.cost.toFixed(2)}</span>
                      </div>
                      <div className="detail-row">
                        <span className="label">🎯 Confidence:</span>
                        <span className="value">{(pred.confidence * 100).toFixed(0)}%</span>
                      </div>
                      <div className="detail-row">
                        <span className="label">⏱️ Downtime:</span>
                        <span className="value">{pred.downtime_hours} hours</span>
                      </div>
                    </div>

                    <div className="action-section">
                      <p className="action-label">✅ Recommended Action:</p>
                      <p className="action-text">{pred.action}</p>
                    </div>

                    {pred.parts_needed && pred.parts_needed.length > 0 && (
                      <div className="parts-section">
                        <p className="parts-label">📦 Parts Needed:</p>
                        <div className="parts-list">
                          {pred.parts_needed.map((part, pidx) => (
                            <span key={pidx} className="part-badge">{part}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="recommendations">
                <h4>🎯 Maintenance Recommendations</h4>
                <ul>
                  <li>Schedule preventive maintenance before critical issues develop</li>
                  <li>Order parts in advance to minimize vehicle downtime</li>
                  <li>Plan maintenance around delivery schedules</li>
                  <li>Monitor vehicle performance regularly</li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="placeholder">
              <p>🚗 Select a vehicle to view maintenance predictions</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MaintenancePredictor;
