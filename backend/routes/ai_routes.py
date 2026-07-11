"""
AI-Powered Logistics API Routes
Core endpoints for Highway Pilot autonomous logistics platform
"""
from fastapi import APIRouter, HTTPException, WebSocket, Depends
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime

from backend.services.route_optimizer import route_optimizer, RouteStop, Location
from backend.services.dispatch_service import dispatch_service, Driver, Job
from backend.services.maintenance_service import maintenance_service, VehicleData
from backend.services.driver_analytics import driver_analytics, DriverMetrics
from backend.services.forecasting_service import forecasting_service
from backend.services.chatbot_service import chatbot

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI Services"])


# ============= Route Optimization =============

@router.post("/optimize-route")
async def optimize_route(
    stops: List[Dict[str, Any]],
    vehicle_type: str = "standard",
    traffic_data: Optional[Dict[str, Any]] = None,
    avoid_areas: Optional[List[str]] = None,
    driver_preferences: Optional[Dict[str, Any]] = None
):
    """Optimize delivery route using AI"""
    try:
        # Convert dict stops to RouteStop objects
        route_stops = [
            RouteStop(
                job_id=stop.get("job_id"),
                location=Location(
                        latitude=stop["location"]["lat"],
                        longitude=stop["location"]["lng"],
                        address=stop["location"].get("address", "")
                ),
                priority=stop.get("priority", 5)
            )
            for stop in stops
        ]
        
        optimized = await route_optimizer.optimize_route(
            route_stops,
            vehicle_type,
            traffic_data,
            avoid_areas,
            driver_preferences
        )
        
        return {
            "status": "success",
            "route": {
                "stops": [
                    {
                        "job_id": stop.job_id,
                        "address": stop.location.address,
                        "lat": stop.location.latitude,
                        "lng": stop.location.longitude
                    }
                    for stop in optimized.stops
                ],
                "total_distance": optimized.total_distance,
                "estimated_duration_minutes": optimized.estimated_duration,
                "confidence_score": optimized.confidence_score,
                "traffic_adjustments": optimized.traffic_adjustments,
                "notes": optimized.notes
            }
        }
    except Exception as e:
        logger.error(f"Route optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict-eta")
async def predict_eta(
    route_id: str,
    current_location: Dict[str, float],
    current_time: Optional[str] = None
):
    """Predict ETA for a route"""
    try:
        location = Location(
            latitude=current_location["lat"],
                longitude=current_location["lng"],
                address=current_location.get("address", "")
        )
        current = datetime.fromisoformat(current_time) if current_time else None
        
        # Get route (in production, fetch from DB)
        # For now, return placeholder
        result = await route_optimizer.predict_eta(None, location, current)
        
        return {
            "status": "success",
            "eta_prediction": result
        }
    except Exception as e:
        logger.error(f"ETA prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= Autonomous Dispatch =============

@router.post("/auto-dispatch")
async def auto_dispatch_job(
    job: Dict[str, Any],
    available_drivers: List[Dict[str, Any]],
    system_constraints: Optional[Dict[str, Any]] = None
):
    """Auto-assign job to best available driver"""
    try:
        # Convert to service objects
        job_obj = Job(
            id=job["id"],
            pickup_location=job["pickup_location"],
            delivery_location=job["delivery_location"],
            weight=job.get("weight", 0),
            dimensions=job.get("dimensions", {}),
            priority=job.get("priority", 5),
            cargo_type=job.get("cargo_type", "general"),
            time_window_start=job.get("time_window_start"),
            time_window_end=job.get("time_window_end"),
            special_requirements=job.get("special_requirements", [])
        )
        
        drivers_obj = [
            Driver(
                id=d["id"],
                name=d["name"],
                current_location=d["current_location"],
                available_capacity=d.get("available_capacity", 0),
                license_type=d.get("license_type", "standard"),
                current_jobs_count=d.get("current_jobs_count", 0),
                rating=d.get("rating", 0),
                experience_years=d.get("experience_years", 0)
            )
            for d in available_drivers
        ]
        
        assignment = await dispatch_service.assign_job_to_driver(
            job_obj,
            drivers_obj,
            system_constraints
        )
        
        return {
            "status": "success",
            "assignment": {
                "job_id": assignment.job_id,
                "driver_id": assignment.driver_id,
                "driver_name": assignment.driver_name,
                "confidence_score": assignment.confidence_score,
                "reason": assignment.reason,
                "pickup_eta": assignment.pickup_eta,
                "delivery_eta": assignment.delivery_eta,
                "optimization_notes": assignment.route_optimization_notes
            }
        }
    except Exception as e:
        logger.error(f"Auto-dispatch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-dispatch")
async def batch_dispatch(
    jobs: List[Dict[str, Any]],
    available_drivers: List[Dict[str, Any]],
    optimization_strategy: str = "balanced"
):
    """Dispatch multiple jobs optimally"""
    try:
        jobs_obj = [
            Job(
                id=j["id"],
                pickup_location=j["pickup_location"],
                delivery_location=j["delivery_location"],
                weight=j.get("weight", 0),
                dimensions=j.get("dimensions", {}),
                priority=j.get("priority", 5),
                cargo_type=j.get("cargo_type", "general")
            )
            for j in jobs
        ]
        
        drivers_obj = [
            Driver(
                id=d["id"],
                name=d["name"],
                current_location=d["current_location"],
                available_capacity=d.get("available_capacity", 0),
                license_type=d.get("license_type", "standard"),
                current_jobs_count=d.get("current_jobs_count", 0),
                rating=d.get("rating", 0),
                experience_years=d.get("experience_years", 0)
            )
            for d in available_drivers
        ]
        
        assignments = await dispatch_service.assign_batch_jobs(
            jobs_obj,
            drivers_obj,
            optimization_strategy
        )
        
        return {
            "status": "success",
            "assignments": [
                {
                    "job_id": a.job_id,
                    "driver_id": a.driver_id,
                    "driver_name": a.driver_name,
                    "confidence_score": a.confidence_score
                }
                for a in assignments
            ]
        }
    except Exception as e:
        logger.error(f"Batch dispatch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= Predictive Maintenance =============

@router.post("/predict-maintenance")
async def predict_maintenance(
    vehicle_data: Dict[str, Any],
    historical_data: Optional[Dict[str, Any]] = None
):
    """Predict maintenance needs for a vehicle"""
    try:
        vehicle = VehicleData(
            vehicle_id=vehicle_data["vehicle_id"],
            mileage=vehicle_data.get("mileage", 0),
            engine_hours=vehicle_data.get("engine_hours", 0),
            fuel_consumption=vehicle_data.get("fuel_consumption", 0),
            tire_pressure_readings=vehicle_data.get("tire_pressure_readings", []),
            engine_temperature=vehicle_data.get("engine_temperature", 0),
            oil_pressure=vehicle_data.get("oil_pressure", 0),
            battery_voltage=vehicle_data.get("battery_voltage", 0),
            diagnostics_codes=vehicle_data.get("diagnostics_codes", []),
            last_service_date=vehicle_data.get("last_service_date", ""),
            service_interval=vehicle_data.get("service_interval", 0),
            utilization_percentage=vehicle_data.get("utilization_percentage", 0)
        )
        
        predictions = await maintenance_service.predict_maintenance_needs(
            vehicle,
            historical_data
        )
        
        return {
            "status": "success",
            "predictions": [
                {
                    "issue": p.predicted_issue,
                    "urgency": p.urgency_level,
                    "days_to_failure": p.estimated_days_to_failure,
                    "action": p.recommended_action,
                    "cost": p.estimated_cost,
                    "confidence": p.confidence_score,
                    "parts_needed": p.parts_needed,
                    "downtime_hours": p.downtime_estimate_hours
                }
                for p in predictions
            ]
        }
    except Exception as e:
        logger.error(f"Maintenance prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= Driver Analytics =============

@router.post("/driver-analytics/{driver_id}")
async def analyze_driver(
    driver_id: str,
    metrics: Dict[str, Any],
    benchmark_data: Optional[Dict[str, float]] = None
):
    """Analyze driver performance"""
    try:
        driver_metrics = DriverMetrics(
            driver_id=driver_id,
            name=metrics.get("name", ""),
            total_trips=metrics.get("total_trips", 0),
            on_time_percentage=metrics.get("on_time_percentage", 0),
            average_rating=metrics.get("average_rating", 0),
            accidents_count=metrics.get("accidents_count", 0),
            violations_count=metrics.get("violations_count", 0),
            average_speed=metrics.get("average_speed", 0),
            harsh_braking_incidents=metrics.get("harsh_braking_incidents", 0),
            harsh_acceleration_incidents=metrics.get("harsh_acceleration_incidents", 0),
            fuel_efficiency_score=metrics.get("fuel_efficiency_score", 0),
            customer_satisfaction=metrics.get("customer_satisfaction", 0),
            experience_years=metrics.get("experience_years", 0)
        )
        
        insights = await driver_analytics.analyze_driver_performance(
            driver_metrics,
            benchmark_data
        )
        
        return {
            "status": "success",
            "insights": {
                "performance_level": insights.performance_level,
                "safety_score": insights.safety_score,
                "efficiency_score": insights.efficiency_score,
                "customer_service_score": insights.customer_service_score,
                "strengths": insights.key_strengths,
                "improvements_needed": insights.areas_for_improvement,
                "recommendations": insights.recommendations,
                "risk_factors": insights.risk_factors,
                "coaching_suggestions": insights.coaching_suggestions,
                "retention_risk": insights.predicted_retention_risk
            }
        }
    except Exception as e:
        logger.error(f"Driver analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= Demand Forecasting =============

@router.post("/forecast-demand")
async def forecast_demand(
    historical_data: List[Dict[str, Any]],
    forecast_horizon_days: int = 30,
    include_seasonality: bool = True,
    include_external_factors: bool = True
):
    """Forecast shipping demand"""
    try:
        forecast = await forecasting_service.forecast_demand(
            historical_data,
            forecast_horizon_days,
            include_seasonality,
            include_external_factors
        )
        
        return {
            "status": "success",
            "forecast": {
                "period": forecast.forecast_period,
                "start_date": forecast.start_date,
                "end_date": forecast.end_date,
                "predicted_volume": forecast.predicted_volume,
                "confidence": forecast.confidence_interval,
                "growth_rate": forecast.growth_rate,
                "seasonal_factors": forecast.seasonal_factors,
                "recommended_capacity": forecast.recommended_capacity,
                "peak_days": forecast.peak_days,
                "supply_recommendations": forecast.supply_recommendations,
                "risk_factors": forecast.risk_factors
            }
        }
    except Exception as e:
        logger.error(f"Demand forecasting error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= AI Chatbot =============

@router.post("/chat")
async def chat(
    session_id: str,
    message: str,
    context_data: Optional[Dict[str, Any]] = None
):
    """Chat with AI dispatcher"""
    try:
        response = await chatbot.chat(message, session_id, context_data)
        
        return {
            "status": "success",
            "response": {
                "message": response.message,
                "action_type": response.action_type,
                "action_data": response.action_data,
                "context": response.context.value,
                "confidence": response.confidence_score,
                "followup_questions": response.followup_questions
            }
        }
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat-history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        history = chatbot.get_conversation_history(session_id)
        return {
            "status": "success",
            "history": history
        }
    except Exception as e:
        logger.error(f"Chat history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat-suggestions/{session_id}")
async def get_suggestions(session_id: str, context: str = "general"):
    """Get AI suggestions for next actions"""
    try:
        from backend.services.chatbot_service import ChatContext
        context_type = ChatContext[context.upper()] if context.upper() in ChatContext.__members__ else ChatContext.GENERAL
        
        suggestions = await chatbot.get_suggestions(session_id, context_type)
        
        return {
            "status": "success",
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= Health Check =============

@router.get("/health")
async def health_check():
    """Health check for AI services"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "route_optimizer": "active",
            "dispatch_service": "active",
            "maintenance_service": "active",
            "driver_analytics": "active",
            "forecasting_service": "active",
            "chatbot": "active"
        }
    }
