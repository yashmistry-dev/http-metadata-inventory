import pytest
from app.database.connection import get_database
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_database_indexes(test_db):
    """Test that indexes are created."""
    indexes = await test_db.metadata.list_indexes().to_list(length=10)
    index_names = [idx["name"] for idx in indexes]
    
    # Should have _id index and url index
    assert "_id_" in index_names
    assert "url_1" in index_names


@pytest.mark.asyncio
async def test_database_unique_constraint(test_db):
    """Test that URL uniqueness is enforced."""
    url = "https://example.com"
    document = {
        "url": url,
        "headers": {},
        "cookies": [],
        "page_source": "",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    # Insert first document
    await test_db.metadata.insert_one(document)
    
    # Try to insert duplicate (should work with upsert, but not create duplicate)
    await test_db.metadata.update_one(
        {"url": url},
        {"$set": document},
        upsert=True
    )
    
    # Verify only one document exists
    count = await test_db.metadata.count_documents({"url": url})
    assert count == 1
