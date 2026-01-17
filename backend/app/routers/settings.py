"""Settings API endpoints."""

from pydantic import BaseModel
from fastapi import APIRouter

from app.core.config import (
    settings,
    get_runtime_settings,
    save_runtime_settings,
)

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
    anthropic_api_key: SettingValue
    anthropic_model: SettingValue
    gdrive_folder: SettingValue
    timezone: SettingValue
    google_configured: bool  # Whether OAuth is set up
    version: VersionInfo


class SettingsUpdate(BaseModel):
    """Settings update request."""
    anthropic_api_key: str | None = None
    anthropic_model: str | None = None
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
        anthropic_api_key=get_setting_with_source("anthropic_api_key", settings.anthropic_api_key, mask=True),
        anthropic_model=get_setting_with_source("anthropic_model", settings.anthropic_model),
        gdrive_folder=get_setting_with_source("gdrive_folder", settings.gdrive_folder),
        timezone=get_setting_with_source("timezone", settings.timezone),
        google_configured=bool(settings.google_client_id and settings.google_client_secret),
        version=VersionInfo(
            app_version=settings.app_version,
            image_tag=settings.image_tag,
        ),
    )


@router.put("/settings", response_model=AppSettings)
async def update_settings(update: SettingsUpdate):
    """Update application settings."""
    runtime = get_runtime_settings()

    # Update only provided fields
    if update.anthropic_api_key is not None:
        if update.anthropic_api_key:
            runtime["anthropic_api_key"] = update.anthropic_api_key
        elif "anthropic_api_key" in runtime:
            del runtime["anthropic_api_key"]

    if update.anthropic_model is not None:
        if update.anthropic_model:
            runtime["anthropic_model"] = update.anthropic_model
        elif "anthropic_model" in runtime:
            del runtime["anthropic_model"]

    if update.gdrive_folder is not None:
        if update.gdrive_folder:
            runtime["gdrive_folder"] = update.gdrive_folder
        elif "gdrive_folder" in runtime:
            del runtime["gdrive_folder"]

    if update.timezone is not None:
        if update.timezone:
            runtime["timezone"] = update.timezone
        elif "timezone" in runtime:
            del runtime["timezone"]

    save_runtime_settings(runtime)

    # Return updated settings
    return await get_settings()


@router.delete("/settings/{key}")
async def reset_setting(key: str):
    """Reset a setting to default/env value."""
    valid_keys = {"anthropic_api_key", "anthropic_model", "gdrive_folder", "timezone"}
    if key not in valid_keys:
        return {"error": "Invalid setting key"}

    runtime = get_runtime_settings()
    if key in runtime:
        del runtime[key]
        save_runtime_settings(runtime)

    return {"message": f"Reset {key} to default"}
