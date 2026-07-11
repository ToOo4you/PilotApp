import React, { useState } from 'react';
import './DispatchDashboard.css';
import { API_BASE_URL } from '../lib/api';

const DispatchDashboard = () => {
  const [jobs, setJobs] = useState([
    { id: 'JOB-001', priority: 8, cargo: 'Electronics', weight: 500 },
    { id: 'JOB-002', priority: 5, cargo: 'Furniture', weight: 2000 }
  ]);
  const [drivers, setDrivers] = useState([
    { id: 'DRV-001', name: 'John Smith', capacity: 5000, rating: 4.8 },
    { id: 'DRV-002', name: 'Sarah Johnson', capacity: 3000, rating: 4.6 }
  ]);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(false);

  const autoDispatch = async () => {
    if (!jobs.length || !drivers.length) {
      alert('Add jobs and drivers first');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/batch-dispatch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jobs: jobs.map(j => ({
            id: j.id,
            priority: j.priority,
            pickup_location: { lat: 40.7128, lng: -74.0060 },
            delivery_location: { lat: 40.7580, lng: -73.9855 },
            weight: j.weight,
            cargo_type: j.cargo
          })),
          available_drivers: drivers.map(d => ({
            id: d.id,
            name: d.name,
            current_location: { lat: 40.7128, lng: -74.0060 },
            available_capacity: d.capacity,
            rating: d.rating
          })),
          optimization_strategy: 'balanced'
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        setAssignments(data.assignments);
      }
    } catch (error) {
      console.error('Dispatch error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dispatch-dashboard">
      <h2>🚚 Autonomous Dispatch</h2>

      <div className="dispatch-grid">
        <div className="section jobs-section">
          <h3>📦 Pending Jobs</h3>
          <div className="jobs-list">
            {jobs.map(job => (
              <div key={job.id} className="job-card">
                <div className="job-header">
                  <span className="job-id">{job.id}</span>
                  <span className="priority-level">Priority: {job.priority}/10</span>
                </div>
                <p><strong>Cargo:</strong> {job.cargo}</p>
                <p><strong>Weight:</strong> {job.weight} kg</p>
              </div>
            ))}
          </div>
        </div>

        <div className="section drivers-section">
          <h3>👥 Available Drivers</h3>
          <div className="drivers-list">
            {drivers.map(driver => (
              <div key={driver.id} className="driver-card">
                <div className="driver-header">
                  <span className="driver-name">{driver.name}</span>
                  <span className="rating">⭐ {driver.rating}</span>
                </div>
                <p><strong>Capacity:</strong> {driver.capacity} kg</p>
                <p><strong>ID:</strong> {driver.id}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="dispatch-button-section">
          <button
            onClick={autoDispatch}
            disabled={loading}
            className="dispatch-btn"
          >
            {loading ? '⏳ Dispatching...' : '🤖 Auto-Dispatch All'}
          </button>
        </div>

        <div className="section assignments-section">
          <h3>✅ Assignments</h3>
          <div className="assignments-list">
            {assignments.length === 0 ? (
              <p className="placeholder">No assignments yet. Click Auto-Dispatch to generate assignments.</p>
            ) : (
              assignments.map((assign, idx) => (
                <div key={idx} className="assignment-card">
                  <div className="assignment-header">
                    <span className="job">{assign.job_id}</span>
                    <span className="arrow">→</span>
                    <span className="driver">{assign.driver_name}</span>
                  </div>
                  <div className="confidence">
                    Confidence: {(assign.confidence_score * 100).toFixed(0)}%
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DispatchDashboard;
