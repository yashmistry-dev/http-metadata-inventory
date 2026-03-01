import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks, status, Query
from fastapi.responses import JSONResponse
from pydantic import HttpUrl

from app.models.schemas import (
    MetadataRequest, 
    MetadataResponse, 
    ErrorResponse
)
from app.services.metadata_service import MetadataService

logger = logging.getLogger(__name__)

router = APIRouter()
service = MetadataService()


@router.get("/", tags=["general"])
async def root():
    return {
        "message": "HTTP Metadata Inventory Service",
        "msg": "This service collects and stores metadata from HTTP URLs. Use the /docs endpoint to explore the API documentation and available endpoints.",
        "docs": "/docs",
    }


@router.get("/health", tags=["general"])
async def health_check():
    try:
        from app.database.connection import db
        if db.client:
            await db.client.admin.command('ping')
            return {"status": "healthy", "database": "connected"}
        else:
            return {"status": "unhealthy", "database": "disconnected"}
    except Exception:
        return {"status": "unhealthy", "database": "disconnected"}


@router.post(
    "/metadata",
    response_model=MetadataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create metadata",
    description="Fetch and create metadata for a given URL. Collects HTTP headers, cookies, and page source.",
    responses={
        400: {"model": ErrorResponse, "description": "Failed to fetch metadata"},
        422: {"model": ErrorResponse, "description": "Invalid URL format"}
    },
    tags=["metadata"]
)
async def create_metadata(
    request: MetadataRequest
) -> MetadataResponse:
    url = str(request.url)
    
    try:
        logger.info(f"Creating metadata for URL: {url}")
        metadata = await service.create_metadata(url)
        logger.info(f"Successfully created metadata for URL: {url}")
        return MetadataResponse(**metadata)
    except Exception as e:
        logger.error(f"Failed to create metadata for {url}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to collect metadata: {str(e)}"
        )


@router.get(
    "/metadata",
    summary="Get metadata",
    description="Retrieve metadata for a URL. Returns existing metadata or initiates background collection.",
    responses={
        200: {"model": MetadataResponse, "description": "Metadata found"},
        202: {"description": "Metadata collection initiated"},
        422: {"model": ErrorResponse, "description": "Invalid URL format"}
    },
    tags=["metadata"]
)
async def get_metadata(
    background_tasks: BackgroundTasks,
    url: HttpUrl = Query(..., description="The URL to retrieve metadata for")
):
    url_str = str(url)
    metadata = await service.get_metadata(url_str)
    
    if metadata:
        logger.info(f"Retrieved existing metadata for URL: {url_str}")
        return MetadataResponse(**metadata)
    else:
        logger.info(f"Metadata not found for URL: {url_str}, initiating background collection")
        background_tasks.add_task(
            service.collect_metadata_background,
            url_str
        )
        
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "message": "Metadata collection initiated",
                "url": url_str,
                "status": "pending"
            }
        )

