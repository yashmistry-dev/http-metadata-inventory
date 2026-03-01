import pytest
from app.services.common import http_client


@pytest.mark.asyncio
async def test_fetch_metadata_success():
    """Test successful metadata fetching."""
    url = "https://google.com"
    
    result = await http_client.fetch_metadata(url)
    
    assert "headers" in result
    assert "cookies" in result
    assert "page_source" in result
    assert isinstance(result["headers"], dict)
    assert isinstance(result["cookies"], list)
    assert isinstance(result["page_source"], str)
    assert len(result["page_source"]) > 0


@pytest.mark.asyncio
async def test_fetch_metadata_invalid_url():
    """Test fetching metadata from invalid URL."""
    url = "https://this-domain-definitely-does-not-exist-12345.com"
    
    with pytest.raises(Exception):
        await http_client.fetch_metadata(url)

