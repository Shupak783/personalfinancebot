from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5"

    plaid_client_id: str = ""
    plaid_secret: str = ""
    plaid_env: str = "sandbox"
    plaid_products: str = "transactions"
    plaid_country_codes: str = "US"

    database_url: str = "sqlite:///./finbot.db"
    app_secret: str = "change-me"

    email_smtp_host: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_username: str = ""
    email_app_password: str = ""
    email_from: str = ""
    email_to: str = ""

    @property
    def plaid_products_list(self) -> list[str]:
        return [p.strip() for p in self.plaid_products.split(",") if p.strip()]

    @property
    def plaid_country_codes_list(self) -> list[str]:
        return [c.strip() for c in self.plaid_country_codes.split(",") if c.strip()]


settings = Settings()
