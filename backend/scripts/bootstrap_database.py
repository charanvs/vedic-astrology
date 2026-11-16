"""Provision local development/test schemas and restricted accounts."""
from __future__ import annotations
import secrets
from pathlib import Path
import pymysql
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
ADMIN_FILE, APP_FILE = ROOT / ".env.mysql-admin", ROOT / ".env"

def new_password() -> str:
    return secrets.token_urlsafe(32)

def main() -> None:
    admin = dotenv_values(ADMIN_FILE)
    required = ("MYSQL_ADMIN_HOST", "MYSQL_ADMIN_PORT", "MYSQL_ADMIN_USER", "MYSQL_ADMIN_PASSWORD")
    if missing := [key for key in required if not admin.get(key)]:
        raise SystemExit(f"Missing administrator settings: {', '.join(missing)}")
    existing = dotenv_values(APP_FILE) if APP_FILE.exists() else {}
    runtime_password = existing.get("DB_PASSWORD") or new_password()
    migration_password = existing.get("MIGRATION_DB_PASSWORD") or new_password()
    test_password = existing.get("TEST_DB_PASSWORD") or new_password()
    connection = pymysql.connect(host=admin["MYSQL_ADMIN_HOST"], port=int(admin["MYSQL_ADMIN_PORT"]), user=admin["MYSQL_ADMIN_USER"], password=admin["MYSQL_ADMIN_PASSWORD"], autocommit=True)
    try:
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS vedic_astrology CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute("CREATE DATABASE IF NOT EXISTS vedic_astrology_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            for user, secret in (("vedic_app", runtime_password), ("vedic_migrator", migration_password), ("vedic_test", test_password)):
                cursor.execute(f"CREATE USER IF NOT EXISTS '{user}'@'localhost' IDENTIFIED BY %s", (secret,))
                cursor.execute(f"ALTER USER '{user}'@'localhost' IDENTIFIED BY %s ACCOUNT UNLOCK", (secret,))
            cursor.execute("GRANT SELECT, INSERT, UPDATE ON vedic_astrology.* TO 'vedic_app'@'localhost'")
            cursor.execute("GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES ON vedic_astrology.* TO 'vedic_migrator'@'localhost'")
            cursor.execute("GRANT ALL PRIVILEGES ON vedic_astrology_test.* TO 'vedic_test'@'localhost'")
    finally:
        connection.close()
    APP_FILE.write_text("\n".join(("APP_NAME=vedic-astrology", "APP_VERSION=0.2.0", "APP_ENV=development", "ALLOWED_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173", "DB_HOST=127.0.0.1", "DB_PORT=3306", "DB_NAME=vedic_astrology", "DB_USER=vedic_app", f"DB_PASSWORD={runtime_password}", "MIGRATION_DB_USER=vedic_migrator", f"MIGRATION_DB_PASSWORD={migration_password}", "TEST_DB_NAME=vedic_astrology_test", "TEST_DB_USER=vedic_test", f"TEST_DB_PASSWORD={test_password}", "")), encoding="utf-8")
    print("Provisioned local development/test schemas and restricted accounts; secrets were not displayed.")

if __name__ == "__main__":
    main()
