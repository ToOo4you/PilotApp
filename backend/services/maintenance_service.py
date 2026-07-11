"""
Predictive Maintenance AI Service
Predicts vehicle maintenance needs before failures occur
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from backend.services.ai_service import ai_service

logger = logging.getLogger(__name__)


@dataclass
class VehicleData:
    """Vehicle sensor and operational data"""
    vehicle_id: str
    mileage: int
    engine_hours: int
    fuel_consumption: float  # average
    tire_pressure_readings: List[float]
    engine_temperature: float
    oil_pressure: float
    battery_voltage: float
    diagnostics_codes: List[str]
    last_service_date: str
    service_interval: int  # in days
    utilization_percentage: float


@dataclass
class MaintenancePrediction:
    """Maintenance prediction result"""
    vehicle_id: str
    predicted_issue: str
    urgency_level: str  # low, medium, high, critical
    estimated_days_to_failure: int
    recommended_action: str
    estimated_cost: float
    confidence_score: float
    parts_needed: List[str]
    downtime_estimate_hours: float


class PredictiveMaintenanceService:
    """AI-powered predictive maintenance"""
    
    async def predict_maintenance_needs(
        self,
        vehicle_data: VehicleData,
        historical_data: Dict[str, Any] = None
    ) -> List[MaintenancePrediction]:
        """
        Predict maintenance needs for a vehicle
        
        Args:
            vehicle_data: Current vehicle sensor/operational data
            historical_data: Historical maintenance and performance data
        
        Returns:
            List of maintenance predictions
        """
        
        diag_codes = f"Diagnostic codes: {', '.join(vehicle_data.diagnostics_codes)}" if vehicle_data.diagnostics_codes else ""
        
        prompt = f"""
        Predict maintenance needs for vehicle:
        
        Vehicle ID: {vehicle_data.vehicle_id}
        Mileage: {vehicle_data.mileage} km
        Engine hours: {vehicle_data.engine_hours}
        
        Current readings:
        - Fuel consumption: {vehicle_data.fuel_consumption} L/km
        - Tire pressure: {vehicle_data.tire_pressure_readings} PSI
        - Engine temp: {vehicle_data.engine_temperature}°C
        - Oil pressure: {vehicle_data.oil_pressure} PSI
        - Battery: {vehicle_data.battery_voltage}V
        {diag_codes}
        
        Service history:
        - Last service: {vehicle_data.last_service_date}
        - Service interval: {vehicle_data.service_interval} days
        - Utilization: {vehicle_data.utilization_percentage}%
        
        Based on predictive analytics, identify ALL potential maintenance issues:
        
        For each issue, return JSON array with:
        - predicted_issue: Issue name
        - urgency_level: low/medium/high/critical
        - estimated_days_to_failure: Number of days before likely failure
        - recommended_action: What to do
        - estimated_cost: Cost in USD
        - confidence_score: 0-100
        - parts_needed: List of parts to order
        - downtime_estimate_hours: Hours vehicle will be down
        """
        
        try:
            response = await ai_service.call_ai(
                prompt,
                provider="claude",  # Claude excels at detailed analysis
                model="claude-3-opus-20240229",
                temperature=0.3
            )
            
            import json
            results = json.loads(response)
            
            predictions = []
            for result in results if isinstance(results, list) else [results]:
                predictions.append(MaintenancePrediction(
                    vehicle_id=vehicle_data.vehicle_id,
                    predicted_issue=result['predicted_issue'],
                    urgency_level=result['urgency_level'],
                    estimated_days_to_failure=int(result.get('estimated_days_to_failure', 0)),
                    recommended_action=result['recommended_action'],
                    estimated_cost=float(result.get('estimated_cost', 0)),
                    confidence_score=float(result.get('confidence_score', 0)) / 100,
                    parts_needed=result.get('parts_needed', []),
                    downtime_estimate_hours=float(result.get('downtime_estimate_hours', 0))
                ))
            
            return predictions
            
        except Exception as e:
            logger.error(f"Maintenance prediction failed: {e}")
            raise
    
    async def schedule_maintenance(
        self,
        predictions: List[MaintenancePrediction],
        available_slots: List[Dict[str, Any]],
        priority_constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Schedule maintenance based on predictions and availability"""
        
        predictions_text = "\n".join([
            f"- {p.predicted_issue} ({p.urgency_level}): {p.estimated_days_to_failure} days"
            for p in predictions
        ])
        
        prompt = f"""
        Schedule maintenance based on urgency and vehicle availability:
        
        Predicted issues:
        {predictions_text}
        
        Available maintenance slots: {len(available_slots)}
        
        Create optimal maintenance schedule considering:
        1. Urgency levels
        2. Vehicle downtime impact
        3. Parts availability
        4. Cost optimization
        5. Preventive vs. reactive maintenance
        
        Return JSON with scheduled_maintenance array and overall_strategy.
        """
        
        try:
            response = await ai_service.call_ai(
                prompt,
                model="gpt-4",
                temperature=0.3
            )
            import json
            return json.loads(response)
        except Exception as e:
            logger.error(f"Maintenance scheduling failed: {e}")
            return {"error": str(e)}
    
    async def analyze_anomalies(
        self,
        vehicle_id: str,
        sensor_data: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """Detect anomalies in sensor data"""
        
        prompt = f"""
        Analyze sensor data for anomalies and failure indicators:
        
        Vehicle: {vehicle_id}
        Sensor data: {sensor_data}
        
        Identify: anomalies, failure indicators, recommended_actions
        
        Return JSON with anomaly_details array.
        """
        
        try:
            response = await ai_service.call_ai(prompt, model="gpt-3.5-turbo")
            import json
            return json.loads(response)
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return {"error": str(e)}


maintenance_service = PredictiveMaintenanceService()
