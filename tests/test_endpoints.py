import pytest
from httpx import AsyncClient
from app.main import app
from app.database.connection import db
from datetime import datetime


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
    url = "https://example.com"
    
    response = await client.post(
        "/metadata",
        json={"url": url}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["url"] == url
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
    # Insert test data
    await test_db.metadata.insert_one({
        **sample_metadata,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    response = await client.get("/metadata", params={"url": sample_metadata["url"]})
    
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == sample_metadata["url"]
    assert data["headers"] == sample_metadata["headers"]


@pytest.mark.asyncio
async def test_get_metadata_not_found(client: AsyncClient, test_db):
    """Test GET /metadata endpoint when metadata does not exist."""
    url = "https://nonexistent-example-12345.com"
    
    response = await client.get("/metadata", params={"url": url})
    
    assert response.status_code == 202  # Accepted
    data = response.json()
    assert data["status"] == "pending"
    assert data["url"] == url
