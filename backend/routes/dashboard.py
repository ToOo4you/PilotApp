from datetime import date, datetime, timezone

from fastapi import APIRouter
from sqlalchemy import func

from backend.database.db import SessionLocal
from backend.database.models import Company, Driver, Job


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/{company_id}")
def get_dashboard(company_id: int):
    db = SessionLocal()
    try:
        company = db.query(Company).filter(Company.id == company_id).first()
        drivers = db.query(Driver).filter(Driver.company_id == company_id).all()

        # Calculate today's jobs
        today_jobs = (
            db.query(Job)
            .filter(Job.company_id == company_id)
            .count()
        )

        # Active (non-completed) jobs
        active_jobs = (
            db.query(Job)
            .filter(Job.company_id == company_id)
            .filter(Job.status.notin_(["Completed", "Cancelled"]))
            .count()
        )

        # Revenue from completed jobs
        revenue_result = (
            db.query(func.coalesce(func.sum(Job.price), 0))
            .filter(Job.company_id == company_id)
            .filter(Job.status == "Completed")
            .scalar()
        )
        revenue_today = float(revenue_result) if revenue_result else 0.0

        return {
            "company": company,
            "driver_count": len(drivers),
            "drivers": drivers,
            "today_jobs": today_jobs,
            "active_jobs": active_jobs,
            "revenue_today": revenue_today,
        }
    finally:
        db.close()