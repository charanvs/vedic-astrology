from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator

from app.astrology.julian import MAXIMUM_YEAR, MINIMUM_YEAR
from app.schemas.database import validate_timezone


def validate_panchang_date(value: date) -> date:
    if not MINIMUM_YEAR <= value.year <= MAXIMUM_YEAR:
        raise ValueError(f"date must be between {MINIMUM_YEAR}-01-01 and {MAXIMUM_YEAR}-12-31")
    return value


class PanchangRequest(BaseModel):
    date: date
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str = Field(min_length=1, max_length=100)
    elevation: float = Field(0.0, ge=-500, le=9000)
    city: str = Field("Coordinates", min_length=1, max_length=150)
    state: str | None = Field(None, max_length=150)
    country: str = Field("", max_length=150)

    @field_validator("date")
    @classmethod
    def valid_date(cls, value: date) -> date:
        return validate_panchang_date(value)

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        return validate_timezone(value)


class TimestampPair(BaseModel):
    utc: datetime
    local: datetime


class PanchangTransition(BaseModel):
    element: str
    from_name: str
    to_name: str
    utc: datetime
    local: datetime


class ElementNext(BaseModel):
    name: str
    number: int | None = None
    position: int | None = None
    display_name: str | None = None
    paksha: str | None = None
    lord: str | None = None
    pada: int | None = None
    tithi_number: int | None = None
    half: str | None = None


class TimedElementBase(BaseModel):
    name: str
    active_at_sunrise: bool
    start: TimestampPair
    end: TimestampPair
    next: ElementNext
    transitions: list[PanchangTransition]
    explanation: str


class TithiInfo(TimedElementBase):
    number: int = Field(ge=1, le=30)
    display_name: str
    paksha: str


class NakshatraPanchangInfo(TimedElementBase):
    number: int = Field(ge=1, le=27)
    pada: int = Field(ge=1, le=4)
    lord: str
    longitude_within: float


class YogaInfo(TimedElementBase):
    number: int = Field(ge=1, le=27)


class KaranaInfo(TimedElementBase):
    position: int = Field(ge=1, le=60)
    tithi_number: int = Field(ge=1, le=30)
    half: str


class VaraInfo(BaseModel):
    english_name: str
    name: str
    hindi_name: str
    local_civil_date: date
    day_start: TimestampPair
    day_end: TimestampPair
    explanation: str


class PanchangLocation(BaseModel):
    id: int | None
    city: str
    state: str | None
    country: str
    latitude: float
    longitude: float
    timezone: str
    elevation: float


class SunriseSunsetInfo(BaseModel):
    sunrise: TimestampPair
    sunset: TimestampPair | None
    next_sunrise: TimestampPair
    day_duration_seconds: int | None
    status: str
    convention: str


class PanchangDayInfo(BaseModel):
    start: TimestampPair
    end: TimestampPair
    definition: str


class TimelineEvent(BaseModel):
    event_type: str
    label: str
    utc: datetime
    local: datetime


class DailyPanchangResponse(BaseModel):
    civil_date: date
    location: PanchangLocation
    panchang_day: PanchangDayInfo
    solar: SunriseSunsetInfo
    tithi: TithiInfo
    vara: VaraInfo
    nakshatra: NakshatraPanchangInfo
    yoga: YogaInfo
    karana: KaranaInfo
    timeline: list[TimelineEvent]
    settings: dict
    engine: dict
    warnings: list[str]


class PanchangConfigResponse(BaseModel):
    method: str
    zodiac: str
    ayanamsa: str
    ephemeris: dict
    sunrise_convention: str
    supported_date_range: dict[str, int]
    timezone_handling: str
    panchang_day_definition: str
    public_deployment_blocked: bool = False
