from fastapi import APIRouter

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)
customers = [
    {
        "id": 1,
        "name": "ABC Logistics",
        "contact": "John Smith",
        "phone": "(555) 123-4567",
        "email": "dispatch@abclogistics.com"
    }
]

@router.get("/")
def get_customers():
    return customers