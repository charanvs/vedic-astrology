from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime,ForeignKey,Index,Integer,String,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.base import Base
from app.models.entities import utcnow
TABLE_OPTIONS={"mysql_engine":"InnoDB","mysql_charset":"utf8mb4","mysql_collate":"utf8mb4_unicode_ci"}
class AuthSession(Base):
 __tablename__="auth_sessions";__table_args__=(Index("ix_auth_sessions_user_active","user_id","revoked_at","expires_at"),Index("ix_auth_sessions_public_id","public_id"),Index("ix_auth_sessions_token_hash","token_hash"),UniqueConstraint("public_id"),UniqueConstraint("token_hash"),TABLE_OPTIONS)
 id:Mapped[int]=mapped_column(primary_key=True);public_id:Mapped[str]=mapped_column(String(36));token_hash:Mapped[str]=mapped_column(String(64));csrf_hash:Mapped[str]=mapped_column(String(64));user_id:Mapped[int]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),index=True);created_at:Mapped[datetime]=mapped_column(DateTime,default=utcnow);last_activity_at:Mapped[datetime]=mapped_column(DateTime,default=utcnow);expires_at:Mapped[datetime]=mapped_column(DateTime,index=True);absolute_expires_at:Mapped[datetime]=mapped_column(DateTime);revoked_at:Mapped[datetime|None]=mapped_column(DateTime);ip_hash:Mapped[str|None]=mapped_column(String(64));user_agent:Mapped[str|None]=mapped_column(String(255));user=relationship("User",back_populates="sessions")
class AccountToken(Base):
 __tablename__="account_tokens";__table_args__=(Index("ix_account_tokens_user_purpose","user_id","purpose","used_at"),Index("ix_account_tokens_token_hash","token_hash"),UniqueConstraint("token_hash"),TABLE_OPTIONS)
 id:Mapped[int]=mapped_column(primary_key=True);user_id:Mapped[int]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),index=True);purpose:Mapped[str]=mapped_column(String(32));token_hash:Mapped[str]=mapped_column(String(64));created_at:Mapped[datetime]=mapped_column(DateTime,default=utcnow);expires_at:Mapped[datetime]=mapped_column(DateTime,index=True);used_at:Mapped[datetime|None]=mapped_column(DateTime)
class AuditEvent(Base):
 __tablename__="audit_events";__table_args__=(Index("ix_audit_events_user_created","user_id","created_at"),TABLE_OPTIONS)
 id:Mapped[int]=mapped_column(primary_key=True);user_id:Mapped[int|None]=mapped_column(ForeignKey("users.id",ondelete="SET NULL"));event_type:Mapped[str]=mapped_column(String(64),index=True);outcome:Mapped[str]=mapped_column(String(20));request_id:Mapped[str|None]=mapped_column(String(36));ip_hash:Mapped[str|None]=mapped_column(String(64));detail:Mapped[str|None]=mapped_column(String(255));created_at:Mapped[datetime]=mapped_column(DateTime,default=utcnow,index=True)
class RateLimitCounter(Base):
 __tablename__="rate_limit_counters";__table_args__=(UniqueConstraint("scope","key_hash","window_started_at",name="uq_rate_limit_window"),TABLE_OPTIONS)
 id:Mapped[int]=mapped_column(primary_key=True);scope:Mapped[str]=mapped_column(String(64));key_hash:Mapped[str]=mapped_column(String(64));window_started_at:Mapped[datetime]=mapped_column(DateTime);count:Mapped[int]=mapped_column(Integer,default=1,server_default="1");expires_at:Mapped[datetime]=mapped_column(DateTime,index=True)
