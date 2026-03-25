"""
Configuración central con Pydantic Settings.
Lee variables del .env y las valida.
"""

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ─────────────────────────────────────────────────────────────────
    # AWS Credentials
    # ─────────────────────────────────────────────────────────────────
    aws_access_key_id: str = Field(..., validation_alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(..., validation_alias="AWS_SECRET_ACCESS_KEY")
    aws_session_token: str | None = Field(
        default=None, validation_alias="AWS_SESSION_TOKEN"
    )
    aws_region: str = Field(
        "eu-west-1", validation_alias=AliasChoices("AWS_REGION", "AWS_DEFAULT_REGION")
    )

    # ─────────────────────────────────────────────────────────────────
    # Bedrock Models
    # ─────────────────────────────────────────────────────────────────
    llm_model_id_small: str = Field(
        "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        validation_alias="LLM_MODEL_ID_SMALL",
    )
    llm_model_id_medium: str = Field(
        "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        validation_alias="LLM_MODEL_ID_MEDIUM",
    )
    llm_model_id_large: str = Field(
        "us.anthropic.claude-opus-4-5-20251101-v1:0",
        validation_alias="LLM_MODEL_ID_LARGE",
    )


# Instancia global
settings = Settings()  # type: ignore[call-arg]
