"""
AI-Powered Logistics API Routes
Core endpoints for Highway Pilot autonomous logistics platform
"""
from fastapi import APIRouter, HTTPException, WebSocket, Depends
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime

from sqlalchemy import func
from sqlalchemy import text

from backend.database.db import SessionLocal
from backend.database.models import Driver as DriverModel
from backend.database.models import Job as JobModel
from backend.routes.customers import customers as seed_customers
from backend.services.route_optimizer import route_optimizer, RouteStop, Location
from backend.services.dispatch_service import dispatch_service, Driver, Job
from backend.services.maintenance_service import maintenance_service, VehicleData
from backend.services.driver_analytics import driver_analytics, DriverMetrics
from backend.services.forecasting_service import forecasting_service
from backend.services.chatbot_service import chatbot
from backend.services.ai_service import ai_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI Services"])


def _recruit_score(name: str, email: str, subscribed: bool = False) -> int:
    score = 52
    name_value = (name or "").lower()
    email_value = (email or "").lower()

    if any(token in name_value for token in ["logistics", "transport", "freight", "supply"]):
        score += 18
    if any(token in email_value for token in ["ops", "dispatch", "fleet", "sales"]):
        score += 12
    if subscribed:
        score += 8

    return max(1, min(score, 99))


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


# ============= Revenue / Earnings =============

@router.get("/customer-fetch-subscribers")
async def customer_fetch_subscribers(include_inactive: bool = False):
    """Fetch customers and match them with subscription records, with AI insights."""
    db = SessionLocal()
    try:
        subs = db.execute(text("SELECT * FROM subscriptions")).mappings().all()
        subscribers_by_email: Dict[str, Dict[str, Any]] = {}

        for sub in subs:
            email = ((sub.get("customer_email") or sub.get("email") or "").strip().lower())
            if not email:
                continue

            status = (sub.get("status") or "inactive").strip().lower()
            if (not include_inactive) and status not in {"active", "trialing"}:
                continue

            subscribers_by_email[email] = {
                "subscription_id": sub.get("id"),
                "email": email,
                "plan": sub.get("plan_key") or sub.get("plan"),
                "status": status,
                "provider": sub.get("provider") or "stripe",
                "current_period_end": (
                    sub.get("current_period_end").isoformat()
                    if sub.get("current_period_end")
                    else None
                ),
            }

        matched_customers = []
        non_subscriber_leads = []

        def _lead_score(customer_row: Dict[str, Any]) -> int:
            # Simple deterministic scoring until richer customer telemetry is available.
            score = 55
            email_value = (customer_row.get("email") or "").lower()
            name_value = (customer_row.get("name") or "").lower()
            contact_value = (customer_row.get("contact") or "").lower()

            if any(token in email_value for token in ["logistics", "freight", "transport", "fleet"]):
                score += 20
            if any(token in name_value for token in ["inc", "llc", "logistics", "transport"]):
                score += 10
            if contact_value and contact_value != "n/a":
                score += 5

            return max(1, min(score, 99))

        def _customer_rating(customer_row: Dict[str, Any], subscribed: bool) -> float:
            base = 4.1 if subscribed else 3.9
            name_value = (customer_row.get("name") or "").lower()
            email_value = (customer_row.get("email") or "").lower()

            if any(token in name_value for token in ["logistics", "transport", "freight"]):
                base += 0.4
            if any(token in email_value for token in ["ops", "dispatch", "fleet"]):
                base += 0.2

            return round(max(3.0, min(base, 5.0)), 1)

        for customer in seed_customers:
            email = (customer.get("email") or "").strip().lower()
            sub = subscribers_by_email.get(email)
            if sub:
                rating = _customer_rating(customer, True)
                matched_customers.append(
                    {
                        "id": customer.get("id"),
                        "name": customer.get("name"),
                        "contact": customer.get("contact"),
                        "phone": customer.get("phone"),
                        "email": customer.get("email"),
                        "customer_rating": rating,
                        "high_rating": rating >= 4.5,
                        "subscription": sub,
                    }
                )
            else:
                score = _lead_score(customer)
                rating = _customer_rating(customer, False)
                non_subscriber_leads.append(
                    {
                        "id": customer.get("id"),
                        "name": customer.get("name"),
                        "contact": customer.get("contact"),
                        "phone": customer.get("phone"),
                        "email": customer.get("email"),
                        "conversion_score": score,
                        "customer_rating": rating,
                        "high_rating": rating >= 4.5,
                        "priority": "high" if score >= 75 else ("medium" if score >= 60 else "low"),
                        "recommended_offer": (
                            "14-day dispatch automation pilot"
                            if score >= 75
                            else "Starter plan with onboarding call"
                        ),
                    }
                )

        non_subscriber_leads.sort(key=lambda row: row.get("conversion_score", 0), reverse=True)

        prompt = (
            "You are a logistics revenue AI assistant. "
            f"Total customers: {len(seed_customers)}. "
            f"Subscriber customers: {len(matched_customers)}. "
            "Write 2 concise recommendations to increase subscriber conversions and retention."
        )

        lead_prompt = (
            "You are a B2B logistics growth strategist. "
            f"Non-subscriber lead count: {len(non_subscriber_leads)}. "
            "Provide one concise outreach strategy to convert top leads this week."
        )

        try:
            ai_summary = await ai_service.call_ai(prompt, temperature=0.3)
        except Exception:
            ai_summary = (
                "1) Launch a 14-day paid pilot with onboarding support for non-subscribers. "
                "2) Offer annual discounts and usage-based upsell prompts to increase retention."
            )

        try:
            lead_strategy = await ai_service.call_ai(lead_prompt, temperature=0.25)
        except Exception:
            lead_strategy = "Prioritize high-score leads with a 15-minute ROI demo and limited-time pilot offer."

        return {
            "status": "success",
            "customers_total": len(seed_customers),
            "subscriber_customers_total": len(matched_customers),
            "subscriber_customers": matched_customers,
            "non_subscriber_leads_total": len(non_subscriber_leads),
            "non_subscriber_leads": non_subscriber_leads,
            "ai_summary": ai_summary,
            "lead_strategy": lead_strategy,
        }
    except Exception as e:
        logger.error(f"Customer subscriber fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/recruiter-intelligence")
async def recruiter_intelligence():
    """Generate AI-assisted recruiting opportunities across customers, companies, and clients."""
    db = SessionLocal()
    try:
        companies = db.execute(
            text(
                """
                SELECT id, company_name, owner_name, phone, email, industry
                FROM companies
                ORDER BY created_at DESC
                LIMIT 120
                """
            )
        ).mappings().all()

        subs = db.execute(text("SELECT customer_email, email, status, plan_key, plan FROM subscriptions")).mappings().all()
        subscriber_emails = {
            ((row.get("customer_email") or row.get("email") or "").strip().lower()): row
            for row in subs
            if (row.get("customer_email") or row.get("email"))
        }

        customer_targets = []
        client_targets = []
        company_targets = []

        for customer in seed_customers:
            email = (customer.get("email") or "").strip().lower()
            subscribed = email in subscriber_emails
            score = _recruit_score(customer.get("name", ""), email, subscribed=subscribed)
            payload = {
                "id": customer.get("id"),
                "name": customer.get("name"),
                "contact": customer.get("contact"),
                "phone": customer.get("phone"),
                "email": customer.get("email"),
                "fit_score": score,
                "priority": "high" if score >= 76 else ("medium" if score >= 62 else "low"),
                "status": "subscriber" if subscribed else "prospect",
            }
            customer_targets.append(payload)
            if not subscribed:
                client_targets.append({
                    **payload,
                    "recommended_pitch": (
                        "Offer a 14-day AI dispatch pilot with weekly ROI review."
                        if score >= 75
                        else "Offer a quick-start onboarding plus starter plan discount."
                    ),
                })

        for company in companies:
            email = (company.get("email") or "").strip().lower()
            score = _recruit_score(company.get("company_name", ""), email)
            company_targets.append(
                {
                    "id": company.get("id"),
                    "company_name": company.get("company_name"),
                    "owner_name": company.get("owner_name"),
                    "phone": company.get("phone"),
                    "email": company.get("email"),
                    "industry": company.get("industry"),
                    "fit_score": score,
                    "priority": "high" if score >= 76 else ("medium" if score >= 62 else "low"),
                }
            )

        customer_targets.sort(key=lambda row: row.get("fit_score", 0), reverse=True)
        company_targets.sort(key=lambda row: row.get("fit_score", 0), reverse=True)
        client_targets.sort(key=lambda row: row.get("fit_score", 0), reverse=True)

        prompt = (
            "You are a logistics growth strategist. "
            f"Customer prospects: {len(customer_targets)}. "
            f"Company prospects: {len(company_targets)}. "
            f"Client prospects: {len(client_targets)}. "
            "Provide a concise 3-step recruiting strategy for this week in plain English."
        )

        try:
            recruiting_plan = await ai_service.call_ai(prompt, temperature=0.25)
        except Exception:
            recruiting_plan = (
                "1) Prioritize high-fit prospects and schedule short ROI demos. "
                "2) Launch a time-boxed pilot offer for medium-fit leads. "
                "3) Follow up with weekly success metrics to convert and retain accounts."
            )

        return {
            "status": "success",
            "customer_targets": customer_targets[:20],
            "company_targets": company_targets[:20],
            "client_targets": client_targets[:20],
            "recruiting_plan": recruiting_plan,
        }
    except Exception as exc:
        logger.error(f"Recruiter intelligence error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        db.close()

@router.get("/earnings/{company_id}")
async def get_earnings(company_id: int):
    """Get AI-powered earnings summary for a company"""
    db = SessionLocal()
    try:
        # Total revenue from completed jobs
        total_revenue = (
            db.query(func.coalesce(func.sum(JobModel.price), 0))
            .filter(JobModel.company_id == company_id, JobModel.status == "Completed")
            .scalar()
        )

        # Count of completed jobs
        completed_jobs = (
            db.query(func.count(JobModel.id))
            .filter(JobModel.company_id == company_id, JobModel.status == "Completed")
            .scalar()
        )

        # Count of pending jobs (potential revenue)
        pending_jobs_count = (
            db.query(func.count(JobModel.id))
            .filter(JobModel.company_id == company_id, JobModel.status.notin_(["Completed", "Cancelled"]))
            .scalar()
        )

        pending_revenue = (
            db.query(func.coalesce(func.sum(JobModel.price), 0))
            .filter(JobModel.company_id == company_id, JobModel.status.notin_(["Completed", "Cancelled"]))
            .scalar()
        )

        # Average job value
        avg_job_value = (
            db.query(func.coalesce(func.avg(JobModel.price), 0))
            .filter(JobModel.company_id == company_id, JobModel.status == "Completed")
            .scalar()
        )

        total_revenue = float(total_revenue) if total_revenue else 0.0
        pending_revenue = float(pending_revenue) if pending_revenue else 0.0
        avg_job_value = float(avg_job_value) if avg_job_value else 0.0

        return {
            "status": "success",
            "earnings": {
                "total_revenue": total_revenue,
                "completed_jobs": completed_jobs or 0,
                "pending_jobs": pending_jobs_count or 0,
                "pending_revenue": pending_revenue,
                "average_job_value": round(avg_job_value, 2),
                "projected_revenue": total_revenue + pending_revenue,
            },
        }
    except Exception as e:
        logger.error(f"Earnings calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/accountant-summary")
async def accountant_summary(company_id: Optional[int] = None):
    """Return AI-assisted accounting summary across jobs and billing signals."""
    db = SessionLocal()
    try:
        completed_query = db.query(JobModel).filter(JobModel.status == "Completed")
        active_query = db.query(JobModel).filter(JobModel.status.notin_(["Completed", "Cancelled"]))
        if company_id is not None:
            completed_query = completed_query.filter(JobModel.company_id == company_id)
            active_query = active_query.filter(JobModel.company_id == company_id)

        total_revenue = completed_query.with_entities(func.coalesce(func.sum(JobModel.price), 0)).scalar() or 0
        completed_jobs = completed_query.with_entities(func.count(JobModel.id)).scalar() or 0
        pending_revenue = active_query.with_entities(func.coalesce(func.sum(JobModel.price), 0)).scalar() or 0
        pending_jobs = active_query.with_entities(func.count(JobModel.id)).scalar() or 0

        avg_job_value = round(float(total_revenue) / max(int(completed_jobs), 1), 2) if completed_jobs else 0

        sub_rows = db.execute(
            text("SELECT status, COUNT(*) AS cnt FROM subscriptions GROUP BY status")
        ).mappings().all()
        subscription_status_counts = {
            str(row.get("status") or "unknown"): int(row.get("cnt") or 0)
            for row in sub_rows
        }

        prompt = (
            "You are an AI accountant for a logistics company. "
            f"Completed revenue: {float(total_revenue):.2f}. "
            f"Pending revenue: {float(pending_revenue):.2f}. "
            f"Completed jobs: {int(completed_jobs)}. Pending jobs: {int(pending_jobs)}. "
            f"Average job value: {avg_job_value}. "
            f"Subscription statuses: {subscription_status_counts}. "
            "Provide 3 concise actions to improve cash flow, margin, and billing reliability."
        )

        try:
            recommendations = await ai_service.call_ai(prompt, temperature=0.2)
        except Exception:
            recommendations = (
                "1) Prioritize invoicing and collection workflows for high-value pending jobs. "
                "2) Reduce low-margin routes and increase route density on active lanes. "
                "3) Run weekly billing audits and reactivate inactive subscriptions with targeted offers."
            )

        utilization_ratio = 0
        if (int(completed_jobs) + int(pending_jobs)) > 0:
            utilization_ratio = round(
                int(completed_jobs) / (int(completed_jobs) + int(pending_jobs)),
                2,
            )

        return {
            "status": "success",
            "summary": {
                "company_id": company_id,
                "total_revenue": float(total_revenue),
                "pending_revenue": float(pending_revenue),
                "completed_jobs": int(completed_jobs),
                "pending_jobs": int(pending_jobs),
                "average_job_value": avg_job_value,
                "subscription_status_counts": subscription_status_counts,
                "utilization_ratio": utilization_ratio,
            },
            "recommendations": recommendations,
        }
    except Exception as exc:
        logger.error(f"Accountant summary error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        db.close()


@router.get("/logistics-manager")
async def logistics_manager(company_id: Optional[int] = None):
    """Return AI-powered logistics operations summary and action plan."""
    db = SessionLocal()
    try:
        jobs_query = db.query(JobModel)
        drivers_query = db.query(DriverModel)
        if company_id is not None:
            jobs_query = jobs_query.filter(JobModel.company_id == company_id)
            drivers_query = drivers_query.filter(DriverModel.company_id == company_id)

        total_jobs = jobs_query.with_entities(func.count(JobModel.id)).scalar() or 0
        completed_jobs = jobs_query.filter(JobModel.status == "Completed").with_entities(func.count(JobModel.id)).scalar() or 0
        waiting_jobs = jobs_query.filter(JobModel.status == "Waiting").with_entities(func.count(JobModel.id)).scalar() or 0
        active_jobs = jobs_query.filter(JobModel.status.notin_(["Completed", "Cancelled", "Waiting"]))\
            .with_entities(func.count(JobModel.id)).scalar() or 0

        active_drivers = drivers_query.with_entities(func.count(DriverModel.id)).scalar() or 0

        completion_rate = round((int(completed_jobs) / max(int(total_jobs), 1)) * 100, 1) if total_jobs else 0.0
        backlog_pressure = int(waiting_jobs) + int(active_jobs)

        plan_prompt = (
            "You are an AI logistics manager. "
            f"Total jobs: {int(total_jobs)}. "
            f"Completed jobs: {int(completed_jobs)}. "
            f"Waiting jobs: {int(waiting_jobs)}. "
            f"In-flight jobs: {int(active_jobs)}. "
            f"Active drivers: {int(active_drivers)}. "
            f"Completion rate: {completion_rate}%. "
            "Provide a concise operations action plan with 3 priorities for dispatch, fleet utilization, and service reliability."
        )

        try:
            action_plan = await ai_service.call_ai(plan_prompt, temperature=0.25)
        except Exception:
            action_plan = (
                "1) Dispatch waiting jobs by priority and nearest available capacity first. "
                "2) Rebalance driver utilization to reduce idle time and bottlenecks. "
                "3) Review delayed jobs every 2 hours and trigger proactive customer updates."
            )

        return {
            "status": "success",
            "summary": {
                "company_id": company_id,
                "total_jobs": int(total_jobs),
                "completed_jobs": int(completed_jobs),
                "waiting_jobs": int(waiting_jobs),
                "active_jobs": int(active_jobs),
                "active_drivers": int(active_drivers),
                "completion_rate": completion_rate,
                "backlog_pressure": backlog_pressure,
            },
            "action_plan": action_plan,
        }
    except Exception as exc:
        logger.error(f"Logistics manager error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        db.close()


# ============= Health Check =============

@router.get("/health")
async def health_check():
    """Health check for AI services"""
    ai_runtime = ai_service.get_health_status()
    overall_status = "healthy" if ai_runtime["active_provider"] or ai_runtime["mock_mode"] else "degraded"

    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "services": {
            "route_optimizer": "active",
            "dispatch_service": "active",
            "maintenance_service": "active",
            "driver_analytics": "active",
            "forecasting_service": "active",
            "chatbot": "active",
            "ai_runtime": ai_runtime,
        },
    }
