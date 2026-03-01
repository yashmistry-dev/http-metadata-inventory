import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from app.main import app
from app.database.connection import db
from app.config import settings


@pytest.fixture(scope="function")
async def test_db():
    """Create a test database."""
    # Use a test database
    test_db_name = f"{settings.mongodb_db_name}_test"
    test_client = AsyncIOMotorClient(settings.mongodb_url)
    test_database = test_client[test_db_name]
    
    # Store original database
    original_db = db.database
    
    # Replace with test database
    db.database = test_database
    
    yield test_database
    
    # Cleanup: drop test database
    await test_client.drop_database(test_db_name)
    test_client.close()
    
    # Restore original database
    db.database = original_db


@pytest.fixture(scope="function")
async def client(test_db):
    """Create a test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_url():
    """Sample URL for testing."""
    return "https://example.com"


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing."""
    return {
        "url": "https://example.com",
        "headers": {
            "content-type": "text/html",
            "content-length": "1234"
        },
        "cookies": [
            {
                "name": "session",
                "value": "abc123",
                "domain": "example.com",
                "path": "/"
            }
        ],
        "page_source": "<html><body>Test</body></html>"
    }

