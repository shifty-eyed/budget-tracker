from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    plaid_client_id: str = Field(..., env="PLAID_CLIENT_ID")
    plaid_secret: str = Field(..., env="PLAID_SECRET")
    plaid_env: str = Field("sandbox", env="PLAID_ENV")
    plaid_products: List[str] = Field(default_factory=lambda: ["transactions"], env="PLAID_PRODUCTS")
    plaid_country_codes: List[str] = Field(default_factory=lambda: ["US"], env="PLAID_COUNTRY_CODES")
    plaid_redirect_uri: str | None = Field(default=None, env="PLAID_REDIRECT_URI")
    plaid_android_package_name: str | None = Field(default=None, env="PLAID_ANDROID_PACKAGE_NAME")
    application_name: str = Field("Budget Tracker", env="APP_NAME")
    webhook_url: str | None = Field(default=None, env="PLAID_WEBHOOK")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @validator("plaid_products", "plaid_country_codes", pre=True)
    def _split_csv(cls, value):  # noqa: D401
        """Allow comma-separated configuration values."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache()
def get_settings() -> Settings:
    return Settings()
