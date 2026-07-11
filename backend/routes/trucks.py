from fastapi import APIRouter

router = APIRouter(
    prefix="/trucks",
    tags=["Trucks"]
)

trucks = [
    {
        "id": 1,
        "number": "T-101",
        "make": "Peterbilt",
        "model": "579",
        "year": 2023,
        "status": "Available"
    }
]

@router.get("/")
def get_trucks():
    return trucks