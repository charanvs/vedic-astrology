from datetime import datetime
from typing import Literal
from pydantic import BaseModel

AccountStatus = Literal["pending", "approved", "inactive"]


class AdminUserRead(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    status: AccountStatus
    email_verified: bool
    approved_at: datetime | None
    created_at: datetime
    last_login_at: datetime | None
    deletion_requested_at: datetime | None
    profile_count: int


class AdminSummary(BaseModel):
    pending: int
    approved: int
    inactive: int
    all: int
