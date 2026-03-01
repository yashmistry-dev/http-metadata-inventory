# HTTP Metadata Inventory Service

A FastAPI service that collects and stores HTTP metadata (headers, cookies, page source) from URLs.

## Features

- POST endpoint to create metadata records
- GET endpoint to retrieve metadata or trigger background collection
- MongoDB storage for metadata
- Background processing for async metadata collection

## Tech Stack

- Python 3.11+
- FastAPI
- MongoDB
- Docker Compose

## Setup

### Using Docker Compose

```bash
docker-compose up
```

This starts:
- MongoDB on port 27019 (host) / 27017 (container)
- API on port 8000

Access API docs at: http://localhost:8000/docs

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start MongoDB:
```bash
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

3. Set environment variables (optional):
```bash
export MONGODB_URL="mongodb://localhost:27017/"
export MONGODB_DB_NAME="metadata_db"
```

4. Run the app:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### POST /metadata

Create metadata for a URL.

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response (201):**
```json
{
  "url": "https://example.com",
  "headers": {...},
  "cookies": [...],
  "page_source": "...",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

### GET /metadata?url=<url>

Retrieve metadata. Returns 200 if found, 202 if collection is initiated in background.

### GET /health

Health check endpoint.

## Testing

Run tests:
```bash
# With Docker
docker-compose exec api pytest

# Locally
pytest
```

## Configuration

Environment variables:
- `MONGODB_URL`: MongoDB connection string
- `MONGODB_DB_NAME`: Database name (default: `metadata_db`)
- `API_HOST`: API host (default: `0.0.0.0`)
- `API_PORT`: API port (default: `8000`)
- `HTTP_TIMEOUT`: HTTP timeout in seconds (default: `30`)

## Project Structure

```
app/
├── main.py              # FastAPI app
├── api/routes.py        # API endpoints
├── models/schemas.py    # Pydantic models
├── services/            # Business logic
├── database/            # MongoDB connection
└── config.py            # Configuration
tests/
├── test_endpoints.py    # Endpoint tests
├── test_http_client.py  # HTTP client tests
└── test_database.py    # Database tests
```
