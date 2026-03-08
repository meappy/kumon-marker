"""Settings API endpoints."""

from pydantic import BaseModel
from fastapi import APIRouter

from app.core.config import (
    settings,
    get_runtime_settings,
    save_runtime_settings,
)
from app.services.providers import PROVIDERS

router = APIRouter()


class SettingValue(BaseModel):
    """A single setting with metadata."""
    value: str
    source: str  # "default", "env", "user"
    editable: bool


class VersionInfo(BaseModel):
    """Version information."""
    app_version: str
    image_tag: str


class AppSettings(BaseModel):
    """All application settings."""
    vision_provider: SettingValue
    available_providers: list[str]
    anthropic_api_key: SettingValue
    anthropic_model: SettingValue
    gemini_model: SettingValue
    openai_model: SettingValue
    ollama_model: SettingValue
    validation_method: SettingValue
    validation_provider: SettingValue
    gdrive_folder: SettingValue
    timezone: SettingValue
    google_configured: bool
    version: VersionInfo


class SettingsUpdate(BaseModel):
    """Settings update request."""
    vision_provider: str | None = None
    anthropic_api_key: str | None = None
    anthropic_model: str | None = None
    gemini_model: str | None = None
    openai_model: str | None = None
    ollama_model: str | None = None
    validation_method: str | None = None
    validation_provider: str | None = None
    gdrive_folder: str | None = None
    timezone: str | None = None


def mask_api_key(key: str) -> str:
    """Mask an API key for display."""
    if not key:
        return ""
    if len(key) <= 8:
        return "***"
    return f"{key[:4]}...{key[-4:]}"


def get_setting_with_source(key: str, default: str, mask: bool = False) -> SettingValue:
    """Get a setting value with its source."""
    runtime = get_runtime_settings()
    env_value = getattr(settings, key, "")

    if key in runtime:
        value = runtime[key]
        source = "user"
    elif env_value and env_value != default:
        value = env_value
        source = "env"
    else:
        value = default
        source = "default"

    return SettingValue(
        value=mask_api_key(value) if mask else value,
        source=source,
        editable=True,
    )


@router.get("/settings", response_model=AppSettings)
async def get_settings():
    """Get current application settings."""
    return AppSettings(
        vision_provider=get_setting_with_source("vision_provider", settings.vision_provider),
        available_providers=list(PROVIDERS.keys()),
        anthropic_api_key=get_setting_with_source("anthropic_api_key", settings.anthropic_api_key, mask=True),
        anthropic_model=get_setting_with_source("anthropic_model", settings.anthropic_model),
        gemini_model=get_setting_with_source("gemini_model", settings.gemini_model),
        openai_model=get_setting_with_source("openai_model", settings.openai_model),
        ollama_model=get_setting_with_source("ollama_model", settings.ollama_model),
        validation_method=get_setting_with_source("validation_method", settings.validation_method),
        validation_provider=get_setting_with_source("validation_provider", settings.validation_provider),
        gdrive_folder=get_setting_with_source("gdrive_folder", settings.gdrive_folder),
        timezone=get_setting_with_source("timezone", settings.timezone),
        google_configured=bool(settings.google_client_id and settings.google_client_secret),
        version=VersionInfo(
            app_version=settings.app_version,
            image_tag=settings.image_tag,
        ),
    )


EDITABLE_KEYS = {
    "vision_provider", "anthropic_api_key", "anthropic_model",
    "gemini_model", "openai_model", "ollama_model",
    "validation_method", "validation_provider",
    "gdrive_folder", "timezone",
}


@router.put("/settings", response_model=AppSettings)
async def update_settings(update: SettingsUpdate):
    """Update application settings."""
    runtime = get_runtime_settings()

    for key in EDITABLE_KEYS:
        new_value = getattr(update, key, None)
        if new_value is not None:
            if new_value:
                runtime[key] = new_value
            elif key in runtime:
                del runtime[key]

    save_runtime_settings(runtime)
    return await get_settings()


@router.delete("/settings/{key}")
async def reset_setting(key: str):
    """Reset a setting to default/env value."""
    if key not in EDITABLE_KEYS:
        return {"error": "Invalid setting key"}

    runtime = get_runtime_settings()
    if key in runtime:
        del runtime[key]
        save_runtime_settings(runtime)

    return {"message": f"Reset {key} to default"}
