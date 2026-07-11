import React, { useState } from 'react';
import './DriverAnalytics.css';
import { API_BASE_URL } from '../lib/api';

const DriverAnalytics = () => {
  const [selectedDriver, setSelectedDriver] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);

  const drivers = [
    {
      id: 'DRV-001',
      name: 'John Smith',
      trips: 324,
      onTime: 96.5,
      rating: 4.8,
      accidents: 0,
      violations: 2
    },
    {
      id: 'DRV-002',
      name: 'Sarah Johnson',
      trips: 287,
      onTime: 94.2,
      rating: 4.6,
      accidents: 1,
      violations: 3
    }
  ];

  const analyzeDriver = async (driver) => {
    setSelectedDriver(driver);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/driver-analytics/${driver.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          metrics: {
            name: driver.name,
            total_trips: driver.trips,
            on_time_percentage: driver.onTime,
            average_rating: driver.rating,
            accidents_count: driver.accidents,
            violations_count: driver.violations,
            average_speed: 85,
            harsh_braking_incidents: 3,
            harsh_acceleration_incidents: 2,
            fuel_efficiency_score: 78,
            customer_satisfaction: 4.7,
            experience_years: 8
          }
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        setAnalytics(data.insights);
      }
    } catch (error) {
      console.error('Analytics error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPerformanceColor = (level) => {
    switch (level) {
      case 'excellent': return '#28a745';
      case 'good': return '#17a2b8';
      case 'average': return '#ffc107';
      case 'needs_improvement': return '#dc3545';
      default: return '#999';
    }
  };

  return (
    <div className="driver-analytics">
      <h2>👥 Driver Analytics</h2>

      <div className="analytics-grid">
        <div className="drivers-list-section">
          <h3>Select Driver</h3>
          <div className="drivers-list">
            {drivers.map(driver => (
              <div
                key={driver.id}
                className={`driver-selection ${selectedDriver?.id === driver.id ? 'active' : ''}`}
                onClick={() => analyzeDriver(driver)}
              >
                <div className="driver-header">
                  <span className="name">{driver.name}</span>
                  <span className="rating">⭐ {driver.rating}</span>
                </div>
                <div className="driver-stats">
                  <span className="stat">📊 {driver.trips} trips</span>
                  <span className="stat">✅ {driver.onTime}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="analytics-result-section">
          {loading ? (
            <div className="loading">⏳ Analyzing driver performance...</div>
          ) : analytics ? (
            <div className="analytics-result">
              <div className="performance-header">
                <h3>{selectedDriver.name} - Performance Analysis</h3>
                <span
                  className="performance-level"
                  style={{ backgroundColor: getPerformanceColor(analytics.performance_level) }}
                >
                  {analytics.performance_level.toUpperCase()}
                </span>
              </div>

              <div className="scores-grid">
                <div className="score-card">
                  <span className="score-label">Safety Score</span>
                  <div className="score-bar">
                    <div
                      className="score-fill"
                      style={{ width: `${analytics.safety_score * 100}%` }}
                    ></div>
                  </div>
                  <span className="score-value">{(analytics.safety_score * 100).toFixed(0)}%</span>
                </div>

                <div className="score-card">
                  <span className="score-label">Efficiency Score</span>
                  <div className="score-bar">
                    <div
                      className="score-fill"
                      style={{ width: `${analytics.efficiency_score * 100}%` }}
                    ></div>
                  </div>
                  <span className="score-value">{(analytics.efficiency_score * 100).toFixed(0)}%</span>
                </div>

                <div className="score-card">
                  <span className="score-label">Customer Service</span>
                  <div className="score-bar">
                    <div
                      className="score-fill"
                      style={{ width: `${analytics.customer_service_score * 100}%` }}
                    ></div>
                  </div>
                  <span className="score-value">{(analytics.customer_service_score * 100).toFixed(0)}%</span>
                </div>

                <div className="score-card">
                  <span className="score-label">Retention Risk</span>
                  <div className="score-bar danger">
                    <div
                      className="score-fill danger-fill"
                      style={{ width: `${analytics.predicted_retention_risk * 100}%` }}
                    ></div>
                  </div>
                  <span className="score-value">{(analytics.predicted_retention_risk * 100).toFixed(0)}%</span>
                </div>
              </div>

              <div className="insights-sections">
                {analytics.key_strengths && analytics.key_strengths.length > 0 && (
                  <div className="insight-box success">
                    <h4>💪 Strengths</h4>
                    <ul>
                      {analytics.key_strengths.map((strength, idx) => (
                        <li key={idx}>{strength}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {analytics.areas_for_improvement && analytics.areas_for_improvement.length > 0 && (
                  <div className="insight-box warning">
                    <h4>🎯 Areas for Improvement</h4>
                    <ul>
                      {analytics.areas_for_improvement.map((area, idx) => (
                        <li key={idx}>{area}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {analytics.risk_factors && analytics.risk_factors.length > 0 && (
                  <div className="insight-box danger">
                    <h4>⚠️ Risk Factors</h4>
                    <ul>
                      {analytics.risk_factors.map((risk, idx) => (
                        <li key={idx}>{risk}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {analytics.coaching_suggestions && analytics.coaching_suggestions.length > 0 && (
                  <div className="insight-box info">
                    <h4>📚 Coaching Suggestions</h4>
                    <ul>
                      {analytics.coaching_suggestions.map((suggestion, idx) => (
                        <li key={idx}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="placeholder">
              <p>📊 Select a driver to view detailed analytics</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DriverAnalytics;
