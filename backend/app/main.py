from fastapi import FastAPI
from backend.database.db import engine, SessionLocal
from backend.database.models import Base, Company
from backend.routes.companies import router as companies_router
from backend.routes.drivers import router as drivers_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(companies_router)
app.include_router(drivers_router)

@app.get("/")
def home():
    return {"message": "Pilot App API Running"}


def get_companies():
    db = SessionLocal()

    companies = db.query(Company).all()

    results = []

    for company in companies:
        results.append(
            {
                "company_name": company.company_name,
                "owner_name": company.owner_name,
                "industy": company.industry
             }
        )

    db.close()

    return results