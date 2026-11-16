import os
from dataclasses import dataclass
from dotenv import load_dotenv
from sqlalchemy import URL
load_dotenv()

@dataclass(frozen=True)
class Settings:
    application_name: str = os.getenv("APP_NAME", "vedic-astrology")
    application_version: str = os.getenv("APP_VERSION", "1.2.0")
    environment: str = os.getenv("APP_ENV", "development")
    base_path: str = os.getenv("APP_BASE_PATH", "")
    public_url: str = os.getenv("APP_PUBLIC_URL", "http://localhost:5173")
    allowed_origins_raw: str = os.getenv("ALLOWED_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_name: str = os.getenv("DB_NAME", "vedic_astrology")
    db_user: str = os.getenv("DB_USER", "vedic_app")
    db_password: str = os.getenv("DB_PASSWORD", "")
    session_cookie_name: str = os.getenv("SESSION_COOKIE_NAME", "vedic_session")
    session_cookie_secure: bool = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    session_cookie_path: str = os.getenv("SESSION_COOKIE_PATH", "/")
    session_idle_minutes: int = int(os.getenv("SESSION_IDLE_TIMEOUT_MINUTES", "30"))
    session_absolute_hours: int = int(os.getenv("SESSION_ABSOLUTE_TIMEOUT_HOURS", "24"))
    verification_token_minutes: int = int(os.getenv("VERIFICATION_TOKEN_MINUTES", "60"))
    reset_token_minutes: int = int(os.getenv("RESET_TOKEN_MINUTES", "30"))
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from: str = os.getenv("SMTP_FROM", "")
    require_verified_email: bool = os.getenv("REQUIRE_VERIFIED_EMAIL", "true").lower() == "true"
    require_admin_approval: bool = os.getenv("REQUIRE_ADMIN_APPROVAL", "true").lower() == "true"
    frontend_dist: str = os.getenv("FRONTEND_DIST", "")
    source_code_url: str = os.getenv("SOURCE_CODE_URL", "")
    trusted_hosts_raw: str = os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1,testserver")
    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]
    @property
    def trusted_hosts(self) -> list[str]:
        return [host.strip() for host in self.trusted_hosts_raw.split(",") if host.strip()]
    def database_url(self, *, migration: bool = False, test: bool = False) -> URL:
        user = os.getenv("MIGRATION_DB_USER", self.db_user) if migration else self.db_user
        password = os.getenv("MIGRATION_DB_PASSWORD", self.db_password) if migration else self.db_password
        name = self.db_name
        if test:
            user, password, name = os.getenv("TEST_DB_USER", "vedic_test"), os.getenv("TEST_DB_PASSWORD", ""), os.getenv("TEST_DB_NAME", "vedic_astrology_test")
        return URL.create("mysql+pymysql", username=user, password=password, host=self.db_host, port=self.db_port, database=name, query={"charset": "utf8mb4"})

def get_settings() -> Settings:
    return Settings()
