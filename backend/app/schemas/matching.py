from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.astrology.matching.constants import RULESET_ID

Role = Literal["bride", "groom"]


class MatchingMoonPartner(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None, max_length=150)
    role: Role
    moon_sidereal_longitude: Decimal = Field(ge=0, lt=360)


class MatchingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    partner_one: MatchingMoonPartner
    partner_two: MatchingMoonPartner
    ruleset: str = Field(default=RULESET_ID, max_length=80)

    @model_validator(mode="after")
    def distinct_roles(self):
        if self.partner_one.role == self.partner_two.role:
            raise ValueError("Partners must have distinct bride and groom roles")
        return self


class SavedProfilesMatchingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    partner_one_profile_id: int = Field(gt=0)
    partner_two_profile_id: int = Field(gt=0)
    partner_one_role: Role
    partner_two_role: Role
    ruleset: str = Field(default=RULESET_ID, max_length=80)

    @model_validator(mode="after")
    def validate_pair(self):
        if self.partner_one_profile_id == self.partner_two_profile_id:
            raise ValueError("Two different birth profiles are required")
        if self.partner_one_role == self.partner_two_role:
            raise ValueError("Partners must have distinct bride and groom roles")
        return self


class MatchingMoonData(BaseModel):
    sidereal_longitude: Decimal
    degree_in_rashi: Decimal
    rashi_number: int = Field(ge=1, le=12)
    rashi: str
    rashi_lord: str
    nakshatra_number: int = Field(ge=1, le=27)
    nakshatra: str
    pada: int = Field(ge=1, le=4)
    yoni: str
    gana: str
    nadi: str
    precision: Literal["exact", "date_unambiguous"]
    uncertainty_start_utc: str | None = None
    uncertainty_end_utc: str | None = None


class MatchingPartnerResult(BaseModel):
    profile_id: int | None = None
    name: str | None = None
    role: Role
    moon: MatchingMoonData


class KootaScore(BaseModel):
    id: str
    name: str
    score: Decimal
    maximum: Decimal
    partner_one_classification: str
    partner_two_classification: str
    explanation: str
    rule_id: str
    details: dict[str, Any]
    directional: bool


class DoshaObservation(BaseModel):
    id: str
    name: str
    triggered: bool
    triggering_rule: str
    inputs: dict[str, Any]
    exception_evaluated: bool
    explanation: str


class MatchingThreshold(BaseModel):
    value: Decimal
    met: bool
    label: str


class MatchingResult(BaseModel):
    status: Literal["definitive"]
    ruleset: dict[str, Any]
    partners: list[MatchingPartnerResult] = Field(min_length=2, max_length=2)
    kootas: list[KootaScore] = Field(min_length=8, max_length=8)
    total_score: Decimal = Field(ge=0, le=36)
    maximum_score: Decimal = Field(default=Decimal(36))
    percentage: Decimal = Field(ge=0, le=100)
    threshold: MatchingThreshold
    observations: list[DoshaObservation]
    metadata: dict[str, Any]
    warnings: list[str]


class MatchingConfigResponse(BaseModel):
    supported_rulesets: list[dict[str, Any]]
    default_ruleset: str
    koota_maximums: dict[str, Decimal]
    total_maximum: Decimal
    roles: list[str]
    engine: dict[str, Any]
    ayanamsa: str
    public_deployment_blocked: bool


class MatchingRulesResponse(BaseModel):
    ruleset: dict[str, Any]
    classifications: dict[str, Any]
    matrices: dict[str, Any]
    conventions: dict[str, Any]
    sources: list[dict[str, str]]
