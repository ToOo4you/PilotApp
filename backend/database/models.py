from sqlalchemy import Column, Integer, String
from .db import Base

class Driver(Base):
  __tablename__ = "drivers"

  id = Column(Integer, primary_key=True, index=True)
  first_name = Column(String)
  last_name = Column(String)
  cdl_nuber = Column(String)
  phone = Column(String)