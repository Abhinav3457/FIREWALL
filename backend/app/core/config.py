from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "CAFW API"
    app_env: str = "dev"
    app_secret_key: str = "change_this_secret"
    access_token_expire_minutes: int = 60

    database_url: str = "sqlite:///./cafw.db"
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "cafw"
    redis_url: str = "redis://localhost:6379/0"

    admin_email: str = "abhinav5911thakur@gmail.com"
    admin_password: str = "Abhinav@1606"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_from: str = "security@cafw.local"
    smtp_enabled: bool = False


settings = Settings()
