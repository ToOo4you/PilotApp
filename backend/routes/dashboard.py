from fastapi import APIRouter

from backend.database.db import SessionLocal
from backend.database.models import Company, Driver


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/{company_id}")
def get_dashboard(company_id: int):
    db = SessionLocal()

    company = db.query(Company).filter(Company.id == company_id).first()
    drivers = db.query(Driver).filter(Driver.company_id == company_id).all()

    db.close()

    return {
        "company": company,
        "driver_count": len(drivers),
        "drivers": drivers,
        "today_jobs": 0,
        "active_jobs": 0,
        "revenue_today": 0
    }