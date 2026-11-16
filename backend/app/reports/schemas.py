from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.astrology.matching.constants import RULESET_ID

Language = Literal["en", "hi", "pa"]
Section = Literal["birth_details", "d1_chart", "planetary_positions", "d9_chart", "d10_chart", "panchang", "dasha", "interpretation", "forecast", "calculation_notes"]

class KundliReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profile_id: int = Field(gt=0)
    report_type: Literal["summary", "comprehensive"] = "summary"
    language: Language = "en"
    sections: list[Section] | None = None
    dasha_year_convention: Literal["365.25_day", "360_day_savana"] = "365.25_day"
    reference_datetime: datetime | None = None
    @model_validator(mode="after")
    def valid_options(self):
        if self.sections is not None and len(self.sections) != len(set(self.sections)):
            raise ValueError("Report sections must not contain duplicates")
        if self.reference_datetime is not None and self.reference_datetime.utcoffset() is None:
            raise ValueError("reference_datetime must include a UTC offset")
        return self

class MatchingReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    partner_one_profile_id: int = Field(gt=0)
    partner_two_profile_id: int = Field(gt=0)
    partner_one_role: Literal["bride", "groom"]
    partner_two_role: Literal["bride", "groom"]
    language: Language = "en"
    ruleset: str = Field(default=RULESET_ID, max_length=80)
    @model_validator(mode="after")
    def valid_pair(self):
        if self.partner_one_profile_id == self.partner_two_profile_id: raise ValueError("Two different profiles are required")
        if self.partner_one_role == self.partner_two_role: raise ValueError("Partner roles must be distinct")
        return self
