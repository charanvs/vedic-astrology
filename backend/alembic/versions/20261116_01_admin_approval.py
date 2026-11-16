"""administrator approval of self-registered accounts

Revision ID: 20261116_01
Revises: 20261115_02
"""
from alembic import op
import sqlalchemy as sa

revision="20261116_01";down_revision="20261115_02";branch_labels=None;depends_on=None

def upgrade():
    op.add_column("users",sa.Column("approved_at",sa.DateTime(),nullable=True))
    op.add_column("users",sa.Column("approved_by_id",sa.Integer(),nullable=True))
    op.create_foreign_key("fk_users_approved_by_id","users","users",["approved_by_id"],["id"],ondelete="SET NULL")
    op.create_index("ix_users_approved_at","users",["approved_at"])
    op.execute("UPDATE users SET approved_at = created_at WHERE role = 'admin'")

def downgrade():
    op.drop_index("ix_users_approved_at","users")
    op.drop_constraint("fk_users_approved_by_id","users",type_="foreignkey")
    for column in ("approved_by_id","approved_at"):op.drop_column("users",column)
