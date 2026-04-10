import os

from pydantic_settings import BaseSettings, SettingsConfigDict


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = os.getenv("APP_NAME", "CAFW API")
    app_env: str = os.getenv("APP_ENV", "dev")
    app_secret_key: str = os.getenv("SECRET_KEY", os.getenv("APP_SECRET_KEY", "change-me"))
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./cafw.db")
    mongodb_url: str = os.getenv("MONGODB_URL", "")
    mongodb_db_name: str = os.getenv("MONGODB_DB_NAME", "cafw")
    redis_url: str = os.getenv("REDIS_URL", "")

    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "change-me")

    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_pass: str = os.getenv("SMTP_PASS", "")
    smtp_from: str = os.getenv("SMTP_FROM", "")
    smtp_enabled: bool = _as_bool(os.getenv("SMTP_ENABLED"), default=False)

    def environment_summary(self) -> dict[str, str]:
        return {
            "APP_ENV": self.app_env,
            "MONGODB_URL_SET": str(bool(self.mongodb_url)),
            "REDIS_URL_SET": str(bool(self.redis_url)),
            "SMTP_ENABLED": str(self.smtp_enabled),
            "SMTP_HOST_SET": str(bool(self.smtp_host)),
            "SMTP_USER_SET": str(bool(self.smtp_user)),
            "SECRET_KEY_SET": str(bool(self.app_secret_key and self.app_secret_key != "change-me")),
        }


settings = Settings()
