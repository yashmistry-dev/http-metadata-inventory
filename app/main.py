from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from app.database.connection import connect_to_mongo, close_mongo_connection
from app.api.routes import router
from app.config import settings
from app.services.common import setup_logging

logger = logging.getLogger(__name__)
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    await connect_to_mongo()
    logger.info("MongoDB connected successfully")
    yield

    # Shutdown
    await close_mongo_connection()
    logger.info("MongoDB disconnected successfully")

app = FastAPI(
    title="HTTP Metadata Inventory Service",
    description="A service for collecting and retrieving HTTP metadata (headers, cookies, page source) for URLs.",
    version="1.0.0",
    lifespan=lifespan,
    tags_metadata=[
        {
            "name": "metadata",
            "description": "Operations for creating and retrieving HTTP metadata",
        },
        {
            "name": "general",
            "description": "General service endpoints",
        },
    ]
)

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
