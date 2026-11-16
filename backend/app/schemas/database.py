from datetime import date, datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MINIMUM_BIRTH_DATE = date(1600, 1, 1)


def validate_timezone(value: str) -> str:
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError("timezone must be a valid IANA identifier") from exc
    return value


def validate_birth_date(value: date) -> date:
    if value < MINIMUM_BIRTH_DATE:
        raise ValueError("birth_date must be on or after 1600-01-01")
    if value > date.today():
        raise ValueError("birth_date cannot be in the future")
    return value


class LocationBase(BaseModel):
    city: str = Field(min_length=1, max_length=150)
    state: str | None = Field(None, max_length=150)
    country: str = Field(min_length=1, max_length=150)
    country_code: str | None = Field(None, min_length=2, max_length=2)
    latitude: Decimal = Field(ge=-90, le=90, max_digits=10, decimal_places=7)
    longitude: Decimal = Field(ge=-180, le=180, max_digits=10, decimal_places=7)
    timezone: str = Field(min_length=1, max_length=100)

    @field_validator("city", "state", "country", "timezone")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else value

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        return validate_timezone(value)

    @field_validator("country_code")
    @classmethod
    def upper_code(cls, value: str | None) -> str | None:
        return value.strip().upper() if value else value


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    city: str | None = Field(None, min_length=1, max_length=150)
    state: str | None = Field(None, max_length=150)
    country: str | None = Field(None, min_length=1, max_length=150)
    country_code: str | None = Field(None, min_length=2, max_length=2)
    latitude: Decimal | None = Field(None, ge=-90, le=90, max_digits=10, decimal_places=7)
    longitude: Decimal | None = Field(None, ge=-180, le=180, max_digits=10, decimal_places=7)
    timezone: str | None = Field(None, min_length=1, max_length=100)

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str | None) -> str | None:
        return validate_timezone(value) if value is not None else value

    @field_validator("country_code")
    @classmethod
    def upper_code(cls, value: str | None) -> str | None:
        return value.strip().upper() if value else value


class LocationRead(LocationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class BirthProfileCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: str = Field(min_length=1, max_length=150)
    gender: str | None = Field(None, max_length=50)
    birth_date: date
    birth_time: time | None = None
    birth_time_unknown: bool = False
    location_id: int
    timezone_fold: int | None = Field(None, ge=0, le=1)
    notes: str | None = Field(None, max_length=5000)

    @field_validator("birth_date")
    @classmethod
    def valid_date(cls, value: date) -> date:
        return validate_birth_date(value)

    @field_validator("full_name", "gender")
    @classmethod
    def strip_profile_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else value

    @model_validator(mode="after")
    def valid_time(self):
        if not self.birth_time_unknown and self.birth_time is None:
            raise ValueError("birth_time is required when birth_time_unknown is false")
        if self.birth_time_unknown:
            self.birth_time = None
            self.timezone_fold = None
        return self


class BirthProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: str | None = Field(None, min_length=1, max_length=150)
    gender: str | None = Field(None, max_length=50)
    birth_date: date | None = None
    birth_time: time | None = None
    birth_time_unknown: bool | None = None
    location_id: int | None = None
    timezone_fold: int | None = Field(None, ge=0, le=1)
    notes: str | None = Field(None, max_length=5000)

    @field_validator("birth_date")
    @classmethod
    def valid_date(cls, value: date | None) -> date | None:
        return validate_birth_date(value) if value is not None else value


class BirthProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int | None
    full_name: str
    gender: str | None
    birth_date: date
    birth_time: time | None
    birth_time_unknown: bool
    location_id: int
    birth_time_utc: datetime | None
    utc_offset_minutes: int | None
    timezone_resolution_status: str
    timezone_fold: int | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    location: LocationRead


class BirthTimeValidationRequest(BaseModel):
    birth_date: date
    birth_time: time
    timezone: str = Field(min_length=1, max_length=100)
    fold: int | None = Field(None, ge=0, le=1)

    @field_validator("birth_date")
    @classmethod
    def valid_date(cls, value: date) -> date:
        return validate_birth_date(value)

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        return validate_timezone(value)


class BirthTimeValidationResponse(BaseModel):
    local_datetime: datetime
    utc_datetime: datetime | None
    utc_offset_minutes: int | None
    timezone: str
    resolution_status: str
    fold: int | None
    candidate_offset_minutes: list[int] = Field(default_factory=list)
