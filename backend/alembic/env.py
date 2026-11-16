import os
from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config,pool
from app.core.config import get_settings
from app.db.base import Base
import app.models  # noqa: F401
config=context.config
if config.config_file_name:fileConfig(config.config_file_name)
target_metadata=Base.metadata
url=get_settings().database_url(migration=not bool(os.getenv("ALEMBIC_USE_TEST_DB")),test=bool(os.getenv("ALEMBIC_USE_TEST_DB")))
config.set_main_option("sqlalchemy.url",url.render_as_string(hide_password=False).replace("%","%%"))
def run_migrations_offline():
 context.configure(url=url,target_metadata=target_metadata,literal_binds=True,dialect_opts={"paramstyle":"named"},compare_type=True)
 with context.begin_transaction():context.run_migrations()
def run_migrations_online():
 connectable=engine_from_config(config.get_section(config.config_ini_section),prefix="sqlalchemy.",poolclass=pool.NullPool)
 with connectable.connect() as connection:
  context.configure(connection=connection,target_metadata=target_metadata,compare_type=True)
  with context.begin_transaction():context.run_migrations()
run_migrations_offline() if context.is_offline_mode() else run_migrations_online()
