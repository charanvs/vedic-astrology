"""Server self-check for the production deployment. Prints PASS/WARN/FAIL; never prints secrets.

Run from the application root (cPanel > Setup Python App > "Execute python script": deploy/check_server.py)
or over SSH:  python deploy/check_server.py
"""
import os
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
results = []


def check(name, required=True):
    def wrapper(func):
        try:
            detail = func()
            results.append(("PASS", name, detail or ""))
        except Exception as exc:  # noqa: BLE001 - report every failure without stopping
            results.append(("FAIL" if required else "WARN", name, f"{type(exc).__name__}: {exc}"))
            if os.getenv("CHECK_VERBOSE"): traceback.print_exc()
        return func
    return wrapper


@check("Python version is 3.11")
def _():
    if sys.version_info[:2] != (3, 11): raise RuntimeError(f"found {sys.version.split()[0]}; select Python 3.11 in Setup Python App")
    return sys.version.split()[0]


@check(".env settings file present")
def _():
    if not (ROOT / ".env").is_file(): raise FileNotFoundError("create .env from .env.example in the application root")
    return str(ROOT / ".env")


@check("Settings")
def _():
    from app.core.config import get_settings
    s = get_settings()
    problems = []
    if s.environment != "production": problems.append(f"APP_ENV={s.environment} (expected production)")
    if s.base_path != "/astrology": problems.append(f"APP_BASE_PATH={s.base_path!r} (expected /astrology)")
    if not s.session_cookie_secure: problems.append("SESSION_COOKIE_SECURE should be true")
    if not (s.db_name and s.db_user and s.db_password): problems.append("DB_NAME, DB_USER and DB_PASSWORD are required")
    if problems: raise ValueError("; ".join(problems))
    return f"{s.public_url} · admin approval {'on' if s.require_admin_approval else 'off'} · email verification {'on' if s.require_verified_email else 'off'}"


@check("Built website pages (FRONTEND_DIST)")
def _():
    from app.core.config import get_settings
    dist = Path(get_settings().frontend_dist or "")
    if not (ROOT / dist / "index.html").is_file(): raise FileNotFoundError(f"index.html not found under {dist}")
    return str(dist)


@check("AGPL source link (SOURCE_CODE_URL)", required=False)
def _():
    from app.core.config import get_settings
    url = get_settings().source_code_url
    if not url.startswith("https://"): raise ValueError("set SOURCE_CODE_URL to the public repository address before announcing the site")
    return url


@check("Python packages")
def _():
    import a2wsgi, alembic, fastapi, pymysql, sqlalchemy  # noqa: F401
    return f"fastapi {fastapi.__version__}, SQLAlchemy {sqlalchemy.__version__}"


@check("Password hashing (Argon2id)")
def _():
    from app.core.security import hash_password, verify_password
    if not verify_password("deployment-check", hash_password("deployment-check")): raise RuntimeError("hash verification failed")


@check("Astronomy engine (Swiss Ephemeris)")
def _():
    from app.astrology.config import get_calculation_settings
    from app.astrology.ephemeris import Ephemeris
    from app.astrology.julian import utc_to_julian_day
    settings = get_calculation_settings()
    jd = utc_to_julian_day(datetime.now(UTC), settings.calendar).julian_day_ut
    values, _, source = Ephemeris(settings).calculate_ut(jd, "SUN")
    return f"sidereal Sun {values[0]:.4f}° via {source}"


@check("Database connection and schema version")
def _():
    from alembic.config import Config
    from alembic.script import ScriptDirectory
    from sqlalchemy import text
    from app.db.session import SessionLocal
    head = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini"))).get_current_head()
    with SessionLocal() as db:
        current = db.scalar(text("SELECT version_num FROM alembic_version"))
        users = db.scalar(text("SELECT COUNT(*) FROM users"))
    if current != head: raise RuntimeError(f"database is at {current}, code expects {head}; run deploy/migrate.py")
    return f"schema {current}, {users} user account(s)"


@check("PDF reports (WeasyPrint + Pango)", required=False)
def _():
    from weasyprint import HTML
    pdf = HTML(string="<p>नमस्ते ਸਤ ਸ੍ਰੀ ਅਕਾਲ test</p>").write_pdf()
    if not pdf.startswith(b"%PDF-"): raise RuntimeError("renderer returned an invalid file")
    return f"{len(pdf)} byte test PDF"


if __name__ == "__main__":
    width = max(len(name) for _, name, _ in results)
    for status, name, detail in results: print(f"[{status}] {name.ljust(width)}  {detail}")
    failed = sum(status == "FAIL" for status, _, _ in results)
    warned = sum(status == "WARN" for status, _, _ in results)
    print(f"\n{'READY' if not failed else 'NOT READY'}: {failed} failure(s), {warned} warning(s)")
    sys.exit(1 if failed else 0)
