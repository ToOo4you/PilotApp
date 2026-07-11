"""
Driver Analytics AI Service
Analyzes driver performance, behavior, and provides insights
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from backend.services.ai_service import ai_service

logger = logging.getLogger(__name__)


@dataclass
class DriverMetrics:
    """Driver performance metrics"""
    driver_id: str
    name: str
    total_trips: int
    on_time_percentage: float
    average_rating: float
    accidents_count: int
    violations_count: int
    average_speed: float
    harsh_braking_incidents: int
    harsh_acceleration_incidents: int
    fuel_efficiency_score: float
    customer_satisfaction: float
    experience_years: int


@dataclass
class DriverInsights:
    """Driver analytics insights"""
    driver_id: str
    performance_level: str  # excellent, good, average, needs_improvement
    safety_score: float
    efficiency_score: float
    customer_service_score: float
    key_strengths: List[str]
    areas_for_improvement: List[str]
    recommendations: List[str]
    risk_factors: List[str]
    coaching_suggestions: List[str]
    predicted_retention_risk: float


class DriverAnalyticsService:
    """AI-powered driver analytics"""
    
    async def analyze_driver_performance(
        self,
        driver_metrics: DriverMetrics,
        benchmark_data: Dict[str, float] = None
    ) -> DriverInsights:
        """
        Analyze driver performance and generate insights
        
        Args:
            driver_metrics: Driver performance metrics
            benchmark_data: Industry/fleet benchmarks for comparison
        
        Returns:
            DriverInsights with analysis and recommendations
        """
        
        benchmark_context = f"Benchmarks: {benchmark_data}" if benchmark_data else "Using industry standards"
        
        prompt = f"""
        Analyze driver performance comprehensively:
        
        Driver: {driver_metrics.name} (ID: {driver_metrics.driver_id})
        Experience: {driver_metrics.experience_years} years
        
        Performance metrics:
        - Trips completed: {driver_metrics.total_trips}
        - On-time %: {driver_metrics.on_time_percentage}%
        - Rating: {driver_metrics.average_rating}/5.0
        - Accidents: {driver_metrics.accidents_count}
        - Violations: {driver_metrics.violations_count}
        - Average speed: {driver_metrics.average_speed} km/h
        - Harsh braking: {driver_metrics.harsh_braking_incidents} incidents
        - Harsh acceleration: {driver_metrics.harsh_acceleration_incidents} incidents
        - Fuel efficiency: {driver_metrics.fuel_efficiency_score}/100
        - Customer satisfaction: {driver_metrics.customer_satisfaction}/5.0
        
        {benchmark_context}
        
        Provide comprehensive analysis:
        - performance_level: excellent/good/average/needs_improvement
        - safety_score: 0-100
        - efficiency_score: 0-100
        - customer_service_score: 0-100
        - key_strengths: List of top strengths
        - areas_for_improvement: Areas needing work
        - coaching_suggestions: Specific coaching recommendations
        - risk_factors: Any warning signs or concerns
        - retention_risk: 0-100 likelihood they'll leave
        
        Return JSON response.
        """
        
        try:
            response = await ai_service.call_ai(
                prompt,
                provider="claude",
                model="claude-3-opus-20240229",
                temperature=0.4
            )
            
            import json
            result = json.loads(response)
            
            return DriverInsights(
                driver_id=driver_metrics.driver_id,
                performance_level=result['performance_level'],
                safety_score=float(result.get('safety_score', 0)) / 100,
                efficiency_score=float(result.get('efficiency_score', 0)) / 100,
                customer_service_score=float(result.get('customer_service_score', 0)) / 100,
                key_strengths=result.get('key_strengths', []),
                areas_for_improvement=result.get('areas_for_improvement', []),
                recommendations=result.get('general_recommendations', []),
                risk_factors=result.get('risk_factors', []),
                coaching_suggestions=result.get('coaching_suggestions', []),
                predicted_retention_risk=float(result.get('retention_risk', 0)) / 100
            )
            
        except Exception as e:
            logger.error(f"Driver analysis failed: {e}")
            raise
    
    async def detect_unsafe_behavior(
        self,
        driver_id: str,
        recent_trips: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect unsafe driving behavior patterns
        
        Args:
            driver_id: Driver ID
            recent_trips: Recent trip data with telemetry
        
        Returns:
            Safety analysis with alerts
        """
        
        trips_summary = f"Analyzed {len(recent_trips)} recent trips"
        
        prompt = f"""
        Analyze recent driving behavior for safety concerns:
        
        Driver: {driver_id}
        {trips_summary}
        
        Recent trip data: {recent_trips}
        
        Identify:
        - unsafe_behaviors: List of unsafe behaviors detected
        - severity_level: low/medium/high/critical
        - immediate_action_needed: true/false
        - recommendations: Corrective actions
        
        Return JSON response.
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
            logger.error(f"Unsafe behavior detection failed: {e}")
            return {"error": str(e)}
    
    async def predict_future_performance(
        self,
        driver_id: str,
        historical_data: Dict[str, Any],
        intervention_recommendations: bool = False
    ) -> Dict[str, Any]:
        """Predict future driver performance based on trends"""
        
        prompt = f"""
        Predict future performance trajectory:
        
        Driver: {driver_id}
        Historical data trend: {historical_data}
        
        Predict (3-6 months):
        - performance_trajectory: improving/stable/declining
        - predicted_metrics: Expected performance levels
        - key_factors: What will drive performance
        {f'- intervention_recommendations: How to improve trajectory' if intervention_recommendations else ''}
        
        Return JSON response.
        """
        
        try:
            response = await ai_service.call_ai(prompt, model="gpt-3.5-turbo")
            import json
            return json.loads(response)
        except Exception as e:
            logger.error(f"Performance prediction failed: {e}")
            return {"error": str(e)}


driver_analytics = DriverAnalyticsService()
