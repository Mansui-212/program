from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Hakimi API"
    app_env: str = "development"
    app_debug: bool = True

    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 10080

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
