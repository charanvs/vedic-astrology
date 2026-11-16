"""authentication, sessions, audit, and rate limiting

Revision ID: 20261115_01
Revises: 20261112_02
"""
from alembic import op
import sqlalchemy as sa

revision="20261115_01";down_revision="20261112_02";branch_labels=None;depends_on=None
opts={"mysql_engine":"InnoDB","mysql_charset":"utf8mb4","mysql_collate":"utf8mb4_unicode_ci"}

def upgrade():
    op.add_column("users",sa.Column("password_hash",sa.String(255),nullable=True))
    op.add_column("users",sa.Column("email_verified_at",sa.DateTime(),nullable=True))
    op.add_column("users",sa.Column("role",sa.String(20),nullable=False,server_default="user"))
    op.add_column("users",sa.Column("last_login_at",sa.DateTime(),nullable=True))
    op.add_column("users",sa.Column("deletion_requested_at",sa.DateTime(),nullable=True))
    op.create_table("auth_sessions",
      sa.Column("id",sa.Integer(),primary_key=True),sa.Column("public_id",sa.String(36),nullable=False),
      sa.Column("token_hash",sa.String(64),nullable=False),sa.Column("csrf_hash",sa.String(64),nullable=False),
      sa.Column("user_id",sa.Integer(),nullable=False),sa.Column("created_at",sa.DateTime(),nullable=False),
      sa.Column("last_activity_at",sa.DateTime(),nullable=False),sa.Column("expires_at",sa.DateTime(),nullable=False),
      sa.Column("absolute_expires_at",sa.DateTime(),nullable=False),sa.Column("revoked_at",sa.DateTime()),
      sa.Column("ip_hash",sa.String(64)),sa.Column("user_agent",sa.String(255)),
      sa.ForeignKeyConstraint(["user_id"],["users.id"],ondelete="CASCADE"),sa.UniqueConstraint("public_id"),sa.UniqueConstraint("token_hash"),**opts)
    op.create_index("ix_auth_sessions_public_id","auth_sessions",["public_id"]);op.create_index("ix_auth_sessions_token_hash","auth_sessions",["token_hash"]);op.create_index("ix_auth_sessions_user_id","auth_sessions",["user_id"]);op.create_index("ix_auth_sessions_expires_at","auth_sessions",["expires_at"]);op.create_index("ix_auth_sessions_user_active","auth_sessions",["user_id","revoked_at","expires_at"])
    op.create_table("account_tokens",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("user_id",sa.Integer(),nullable=False),sa.Column("purpose",sa.String(32),nullable=False),sa.Column("token_hash",sa.String(64),nullable=False),sa.Column("created_at",sa.DateTime(),nullable=False),sa.Column("expires_at",sa.DateTime(),nullable=False),sa.Column("used_at",sa.DateTime()),sa.ForeignKeyConstraint(["user_id"],["users.id"],ondelete="CASCADE"),sa.UniqueConstraint("token_hash"),**opts)
    op.create_index("ix_account_tokens_user_id","account_tokens",["user_id"]);op.create_index("ix_account_tokens_token_hash","account_tokens",["token_hash"]);op.create_index("ix_account_tokens_expires_at","account_tokens",["expires_at"]);op.create_index("ix_account_tokens_user_purpose","account_tokens",["user_id","purpose","used_at"])
    op.create_table("audit_events",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("user_id",sa.Integer()),sa.Column("event_type",sa.String(64),nullable=False),sa.Column("outcome",sa.String(20),nullable=False),sa.Column("request_id",sa.String(36)),sa.Column("ip_hash",sa.String(64)),sa.Column("detail",sa.String(255)),sa.Column("created_at",sa.DateTime(),nullable=False),sa.ForeignKeyConstraint(["user_id"],["users.id"],ondelete="SET NULL"),**opts)
    op.create_index("ix_audit_events_event_type","audit_events",["event_type"]);op.create_index("ix_audit_events_created_at","audit_events",["created_at"]);op.create_index("ix_audit_events_user_created","audit_events",["user_id","created_at"])
    op.create_table("rate_limit_counters",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("scope",sa.String(64),nullable=False),sa.Column("key_hash",sa.String(64),nullable=False),sa.Column("window_started_at",sa.DateTime(),nullable=False),sa.Column("count",sa.Integer(),nullable=False,server_default="1"),sa.Column("expires_at",sa.DateTime(),nullable=False),sa.UniqueConstraint("scope","key_hash","window_started_at",name="uq_rate_limit_window"),**opts)
    op.create_index("ix_rate_limit_counters_expires_at","rate_limit_counters",["expires_at"])

def downgrade():
    op.drop_table("rate_limit_counters");op.drop_table("audit_events");op.drop_table("account_tokens");op.drop_table("auth_sessions")
    for column in ("deletion_requested_at","last_login_at","role","email_verified_at","password_hash"):op.drop_column("users",column)
