from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from datetime import datetime
from .db import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    owner_name = Column(String)
    phone = Column(String)
    email = Column(String, unique=True, index=True)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    industry = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    cdl_number = Column(String)
    phone = Column(String)  
    company_id = Column(Integer)

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer)
    driver_id = Column(Integer)
    customer_name = Column(String)
    phone = Column(String)
    pickup = Column(String)
    destination = Column(String)
    vehicle = Column(String)
    status = Column(String, default="Waiting")
    price = Column(Float)


class LogBookEntry(Base):
    __tablename__ = "logbook_entries"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(String, index=True)
    status = Column(String)
    location = Column(String)
    notes = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    email = Column(String, index=True)
    plan = Column(String)  # starter | professional | enterprise
    status = Column(String, default="inactive")  # active | inactive | cancelled | past_due
    stripe_customer_id = Column(String, nullable=True, index=True)
    stripe_subscription_id = Column(String, nullable=True, index=True)
    current_period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BillingSupportRequest(Base):
    __tablename__ = "billing_support_requests"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    transaction_ids = Column(String, nullable=False)
    transaction_dates = Column(String, nullable=False)
    transaction_statuses = Column(String, nullable=False)
    issue = Column(String, nullable=False)
    status = Column(String, default="open", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)