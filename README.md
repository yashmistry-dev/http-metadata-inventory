# HTTP Metadata Inventory Service

A service that collects and stores HTTP metadata (headers, cookies, and page source) from URLs. Built with FastAPI and MongoDB.

## Getting Started

The easiest way to run this project is using Docker Compose. It will start both the API server and MongoDB database for you.

```terminal - 1
docker-compose up
```

Once it's running, you can access:
- API Documentation: http://localhost:8000/docs
- MongoDB: localhost:27019 (from your host machine)

The API will be ready to accept requests once both containers are up and running.

## Running Tests

To run the test suite, open another terminal window and use:

```terminal - 2
docker-compose run tests
```

This will spin up a separate container just for running tests, ensuring a clean test environment. The tests cover endpoints, database operations, and HTTP client functionality.

## Project Structure

The codebase is organized into a few main areas:

- `app/api/routes.py` - Contains all the API endpoints (POST /metadata, GET /metadata, health check)
- `app/services/` - Business logic for metadata collection and storage
- `app/database/` - MongoDB connection and database setup
- `app/models/` - Pydantic models for request/response validation
- `tests/` - Test suite with endpoint, database, and HTTP client tests

The separation keeps things modular - API routes handle HTTP concerns, services contain the business logic, and the database layer manages persistence.

## Configuration

You can use a `.env` file to configure the application, but I've kept most settings in the `docker-compose.yml` file for simplicity..

## API Endpoints

**POST /metadata** - Creates a metadata record by fetching headers, cookies, and page source from a given URL.

**GET /metadata?url=<url>** - Retrieves existing metadata if available (200), or returns 202 Accepted and triggers background collection if not found.

**GET /health** - Health check endpoint to verify the service and database connection status.

You can explore and test all endpoints using the interactive docs at `/docs` when the service is running.

## Future Scalability Considerations

Currently, the background metadata collection uses FastAPI's `BackgroundTasks`, which works well for small to medium workloads but runs in the same process as the API. For better scalability and reliability, here are some improvements that could be made:

**Queue-Based Background Processing**: Instead of FastAPI's background tasks, we could integrate a proper message queue system like:
- **Celery with Redis/RabbitMQ** - A robust Python task queue that supports distributed workers, retries, and monitoring
- **RQ (Redis Queue)** - A simpler alternative that's easier to set up and works well for Python async tasks
- **Apache Kafka** - For high-throughput scenarios where we need to process many URLs concurrently

This would allow:
- Scaling workers independently from the API
- Better error handling and retry mechanisms
- Task persistence (tasks survive API restarts)
- Monitoring and visibility into background job status
- Rate limiting and priority queues for URL fetching

The current implementation is a good starting point, but moving to a queue-based system would be the next logical step as the service grows and needs to handle more concurrent requests or larger workloads.
