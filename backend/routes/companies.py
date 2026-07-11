from fastapi import APIRouter
from pydantic import BaseModel
import logging

from backend.database.db import SessionLocal
from backend.database.models import Company


router = APIRouter(prefix="/companies", tags=["Companies"])
logger = logging.getLogger(__name__)


class CompanyCreate(BaseModel):
    company_name: str
    owner_name: str
    phone: str
    email: str
    address: str
    city: str
    state: str
    zip_code: str
    industry: str


@router.get("/")
def get_companies():
    db = SessionLocal()
    try:
        companies = db.query(Company).all()
        return [
            {
                "id": c.id,
                "company_name": c.company_name,
                "owner_name": c.owner_name,
                "phone": c.phone,
                "email": c.email,
                "address": c.address,
                "city": c.city,
                "state": c.state,
                "zip_code": c.zip_code,
                "industry": c.industry,
                "created_at": c.created_at,
            }
            for c in companies
        ]
    except Exception as exc:
        logger.exception("Failed to load companies: %s", exc)
        return []
    finally:
        db.close()


@router.post("/")
def create_company(company: CompanyCreate):
    db = SessionLocal()

    new_company = Company(
        company_name=company.company_name,
        owner_name=company.owner_name,
        phone=company.phone,
        email=company.email,
        address=company.address,
        city=company.city,
        state=company.state,
        zip_code=company.zip_code,
        industry=company.industry
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    db.close()

    return new_company