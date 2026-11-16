from datetime import date, datetime, time
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.astrology.dasha.settings import DashaYearConvention, DetailLevel
from app.schemas.database import validate_birth_date, validate_timezone


class DashaCalculationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    birth_date: date
    birth_time: time
    timezone: str = Field(min_length=1, max_length=100)
    timezone_fold: int | None = Field(None, ge=0, le=1)
    city: str = Field(min_length=1, max_length=150)
    state: str | None = Field(None, max_length=150)
    country: str = Field(min_length=1, max_length=150)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    full_name: str | None = Field(None, max_length=150)
    year_convention: DashaYearConvention = DashaYearConvention.TROPICAL_365_25
    reference_datetime: datetime | None = None
    detail_level: DetailLevel = DetailLevel.ANTARDASHA

    @field_validator("birth_date")
    @classmethod
    def valid_date(cls, value: date) -> date:
        return validate_birth_date(value)

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        return validate_timezone(value)

    @field_validator("reference_datetime")
    @classmethod
    def aware_reference(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.utcoffset() is None:
            raise ValueError("reference_datetime must include a UTC offset")
        return value


class DashaLocation(BaseModel):
    city: str
    state: str | None
    country: str
    latitude: float
    longitude: float


class DashaProfile(BaseModel):
    id: int | None
    full_name: str | None
    birth_utc: datetime
    birth_local: datetime
    timezone: str
    location: DashaLocation


class BirthMoonInfo(BaseModel):
    sidereal_longitude: Decimal
    rashi: dict
    nakshatra_number: int = Field(ge=1, le=27)
    nakshatra: str
    pada: int = Field(ge=1, le=4)
    lord: str
    position_within_degrees: Decimal
    elapsed_fraction: Decimal
    remaining_fraction: Decimal


class DashaBalanceResponse(BaseModel):
    starting_lord: str
    full_duration_years: Decimal
    elapsed_years: Decimal
    remaining_years: Decimal
    elapsed_days: Decimal
    remaining_days: Decimal
    theoretical_start_utc: datetime
    theoretical_start_local: datetime
    first_mahadasha_end_utc: datetime
    first_mahadasha_end_local: datetime


class DashaPeriodResponse(BaseModel):
    level: str
    lord: str
    planet_identifier: str
    parent_lord: str | None
    start_utc: datetime
    end_utc: datetime
    start_local: datetime
    end_local: datetime
    duration_dasha_years: Decimal
    duration_days: Decimal
    active_at_birth: bool
    active_at_reference: bool
    children: list["DashaPeriodResponse"] = Field(default_factory=list)


class CurrentHierarchyResponse(BaseModel):
    mahadasha: DashaPeriodResponse
    antardasha: DashaPeriodResponse
    pratyantardasha: DashaPeriodResponse
    remaining_seconds: Decimal


class DashaTimelineResponse(BaseModel):
    profile: DashaProfile
    birth_moon: BirthMoonInfo
    balance: DashaBalanceResponse
    reference: dict[str, datetime]
    current: CurrentHierarchyResponse
    mahadashas: list[DashaPeriodResponse]
    settings: dict
    engine: dict
    metadata: dict
    warnings: list[str]

    @model_validator(mode="after")
    def nine_mahadashas(self) -> Self:
        if len(self.mahadashas) != 9:
            raise ValueError("A Vimshottari cycle must contain nine Mahadashas")
        return self


class CurrentDashaResponse(BaseModel):
    profile: DashaProfile
    birth_moon: BirthMoonInfo
    reference: dict[str, datetime]
    current: CurrentHierarchyResponse
    settings: dict
    engine: dict
    metadata: dict
    warnings: list[str]


class DashaConfigResponse(BaseModel):
    available_year_conventions: list[dict]
    default_year_convention: str
    planetary_sequence: list[str]
    mahadasha_durations: dict[str, Decimal]
    total_cycle_years: Decimal
    supported_detail_levels: list[str]
    ayanamsa: str
    zodiac: str
    engine: dict
    interval_semantics: str
    public_deployment_blocked: bool
