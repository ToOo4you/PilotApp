from fastapi import FastAPI
from backend.database.db import engine
from backend.database.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Pilot App API Running"}
@app.get("/drivers")
def get_drivers():
    return[]