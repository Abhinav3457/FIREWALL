from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CAFW API"
    app_env: str = "development"
    secret_key: str = "change_me_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    database_url: str = "sqlite:///./waf.db"
    redis_url: str = "redis://localhost:6379/0"
    frontend_origin: str = "http://localhost:5173"

    admin_email: str = ""
    admin_password_hash: str = ""
    admin_password: str = ""

    otp_expire_seconds: int = 300
    otp_max_attempts: int = 3
    otp_lock_seconds: int = 30

    email_host: str = "smtp.gmail.com"
    email_port: int = 587
    email_username: str = ""
    email_password: str = ""
    email_from: str = ""

    waf_block_patterns: str = "../,<script,union select,drop table,or 1=1"
    waf_max_body_bytes: int = 200000
    waf_login_max_attempts: int = 3
    waf_login_window_seconds: int = 300
    waf_login_lock_seconds: int = 60
    waf_allow_paths: str = "/health,/api/dashboard/stats"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
