from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.config import settings


class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None


db = Database()


async def connect_to_mongo() -> None:
    try:
        db.client = AsyncIOMotorClient(
            settings.mongodb_url,
            serverSelectionTimeoutMS=5000,
        )
        db.database = db.client[settings.mongodb_db_name]
        
        # Create indexes
        await db.database.metadata.create_index("url", unique=True)
        await db.database.metadata.create_index("created_at")
        await db.database.metadata.create_index("updated_at")
        
        await db.client.admin.command('ping')
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise


async def close_mongo_connection() -> None:
    if db.client:
        db.client.close()


def get_database():
    return db.database

