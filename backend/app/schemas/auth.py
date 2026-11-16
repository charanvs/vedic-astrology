from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator
from app.astrology.dasha.settings import DashaYearConvention
from app.astrology.matching.constants import RULESET_ID
from app.reports.schemas import Language

class RegisterRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    full_name: str = Field(min_length=1,max_length=150)
    email: EmailStr
    password: str = Field(min_length=12,max_length=128)
    accept_terms: bool
    @field_validator("full_name")
    @classmethod
    def clean_name(cls,value:str)->str:return value.strip()
    @model_validator(mode="after")
    def terms(self):
        if not self.accept_terms: raise ValueError("Terms and privacy notice must be accepted")
        return self
class LoginRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(min_length=1,max_length=128)
class TokenRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    token: str = Field(min_length=32,max_length=512)
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
class ResetPasswordRequest(TokenRequest):
    password: str = Field(min_length=12,max_length=128)
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1,max_length=128)
    new_password: str = Field(min_length=12,max_length=128)
class AccountUpdateRequest(BaseModel):
    full_name: str = Field(min_length=1,max_length=150)
    @field_validator("full_name")
    @classmethod
    def clean_name(cls,value:str)->str:return value.strip()
class DeletionRequest(BaseModel):
    current_password: str = Field(min_length=1,max_length=128)
    confirmation: str
class UserRead(BaseModel):
    id:int;full_name:str;email:str;email_verified:bool;approved:bool=True;is_active:bool;role:str;created_at:datetime;last_login_at:datetime|None=None;deletion_requested_at:datetime|None=None
class PreferencesRead(BaseModel):
    theme: str|None=None
    report_language: str|None=None
    dasha_year_convention: str|None=None
    matching_ruleset: str|None=None
class PreferencesUpdate(BaseModel):
    model_config=ConfigDict(extra="forbid")
    theme: Literal["light","dark","system"]|None=None
    report_language: Language|None=None
    dasha_year_convention: DashaYearConvention|None=None
    matching_ruleset: str|None=Field(default=None,max_length=80)
    @field_validator("matching_ruleset")
    @classmethod
    def known_ruleset(cls,value:str|None)->str|None:
        if value is not None and value!=RULESET_ID: raise ValueError("Unsupported matching ruleset")
        return value
class SessionRead(BaseModel):
    id:str;created_at:datetime;last_activity_at:datetime;expires_at:datetime;current:bool;user_agent:str|None=None
class AuthResponse(BaseModel):
    message:str;user:UserRead|None=None;csrf_token:str|None=None;development_token:str|None=None
