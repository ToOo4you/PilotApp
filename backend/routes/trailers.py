from fastapi import APIRouter

router = APIRouter(
    prefix="/trailers",
    tags=["Trailers"]
)

trailers = [
    {
        "id": 1,
        "number": "TR-501",
        "type": "Flatbed",
        "length": "48 ft",
        "status": "Available"
    }
]

@router.get("/")
def get_trailers():
    return trailers