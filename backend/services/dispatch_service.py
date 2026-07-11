"""
Autonomous Dispatch AI Service
Automatically assigns jobs to drivers based on various factors using AI
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from backend.services.ai_service import ai_service

logger = logging.getLogger(__name__)


@dataclass
class Driver:
    """Driver information"""
    id: str
    name: str
    current_location: Dict[str, float]
    available_capacity: float
    license_type: str  # standard, hazmat, oversized
    current_jobs_count: int
    rating: float
    experience_years: int


@dataclass
class Job:
    """Job/Shipment information"""
    id: str
    pickup_location: Dict[str, float]
    delivery_location: Dict[str, float]
    weight: float
    dimensions: Dict[str, float]
    priority: int  # 1-10, 10 = highest
    cargo_type: str
    time_window_start: Optional[str] = None
    time_window_end: Optional[str] = None
    special_requirements: List[str] = None


@dataclass
class DispatchAssignment:
    """Assignment result"""
    job_id: str
    driver_id: str
    driver_name: str
    confidence_score: float
    reason: str
    pickup_eta: str
    delivery_eta: str
    route_optimization_notes: str


class AutonomousDispatchService:
    """AI-powered autonomous dispatch system"""
    
    async def assign_job_to_driver(
        self,
        job: Job,
        available_drivers: List[Driver],
        system_constraints: Dict[str, Any] = None
    ) -> DispatchAssignment:
        """
        Assign a job to the best available driver using AI
        
        Args:
            job: Job to dispatch
            available_drivers: List of available drivers
            system_constraints: System-wide constraints
        
        Returns:
            DispatchAssignment with selected driver and reasoning
        """
        
        # Build driver availability context
        drivers_text = "\n".join([
            f"- Driver: {d.name} (ID: {d.id}, Capacity: {d.available_capacity}, "
            f"License: {d.license_type}, Rating: {d.rating}/5.0, "
            f"Current jobs: {d.current_jobs_count})"
            for d in available_drivers
        ])
        
        special_reqs = f"Special requirements: {', '.join(job.special_requirements)}" if job.special_requirements else ""
        
        prompt = f"""
        Autonomously assign this job to the best driver:
        
        Job Details:
        - ID: {job.id}
        - Priority: {job.priority}/10
        - Weight: {job.weight} kg
        - Cargo type: {job.cargo_type}
        - Pickup: {job.pickup_location}
        - Delivery: {job.delivery_location}
        {special_reqs}
        
        Available Drivers:
        {drivers_text}
        
        System constraints:
        {system_constraints or 'standard operations'}
        
        Select the BEST driver considering:
        1. License type compatibility
        2. Available capacity
        3. Current workload
        4. Experience level
        5. Rating/performance
        6. Distance/location efficiency
        7. Job priority
        
        Return JSON with: driver_id, driver_name, confidence_score (0-100), reason, 
        pickup_eta (HH:MM), delivery_eta (HH:MM), optimization_notes
        """
        
        try:
            response = await ai_service.call_ai(
                prompt,
                provider="openai",
                model="gpt-4",
                temperature=0.3
            )
            
            import json
            result = json.loads(response)
            
            return DispatchAssignment(
                job_id=job.id,
                driver_id=result['driver_id'],
                driver_name=result['driver_name'],
                confidence_score=float(result.get('confidence_score', 0)) / 100,
                reason=result['reason'],
                pickup_eta=result['pickup_eta'],
                delivery_eta=result['delivery_eta'],
                route_optimization_notes=result['optimization_notes']
            )
            
        except Exception as e:
            logger.error(f"Job dispatch failed: {e}")
            raise
    
    async def assign_batch_jobs(
        self,
        jobs: List[Job],
        available_drivers: List[Driver],
        optimization_strategy: str = "balanced"
    ) -> List[DispatchAssignment]:
        """
        Assign multiple jobs to drivers optimally
        
        Args:
            jobs: List of jobs to dispatch
            available_drivers: List of available drivers
            optimization_strategy: "balanced", "maximize_utilization", "minimize_eta"
        
        Returns:
            List of dispatch assignments
        """
        
        jobs_text = "\n".join([
            f"- Job {j.id}: Priority {j.priority}, {j.cargo_type}, "
            f"{j.weight}kg, Pickup: {j.pickup_location}"
            for j in jobs
        ])
        
        prompt = f"""
        Perform batch dispatch assignment for {len(jobs)} jobs to {len(available_drivers)} drivers.
        
        Strategy: {optimization_strategy}
        
        Jobs ({len(jobs)}):
        {jobs_text}
        
        Drivers available: {len(available_drivers)}
        
        Optimize for {optimization_strategy}:
        - balanced: Fair workload distribution
        - maximize_utilization: Maximum driver capacity usage
        - minimize_eta: Fastest total delivery time
        
        Return JSON array with assignments:
        [
          {{
            "job_id": "...",
            "driver_id": "...",
            "confidence": 0-100,
            "reason": "..."
          }},
          ...
        ]
        """
        
        try:
            response = await ai_service.call_ai(
                prompt,
                provider="openai",
                model="gpt-4",
                temperature=0.4
            )
            
            import json
            results = json.loads(response)
            assignments = []
            
            for result in results:
                job = next((j for j in jobs if j.id == result['job_id']), None)
                driver = next((d for d in available_drivers if d.id == result['driver_id']), None)
                
                if job and driver:
                    assignments.append(DispatchAssignment(
                        job_id=result['job_id'],
                        driver_id=result['driver_id'],
                        driver_name=driver.name,
                        confidence_score=float(result.get('confidence', 0)) / 100,
                        reason=result['reason'],
                        pickup_eta="TBD",
                        delivery_eta="TBD",
                        route_optimization_notes=""
                    ))
            
            return assignments
            
        except Exception as e:
            logger.error(f"Batch dispatch failed: {e}")
            raise
    
    async def suggest_reassignment(
        self,
        driver_id: str,
        reason: str,
        alternative_drivers: List[Driver]
    ) -> Optional[DispatchAssignment]:
        """Suggest job reassignment for a driver"""
        
        prompt = f"""
        Suggest job reassignment:
        
        Current driver: {driver_id}
        Reason for reassignment: {reason}
        Alternative drivers available: {len(alternative_drivers)}
        
        Return best alternative with confidence score and reasoning.
        """
        
        try:
            response = await ai_service.call_ai(prompt, model="gpt-3.5-turbo")
            import json
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error(f"Reassignment suggestion failed: {e}")
            return None


dispatch_service = AutonomousDispatchService()
