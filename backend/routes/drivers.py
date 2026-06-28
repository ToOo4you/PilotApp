from fastapi import APIRouter
from pydantic import BaseModel

from backend.database.db import SessionLocal
from backend.database.models import Driver


router = APIRouter(prefix="/drivers", tags=["Drivers"])


class DriverCreate(BaseModel):
    company_id: int
    first_name: str
    last_name: str
    cdl_number: str
    phone: str


@router.get("/")
def get_drivers():
    db = SessionLocal()
    drivers = db.query(Driver).all()
    db.close()
    return drivers


@router.post("/")
def create_driver(driver: DriverCreate):
    db = SessionLocal()

    new_driver = Driver(
        company_id=driver.company_id,
        first_name=driver.first_name,
        last_name=driver.last_name,
        cdl_number=driver.cdl_number,
        phone=driver.phone
    )

    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    db.close()

    return new_driver