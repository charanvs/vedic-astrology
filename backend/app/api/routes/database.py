import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.models import BirthProfile, Location, User
from app.schemas.database import (
    BirthProfileCreate, BirthProfileRead, BirthProfileUpdate,
    BirthTimeValidationRequest, BirthTimeValidationResponse,
    LocationCreate, LocationRead, LocationUpdate,
)
from app.services.birth_time import BirthTimeError, BirthTimeResolution, resolve_birth_time
from app.core.security import current_user, require_csrf

logger = logging.getLogger(__name__)
router = APIRouter(tags=["database"])


@router.get("/db-health")
def db_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except SQLAlchemyError as exc:
        logger.exception("Database health check failed", exc_info=exc)
        raise HTTPException(503, "Database unavailable") from exc


def commit(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, message) from exc


@router.post("/locations", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
def create_location(payload: LocationCreate, context = Depends(require_csrf), db: Session = Depends(get_db)):
    item = Location(**payload.model_dump())
    db.add(item)
    commit(db, "Location violates a data constraint")
    db.refresh(item)
    return item


@router.get("/locations", response_model=list[LocationRead])
def list_locations(
    response: Response,
    search: str | None = Query(None, max_length=150),
    country: str | None = Query(None, max_length=150),
    state_filter: str | None = Query(None, alias="state", max_length=150),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    statement = select(Location)
    count_statement = select(func.count(Location.id))
    filters = []
    if search:
        term = f"%{search.strip()}%"
        filters.append(or_(Location.city.ilike(term), Location.state.ilike(term), Location.country.ilike(term)))
    if country:
        filters.append(Location.country.ilike(country.strip()))
    if state_filter:
        filters.append(Location.state.ilike(state_filter.strip()))
    if filters:
        statement = statement.where(*filters)
        count_statement = count_statement.where(*filters)
    response.headers["X-Total-Count"] = str(db.scalar(count_statement) or 0)
    return list(db.scalars(statement.order_by(Location.city, Location.state, Location.country, Location.id).offset(offset).limit(limit)))


@router.get("/locations/{location_id}", response_model=LocationRead)
def get_location(location_id: int, db: Session = Depends(get_db)):
    if not (item := db.get(Location, location_id)):
        raise HTTPException(404, "Location not found")
    return item


@router.patch("/locations/{location_id}", response_model=LocationRead)
def update_location(location_id: int, payload: LocationUpdate, context = Depends(require_csrf), db: Session = Depends(get_db)):
    if not (item := db.get(Location, location_id)):
        raise HTTPException(404, "Location not found")
    changes = payload.model_dump(exclude_unset=True)
    protected = {"latitude", "longitude", "timezone"}.intersection(changes)
    referenced = db.scalar(select(func.count(BirthProfile.id)).where(BirthProfile.location_id == location_id)) or 0
    if protected and referenced:
        raise HTTPException(409, "Coordinates and timezone cannot be changed while the location is referenced by birth profiles")
    for key, value in changes.items():
        setattr(item, key, value)
    commit(db, "Location update violates a data constraint")
    db.refresh(item)
    return item


def check_refs(db: Session, location_id: int, user_id: int | None = None) -> Location:
    if not (location := db.get(Location, location_id)):
        raise HTTPException(422, "location_id does not reference an existing location")
    if user_id is not None and not db.get(User, user_id):
        raise HTTPException(422, "user_id does not reference an existing user")
    return location


def apply_resolution(values: dict, location: Location) -> None:
    if values.get("birth_time_unknown"):
        values.update(birth_time=None, birth_time_utc=None, utc_offset_minutes=None, timezone_resolution_status="unknown_time", timezone_fold=None)
        return
    try:
        result = resolve_birth_time(values["birth_date"], values["birth_time"], location.timezone, values.get("timezone_fold"))
    except BirthTimeError as exc:
        raise HTTPException(422, str(exc)) from exc
    values.update(
        birth_time_utc=result.utc_datetime.replace(tzinfo=None) if result.utc_datetime else None,
        utc_offset_minutes=result.utc_offset_minutes,
        timezone_resolution_status=result.status,
        timezone_fold=result.fold,
    )


@router.post("/birth-time/validate", response_model=BirthTimeValidationResponse)
def validate_birth_time(payload: BirthTimeValidationRequest):
    try:
        result = resolve_birth_time(payload.birth_date, payload.birth_time, payload.timezone, payload.fold)
    except BirthTimeError as exc:
        raise HTTPException(422, str(exc)) from exc
    return resolution_response(result)


def resolution_response(result: BirthTimeResolution) -> BirthTimeValidationResponse:
    return BirthTimeValidationResponse(
        local_datetime=result.local_datetime,
        utc_datetime=result.utc_datetime,
        utc_offset_minutes=result.utc_offset_minutes,
        timezone=result.timezone,
        resolution_status=result.status,
        fold=result.fold,
        candidate_offset_minutes=list(result.candidate_offset_minutes),
    )


@router.post("/birth-profiles", response_model=BirthProfileRead, status_code=201)
def create_profile(payload: BirthProfileCreate, context = Depends(require_csrf), db: Session = Depends(get_db)):
    location = check_refs(db, payload.location_id)
    values = payload.model_dump()
    values["user_id"] = context.user.id
    apply_resolution(values, location)
    item = BirthProfile(**values)
    db.add(item)
    commit(db, "Birth profile violates a data constraint")
    db.refresh(item)
    return item


@router.get("/birth-profiles", response_model=list[BirthProfileRead])
def list_profiles(
    response: Response,
    search: str | None = Query(None, max_length=150),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    statement = select(BirthProfile).options(joinedload(BirthProfile.location)).where(BirthProfile.user_id == user.id)
    count_statement = select(func.count(BirthProfile.id)).where(BirthProfile.user_id == user.id)
    if search:
        term = f"%{search.strip()}%"
        statement = statement.where(BirthProfile.full_name.ilike(term))
        count_statement = count_statement.where(BirthProfile.full_name.ilike(term))
    response.headers["X-Total-Count"] = str(db.scalar(count_statement) or 0)
    return list(db.scalars(statement.order_by(BirthProfile.id.desc()).offset(offset).limit(limit)))


@router.get("/birth-profiles/{profile_id}", response_model=BirthProfileRead)
def get_profile(profile_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = db.scalar(select(BirthProfile).options(joinedload(BirthProfile.location)).where(BirthProfile.id == profile_id, BirthProfile.user_id == user.id))
    if not item:
        raise HTTPException(404, "Birth profile not found")
    return item


@router.patch("/birth-profiles/{profile_id}", response_model=BirthProfileRead)
def update_profile(profile_id: int, payload: BirthProfileUpdate, context = Depends(require_csrf), db: Session = Depends(get_db)):
    item = db.scalar(select(BirthProfile).options(joinedload(BirthProfile.location)).where(BirthProfile.id == profile_id, BirthProfile.user_id == context.user.id))
    if not item:
        raise HTTPException(404, "Birth profile not found")
    changes = payload.model_dump(exclude_unset=True)
    location = check_refs(db, changes.get("location_id", item.location_id))
    unknown = changes.get("birth_time_unknown", item.birth_time_unknown)
    known_time = changes.get("birth_time", item.birth_time)
    if unknown:
        changes["birth_time"] = None
    elif known_time is None:
        raise HTTPException(422, "birth_time is required when birth_time_unknown is false")
    resolved_values = {
        "birth_date": changes.get("birth_date", item.birth_date),
        "birth_time": changes.get("birth_time", item.birth_time),
        "birth_time_unknown": unknown,
        "timezone_fold": changes.get("timezone_fold", item.timezone_fold),
    }
    apply_resolution(resolved_values, location)
    changes.update({key: resolved_values[key] for key in ("birth_time", "birth_time_utc", "utc_offset_minutes", "timezone_resolution_status", "timezone_fold")})
    for key, value in changes.items():
        setattr(item, key, value)
    commit(db, "Birth profile violates a data constraint")
    db.refresh(item)
    return item


@router.delete("/birth-profiles/{profile_id}", status_code=204)
def delete_profile(profile_id: int, context = Depends(require_csrf), db: Session = Depends(get_db)):
    item = db.scalar(select(BirthProfile).where(BirthProfile.id == profile_id, BirthProfile.user_id == context.user.id))
    if not item:
        raise HTTPException(404, "Birth profile not found")
    db.delete(item)
    db.commit()
    return Response(status_code=204)
