from fastapi import APIRouter
from pydantic import BaseModel

from backend.database.db import SessionLocal
from backend.database.models import Company


router = APIRouter(prefix="/companies", tags=["Companies"])


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
    companies = db.query(Company).all()
    db.close()
    return companies


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