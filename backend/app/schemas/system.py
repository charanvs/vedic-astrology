from typing import Literal
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: Literal["ok"]
    application: str
    service: Literal["backend"]

class VersionResponse(BaseModel):
    application: str
    version: str
    environment: str
