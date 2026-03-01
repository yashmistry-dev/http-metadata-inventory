import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from app.database.connection import get_database
from app.services.common import http_client

logger = logging.getLogger(__name__)


class MetadataService:
    
    @staticmethod
    async def create_metadata(url: str) -> Dict[str, Any]:
        metadata = await http_client.fetch_metadata(url)
        
        document = {
            "url": url,
            "headers": metadata["headers"],
            "cookies": metadata["cookies"],
            "page_source": metadata["page_source"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        db = get_database()
        await db.metadata.update_one(
            {"url": url},
            {"$set": document},
            upsert=True
        )
        
        return document
    
    @staticmethod
    async def get_metadata(url: str) -> Optional[Dict[str, Any]]:
        db = get_database()
        document = await db.metadata.find_one({"url": url})
        
        if document:
            document.pop("_id", None)
            return document
        
        return None
    
    @staticmethod
    async def collect_metadata_background(url: str) -> None:
        try:
            metadata = await http_client.fetch_metadata(url)
            
            document = {
                "url": url,
                "headers": metadata["headers"],
                "cookies": metadata["cookies"],
                "page_source": metadata["page_source"],
                "updated_at": datetime.now(timezone.utc),
            }
            
            db = get_database()
            existing = await db.metadata.find_one({"url": url})
            
            if existing:
                await db.metadata.update_one(
                    {"url": url},
                    {"$set": document}
                )
            else:
                document["created_at"] = datetime.now(timezone.utc)
                await db.metadata.insert_one(document)
        except Exception as e:
            logger.error(f"Error in background metadata collection for {url}: {e}", exc_info=True)

