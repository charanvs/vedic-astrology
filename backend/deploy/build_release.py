"""Build the deployment pack for cPanel / GoDaddy: release/astrology-app-<version>.zip

Run on the development machine from the backend folder:  .venv\\Scripts\\python.exe deploy\\build_release.py
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
PROJECT = BACKEND.parent
FRONTEND = PROJECT / "frontend"
RELEASE = PROJECT / "release"
BASE_PATH = "/astrology/"
SKIP_DIRS = {"__pycache__", ".pytest_cache"}


def version() -> str:
    match = re.search(r"^APP_VERSION=(.+)$", (BACKEND / ".env.production.example").read_text(encoding="utf-8"), re.M)
    return match.group(1).strip()


def copy_tree(source: Path, target: Path) -> None:
    shutil.copytree(source, target, ignore=lambda folder, names: [n for n in names if n in SKIP_DIRS or n.endswith((".pyc", ".pyo"))])


def build_frontend() -> Path:
    print("Building frontend for", BASE_PATH)
    subprocess.run("npm run build", cwd=FRONTEND, shell=True, check=True, env={**os.environ, "VITE_BASE_PATH": BASE_PATH})
    dist = FRONTEND / "dist"
    if f'src="{BASE_PATH}assets/' not in (dist / "index.html").read_text(encoding="utf-8"):
        raise SystemExit(f"Frontend build does not use base path {BASE_PATH}")
    return dist


def offline_schema_sql() -> str:
    print("Generating schema.sql from the Alembic migrations")
    result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head", "--sql"], cwd=BACKEND, capture_output=True, text=True, check=True, encoding="utf-8")
    sql = result.stdout
    if "CREATE TABLE users" not in sql or "alembic_version" not in sql: raise SystemExit("Generated SQL is incomplete")
    return "-- Database schema for Vedic Astrology. Import into an EMPTY database with phpMyAdmin.\n" + sql


def assert_no_secrets(folder: Path) -> None:
    forbidden_names = {".env", ".env.mysql-admin"}
    for path in folder.rglob("*"):
        if path.name in forbidden_names or ".venv" in path.parts or "node_modules" in path.parts:
            raise SystemExit(f"Refusing to package {path}")
    example = (folder / ".env.example").read_text(encoding="utf-8")
    for key in ("DB_PASSWORD", "SMTP_PASSWORD"):
        if re.search(rf"^{key}=\S", example, re.M): raise SystemExit(f"{key} has a value in .env.example")


def main() -> None:
    name = f"astrology-app-{version()}"
    staging = RELEASE / name
    if staging.exists(): shutil.rmtree(staging)
    staging.mkdir(parents=True)
    dist = build_frontend()
    copy_tree(BACKEND / "app", staging / "app")
    copy_tree(BACKEND / "alembic", staging / "alembic")
    copy_tree(dist, staging / "frontend_dist")
    (staging / "deploy").mkdir()
    for script in ("check_server.py", "migrate.py"): shutil.copy2(BACKEND / "deploy" / script, staging / "deploy" / script)
    shutil.copy2(BACKEND / "passenger_wsgi.py", staging / "passenger_wsgi.py")
    shutil.copy2(BACKEND / "alembic.ini", staging / "alembic.ini")
    shutil.copy2(BACKEND / "requirements-production.txt", staging / "requirements.txt")
    shutil.copy2(BACKEND / ".env.production.example", staging / ".env.example")
    shutil.copy2(PROJECT / "LICENSE", staging / "LICENSE")
    shutil.copy2(PROJECT / "THIRD_PARTY_NOTICES.md", staging / "THIRD_PARTY_NOTICES.md")
    shutil.copy2(PROJECT / "docs" / "DEPLOYMENT_GODADDY.md", staging / "DEPLOY_GUIDE.md")
    (staging / "schema.sql").write_text(offline_schema_sql(), encoding="utf-8", newline="\n")
    assert_no_secrets(staging)
    archive = RELEASE / f"{name}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(staging.rglob("*")):
            if path.is_file(): bundle.write(path, path.relative_to(staging).as_posix())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    files = sum(1 for p in staging.rglob("*") if p.is_file())
    print(f"\nBuilt {archive} ({archive.stat().st_size / 1_048_576:.1f} MB, {files} files)\nSHA-256 {digest}")


if __name__ == "__main__":
    main()
