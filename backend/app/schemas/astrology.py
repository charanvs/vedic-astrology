from datetime import date, time
from pydantic import BaseModel, Field, field_validator

from app.schemas.database import validate_birth_date, validate_timezone


class CalculationRequest(BaseModel):
    birth_date: date
    birth_time: time
    timezone: str = Field(min_length=1, max_length=100)
    timezone_fold: int | None = Field(None, ge=0, le=1)
    city: str = Field(min_length=1, max_length=150)
    state: str | None = Field(None, max_length=150)
    country: str = Field(min_length=1, max_length=150)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    @field_validator("birth_date")
    @classmethod
    def valid_date(cls, value: date) -> date:
        return validate_birth_date(value)

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        return validate_timezone(value)


class CalculationSettingsResponse(BaseModel):
    zodiac: str
    ayanamsa: str
    ayanamsa_mode: str
    planetary_reference: str
    node_convention: str
    house_system: str
    calendar: str
    ephemeris_source: str
    stationary_threshold: float


class RashiInfo(BaseModel):
    number: int
    name: str
    english_name: str
    hindi_name: str
    longitude_within: float


class NakshatraInfo(BaseModel):
    number: int
    name: str
    pada: int
    longitude_within: float
    lord: str


class PlanetaryPosition(BaseModel):
    identifier: str
    english_name: str
    sanskrit_name: str
    hindi_name: str
    longitude: float
    longitude_formatted: str
    latitude: float | None
    longitude_speed: float | None
    motion: str
    retrograde: bool | None
    rashi: RashiInfo
    nakshatra: NakshatraInfo
    house: int
    calculation_flags: int | None
    ephemeris_source: str
    convention: str


class LagnaInfo(BaseModel):
    longitude: float
    longitude_formatted: str
    rashi: RashiInfo
    method: str
    whole_sign_houses: list[dict]

class ChartHouseInfo(BaseModel):
    house_number: int = Field(ge=1, le=12)
    rashi_number: int = Field(ge=1, le=12)
    rashi_name: str
    rashi_english_name: str
    rashi_hindi_name: str
    planet_identifiers: list[str]
    is_lagna: bool


class AstronomyCalculationResponse(BaseModel):
    birth_datetime: dict
    location: dict
    settings: CalculationSettingsResponse
    julian_day_ut: float
    julian_day_calendar: str
    ayanamsa: dict
    lagna: LagnaInfo
    planets: list[PlanetaryPosition]
    houses: list[ChartHouseInfo]
    whole_sign_houses: list[dict]
    engine: dict
    warnings: list[str]


class CalculationError(BaseModel):
    detail: str


class AstrologyConfigResponse(BaseModel):
    settings: CalculationSettingsResponse
    engine_available: bool
    engine: dict
    supported_bodies: list[str]
    public_deployment_blocked: bool = False
