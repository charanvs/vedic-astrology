"""Apply database migrations (alembic upgrade head) using the settings in .env.

Run from the application root (cPanel > Setup Python App > "Execute python script": deploy/migrate.py)
or over SSH:  python deploy/migrate.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402

if __name__ == "__main__":
    command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
    print("Database is up to date.")
