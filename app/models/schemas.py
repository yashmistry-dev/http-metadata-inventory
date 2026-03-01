from pydantic import BaseModel, HttpUrl, Field
from typing import Dict, List
from datetime import datetime


class MetadataRequest(BaseModel):
    """Request model for creating metadata."""
    url: HttpUrl = Field(..., description="URL to collect metadata from")


class MetadataResponse(BaseModel):
    """Response model containing collected metadata."""
    url: str = Field(..., description="The URL for which metadata was collected")
    headers: Dict[str, str] = Field(..., description="HTTP response headers")
    cookies: List[Dict[str, str]] = Field(..., description="HTTP cookies")
    page_source: str = Field(..., description="HTML page source")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last update timestamp")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str = Field(..., description="Error message")

