"""Tenant settings Pydantic schemas."""
import uuid

from pydantic import BaseModel, Field

from src.types.base import BaseSchema


class TenantGeneralResponse(BaseSchema):
    """Tenant general settings response."""

    id: str
    name: str
    slug: str
    logo_url: str | None = None
    timezone: str = "UTC"
    default_language: str = "en"
    default_template: str | None = None
    is_active: bool = True


class TenantBrandingResponse(BaseSchema):
    """Tenant branding settings response."""

    primary_color: str = "#5F2CFF"
    favicon_url: str | None = None
    font_family: str = "Montserrat"
    email_signature: str | None = None


class TenantDefaultsResponse(BaseSchema):
    """Tenant defaults settings response."""

    default_currency: str = "USD"
    standard_roi_period: str = "3 Years"
    min_feasibility_threshold: int = 65
    required_ethics_level: str = "Level 3 - Enterprise Standard"


class TenantFullResponse(BaseSchema):
    """Full tenant response combining all settings."""

    id: str
    name: str
    slug: str
    logo_url: str | None = None
    timezone: str = "UTC"
    default_language: str = "en"
    default_template: str | None = None
    is_active: bool = True
    primary_color: str = "#5F2CFF"
    favicon_url: str | None = None
    font_family: str = "Montserrat"
    email_signature: str | None = None
    defaults: TenantDefaultsResponse = Field(
        default_factory=TenantDefaultsResponse
    )


class UpdateTenantGeneralRequest(BaseModel):
    """Update tenant general settings."""

    name: str | None = None
    timezone: str | None = None
    default_language: str | None = None
    default_template: str | None = None


class UpdateTenantBrandingRequest(BaseModel):
    """Update tenant branding settings."""

    primary_color: str | None = None
    font_family: str | None = None
    email_signature: str | None = None


class UpdateTenantDefaultsRequest(BaseModel):
    """Update tenant defaults."""

    default_currency: str | None = None
    standard_roi_period: str | None = None
    min_feasibility_threshold: int | None = None
    required_ethics_level: str | None = None
