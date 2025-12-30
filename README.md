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

- **Interactive Docs**: localhost:8000/blog-api/docs
- **Alternative Docs**: localhost:8000/blog-api/redoc

## Endpoints

- `GET /` - Welcome message
- `GET /items/{item_id}` - Get an item by ID
- `POST /items/` - Create a new item
- `PUT /items/{item_id}` - Update an item

## Database Migrations

This project uses Alembic for database migrations. When you make changes to your models, follow these steps:

1. Make your changes to the model files in `app/models/`
2. Start the containers (if not already running):

   ```bash
   docker-compose up -d
   ```

3. Generate a new migration:

   ```bash
   docker compose exec blog-api alembic revision --autogenerate -m "Message"
   ```

4. Restart the containers to apply the migration:

   ```bash
   docker-compose restart
   ```
