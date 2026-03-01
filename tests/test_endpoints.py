import pytest
from httpx import AsyncClient
from app.main import app
from app.database.connection import db
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data


@pytest.mark.asyncio
async def test_create_metadata_success(client: AsyncClient, test_db):
    """Test POST /metadata endpoint with valid URL."""
    from pydantic import HttpUrl
    url = "https://example.com"
    
    response = await client.post(
        "/metadata",
        json={"url": url}
    )
    
    assert response.status_code == 201
    data = response.json()
    # HttpUrl normalizes URLs (may add trailing slash), so compare normalized versions
    expected_url = str(HttpUrl(url))
    assert data["url"] == expected_url
    assert "headers" in data
    assert "cookies" in data
    assert "page_source" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_metadata_invalid_url(client: AsyncClient):
    """Test POST /metadata endpoint with invalid URL."""
    response = await client.post(
        "/metadata",
        json={"url": "not-a-valid-url"}
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_metadata_existing(client: AsyncClient, test_db, sample_metadata):
    """Test GET /metadata endpoint when metadata exists."""
    # HttpUrl normalizes URLs (adds trailing slash), so we need to insert with normalized URL
    from pydantic import HttpUrl
    # Parse the URL to get the normalized version
    normalized_url_obj = HttpUrl(sample_metadata["url"])
    normalized_url = str(normalized_url_obj)
    
    # Insert test data with normalized URL
    test_data = {
        **sample_metadata,
        "url": normalized_url,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    await test_db.metadata.insert_one(test_data)
    
    response = await client.get("/metadata", params={"url": sample_metadata["url"]})
    
    assert response.status_code == 200
    data = response.json()
    # HttpUrl normalizes, so compare normalized versions
    assert data["url"] == normalized_url
    assert data["headers"] == sample_metadata["headers"]


@pytest.mark.asyncio
async def test_get_metadata_not_found(client: AsyncClient, test_db):
    """Test GET /metadata endpoint when metadata does not exist."""
    url = "https://nonexistent-example-12345.com"
    
    response = await client.get("/metadata", params={"url": url})
    
    assert response.status_code == 202  # Accepted
    data = response.json()
    assert data["status"] == "pending"
    # HttpUrl normalizes URLs (adds trailing slash), so compare normalized versions
    assert data["url"].rstrip('/') == url.rstrip('/')
