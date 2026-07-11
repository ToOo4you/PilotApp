from datetime import datetime, timedelta
from math import radians, sin, cos, asin, sqrt
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import desc

from backend.database.db import SessionLocal
from backend.database.models import LogBookEntry


router = APIRouter(prefix="/ops", tags=["Operations"])


class NavigationRequest(BaseModel):
    origin: str = Field(..., description="Route origin address")
    destination: str = Field(..., description="Route destination address")
    waypoints: List[str] = Field(default_factory=list)


class SpeedLimitRequest(BaseModel):
    latitude: float
    longitude: float


class LogBookEntryCreate(BaseModel):
    driver_id: str
    status: str = Field(..., description="driving, on_duty, off_duty, sleeper")
    location: str
    notes: Optional[str] = ""


def _parse_iso_datetime(value: str) -> datetime:
    normalized = value[:-1] if value.endswith("Z") else value
    return datetime.fromisoformat(normalized)


def _minutes_between(start: datetime, end: datetime) -> int:
    return max(0, int((end - start).total_seconds() // 60))


class DotRegulation(BaseModel):
    code: str
    title: str
    summary: str
    practical_rule: str


class ScaleLocation(BaseModel):
    id: int
    name: str
    state: str
    highway: str
    mile_marker: str
    latitude: float
    longitude: float
    status: str


SPEED_LIMIT_ZONES = [
    {"name": "Urban Corridor", "speed_limit_mph": 55, "latitude": 34.0522, "longitude": -118.2437},
    {"name": "Interstate Standard", "speed_limit_mph": 70, "latitude": 39.7392, "longitude": -104.9903},
    {"name": "Rural Freight Route", "speed_limit_mph": 65, "latitude": 41.8781, "longitude": -87.6298},
]


SCALE_LOCATIONS = [
    ScaleLocation(
        id=1,
        name="I-10 Westbound Weigh Station",
        state="AZ",
        highway="I-10",
        mile_marker="MM 112",
        latitude=32.1472,
        longitude=-110.9480,
        status="open",
    ),
    ScaleLocation(
        id=2,
        name="I-80 Eastbound Port of Entry",
        state="WY",
        highway="I-80",
        mile_marker="MM 7",
        latitude=41.0925,
        longitude=-104.8056,
        status="open",
    ),
    ScaleLocation(
        id=3,
        name="I-95 Commercial Vehicle Check",
        state="NC",
        highway="I-95",
        mile_marker="MM 182",
        latitude=35.7796,
        longitude=-78.6382,
        status="intermittent",
    ),
]


DOT_REGULATIONS = [
    DotRegulation(
        code="49 CFR 395.3",
        title="Hours of Service (Property-Carrying)",
        summary="Drivers may drive max 11 hours after 10 consecutive hours off duty.",
        practical_rule="Do not exceed 14-hour duty window; reset with 10 consecutive hours off.",
    ),
    DotRegulation(
        code="49 CFR 392.2",
        title="Compliance with Traffic Laws",
        summary="Commercial drivers must obey all state/local traffic laws unless federal law preempts.",
        practical_rule="Always follow posted signs including truck-specific restrictions and speed limits.",
    ),
    DotRegulation(
        code="49 CFR 396.13",
        title="Driver Vehicle Inspection",
        summary="Driver must be satisfied vehicle is in safe operating condition before driving.",
        practical_rule="Complete a pre-trip check and record defects before dispatch.",
    ),
]


def _haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 3958.8
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return r * c


@router.post("/navigation/route")
def build_navigation_route(request: NavigationRequest):
    checkpoints = [request.origin, *request.waypoints, request.destination]
    return {
        "status": "success",
        "route": {
            "origin": request.origin,
            "destination": request.destination,
            "waypoints": request.waypoints,
            "checkpoints": checkpoints,
            "distance_miles_estimate": max(25, 52 * max(1, len(checkpoints) - 1)),
            "eta_minutes_estimate": max(35, 60 * max(1, len(checkpoints) - 1)),
            "map_url": f"https://www.openstreetmap.org/search?query={request.destination}",
        },
    }


@router.post("/speed-limits")
def get_speed_limit(request: SpeedLimitRequest):
    nearest = min(
        SPEED_LIMIT_ZONES,
        key=lambda zone: _haversine_miles(
            request.latitude,
            request.longitude,
            zone["latitude"],
            zone["longitude"],
        ),
    )
    distance = _haversine_miles(request.latitude, request.longitude, nearest["latitude"], nearest["longitude"])
    return {
        "status": "success",
        "lookup": {
            "latitude": request.latitude,
            "longitude": request.longitude,
            "nearest_zone": nearest["name"],
            "speed_limit_mph": nearest["speed_limit_mph"],
            "distance_to_zone_miles": round(distance, 2),
        },
    }


@router.get("/dot-regulations")
def get_dot_regulations():
    return {
        "status": "success",
        "regulations": [reg.model_dump() for reg in DOT_REGULATIONS],
    }


@router.get("/scale-locations")
def get_scale_locations(state: Optional[str] = None, highway: Optional[str] = None):
    locations = SCALE_LOCATIONS
    if state:
        locations = [loc for loc in locations if loc.state.lower() == state.lower()]
    if highway:
        locations = [loc for loc in locations if loc.highway.lower() == highway.lower()]

    return {
        "status": "success",
        "count": len(locations),
        "locations": [loc.model_dump() for loc in locations],
    }


@router.get("/logbooks")
def get_logbooks(driver_id: Optional[str] = None):
    db = SessionLocal()
    query = db.query(LogBookEntry)
    if driver_id:
        query = query.filter(LogBookEntry.driver_id == driver_id)

    rows = query.order_by(desc(LogBookEntry.created_at)).all()
    db.close()

    entries = [
        {
            "id": row.id,
            "driver_id": row.driver_id,
            "status": row.status,
            "location": row.location,
            "notes": row.notes,
            "created_at": row.created_at.isoformat() + "Z" if row.created_at else None,
        }
        for row in rows
    ]

    return {
        "status": "success",
        "count": len(entries),
        "entries": entries,
    }


@router.post("/logbooks")
def create_logbook_entry(payload: LogBookEntryCreate):
    db = SessionLocal()
    row = LogBookEntry(
        driver_id=payload.driver_id,
        status=payload.status,
        location=payload.location,
        notes=payload.notes or "",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    db.close()

    entry = {
        "id": row.id,
        "driver_id": row.driver_id,
        "status": row.status,
        "location": row.location,
        "notes": row.notes,
        "created_at": row.created_at.isoformat() + "Z" if row.created_at else datetime.utcnow().isoformat() + "Z",
    }

    return {
        "status": "success",
        "entry": entry,
    }


@router.get("/logbooks/{driver_id}/hos-summary")
def get_hos_summary(driver_id: str):
    db = SessionLocal()
    rows = (
        db.query(LogBookEntry)
        .filter(LogBookEntry.driver_id == driver_id)
        .order_by(LogBookEntry.created_at.asc())
        .all()
    )
    db.close()

    entries = [
        {
            "status": row.status,
            "created_at": row.created_at.isoformat() + "Z" if row.created_at else datetime.utcnow().isoformat() + "Z",
        }
        for row in rows
    ]

    now = datetime.utcnow()
    window_start = now - timedelta(hours=24)

    driving_minutes_24h = 0
    on_duty_minutes_24h = 0

    if entries:
        for index, current in enumerate(entries):
            start = _parse_iso_datetime(current["created_at"])
            end = now
            if index + 1 < len(entries):
                end = _parse_iso_datetime(entries[index + 1]["created_at"])

            if end <= window_start:
                continue

            effective_start = max(start, window_start)
            minutes = _minutes_between(effective_start, end)
            status = (current["status"] or "").lower()

            if status == "driving":
                driving_minutes_24h += minutes
                on_duty_minutes_24h += minutes
            elif status == "on_duty":
                on_duty_minutes_24h += minutes

    violations = []
    if driving_minutes_24h > 11 * 60:
        violations.append("Exceeded 11-hour driving limit in rolling 24-hour window")
    if on_duty_minutes_24h > 14 * 60:
        violations.append("Exceeded 14-hour on-duty limit in rolling 24-hour window")

    return {
        "status": "success",
        "driver_id": driver_id,
        "window": "last_24_hours",
        "totals": {
            "driving_minutes": driving_minutes_24h,
            "on_duty_minutes": on_duty_minutes_24h,
            "remaining_driving_minutes": max(0, 11 * 60 - driving_minutes_24h),
            "remaining_on_duty_minutes": max(0, 14 * 60 - on_duty_minutes_24h),
        },
        "violations": violations,
        "compliant": len(violations) == 0,
        "advisory": "This is an operational estimate. Confirm with certified ELD records for compliance decisions.",
    }
