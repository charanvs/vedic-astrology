"""user preferences: theme, report language, dasha convention, matching ruleset

Revision ID: 20261115_02
Revises: 20261115_01
"""
from alembic import op
import sqlalchemy as sa

revision="20261115_02";down_revision="20261115_01";branch_labels=None;depends_on=None

def upgrade():
    op.add_column("users",sa.Column("pref_theme",sa.String(10),nullable=True))
    op.add_column("users",sa.Column("pref_report_language",sa.String(2),nullable=True))
    op.add_column("users",sa.Column("pref_dasha_year_convention",sa.String(20),nullable=True))
    op.add_column("users",sa.Column("pref_matching_ruleset",sa.String(80),nullable=True))

def downgrade():
    for column in ("pref_matching_ruleset","pref_dasha_year_convention","pref_report_language","pref_theme"):op.drop_column("users",column)
