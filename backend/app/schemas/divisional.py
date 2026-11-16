from typing import Literal

from pydantic import BaseModel

from app.schemas.astrology import CalculationRequest, CalculationSettingsResponse


class DivisionalCalculationRequest(CalculationRequest):
    chart_type: Literal["D9", "D10"]


class DivisionalChartResponse(BaseModel):
    chart_type: Literal["D9", "D10"]
    chart_name: str
    primary_use: str
    birth_datetime: dict
    location: dict
    settings: CalculationSettingsResponse
    julian_day_ut: float
    julian_day_calendar: str
    ayanamsa: dict
    lagna: dict
    planets: list[dict]
    houses: list[dict]
    whole_sign_houses: list[dict]
    engine: dict
    warnings: list[str]
    calculation: dict


class DivisionalConfigResponse(BaseModel):
    supported_charts: list[dict]
    system: str
    zodiac: str
    ayanamsa: str
    node_convention: str
    house_system: str
    boundary_policy: str
    public_deployment_blocked: bool = False
