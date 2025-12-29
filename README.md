# blog-api

A basic FastAPI implementation with CRUD operations.

## Running the Server

Build and start the app with a Postgres instance using Docker Compose:

```bash
docker-compose up -d --build
```

By default the compose file exposes:

- **blog0api**: localhost:8000
- **Postgres**: localhost:5432

### API Documentation

- **Interactive Docs**: localhost:8000/docs
- **Alternative Docs**: localhost:8000/redoc

## Endpoints

- `GET /` - Welcome message
- `GET /items/{item_id}` - Get an item by ID
- `POST /items/` - Create a new item
- `PUT /items/{item_id}` - Update an item
