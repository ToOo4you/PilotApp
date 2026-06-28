router = APIRouter(prefix="/drivers", tags=["Drivers"])


class DriverCreate(BaseModel):
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