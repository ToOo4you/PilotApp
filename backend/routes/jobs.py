from fastapi import APIRouter
from pydantic import BaseModel

from backend.database.db import SessionLocal
from backend.database.models import Job


router = APIRouter(prefix="/jobs", tags=["Jobs"])


class JobCreate(BaseModel):
    company_id: int
    driver_id: int
    customer_name: str
    phone: str
    pickup: str
    destination: str
    vehicle: str
    price: float


@router.get("/")
def get_jobs():
    db = SessionLocal()
    jobs = db.query(Job).all()
    db.close()
    return jobs


@router.post("/")
def create_job(job: JobCreate):
    db = SessionLocal()

    new_job = Job(
        company_id=job.company_id,
        driver_id=job.driver_id,
        customer_name=job.customer_name,
        phone=job.phone,
        pickup=job.pickup,
        destination=job.destination,
        vehicle=job.vehicle,
        status="Waiting",
        price=job.price
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    db.close()

    return new_job