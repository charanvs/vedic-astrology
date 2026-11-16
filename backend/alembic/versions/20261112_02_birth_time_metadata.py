"""add birth profile preference and timezone resolution metadata"""
from alembic import op
import sqlalchemy as sa

revision = "20261112_02"
down_revision = "20261112_01"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("birth_profiles", sa.Column("gender", sa.String(50), nullable=True))
    op.add_column("birth_profiles", sa.Column("birth_time_utc", sa.DateTime(), nullable=True))
    op.add_column("birth_profiles", sa.Column("utc_offset_minutes", sa.SmallInteger(), nullable=True))
    op.add_column("birth_profiles", sa.Column("timezone_resolution_status", sa.String(32), nullable=False, server_default="pending"))
    op.add_column("birth_profiles", sa.Column("timezone_fold", sa.SmallInteger(), nullable=True))
    op.create_check_constraint("ck_birth_profiles_timezone_fold", "birth_profiles", "timezone_fold IS NULL OR timezone_fold IN (0, 1)")
    op.create_check_constraint("ck_birth_profiles_utc_offset", "birth_profiles", "utc_offset_minutes IS NULL OR utc_offset_minutes BETWEEN -1440 AND 1440")


def downgrade():
    op.drop_constraint("ck_birth_profiles_utc_offset", "birth_profiles", type_="check")
    op.drop_constraint("ck_birth_profiles_timezone_fold", "birth_profiles", type_="check")
    op.drop_column("birth_profiles", "timezone_fold")
    op.drop_column("birth_profiles", "timezone_resolution_status")
    op.drop_column("birth_profiles", "utc_offset_minutes")
    op.drop_column("birth_profiles", "birth_time_utc")
    op.drop_column("birth_profiles", "gender")
