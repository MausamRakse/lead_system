from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APOLLO_API_KEY: str
    CSC_API_KEY: str
    DATABASE_URL: str
    WEBHOOK_URL: str = "https://webhook-test.com/5b112b64ff0f4104d003444e843c161a"
    ALLOWED_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
