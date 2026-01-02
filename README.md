# Blog API

A modern RESTful blog API built with FastAPI, featuring JWT authentication, nested comments, tag management, image uploads, and automatic sitemap generation.

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (via SQLAlchemy)
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt via passlib
- **Migrations**: Alembic
- **Testing**: pytest with async support
- **Containerization**: Docker & Docker Compose

## Running the Server

Build and start the app with a Postgres instance using Docker Compose:

```bash
docker compose up -d --build
```

By default the compose file exposes:

- **blog-api**: localhost:8000
- **Postgres**: localhost:5432

### API Documentation

- **Interactive Docs**: localhost:8000/blog-api/docs
- **Alternative Docs**: localhost:8000/blog-api/redoc

### Stopping the Server

```bash
docker compose down
```

To remove volumes (delete database data):

```bash
docker compose down -v
```

## Endpoints

### Authentication

- **POST** `/auth/token` - Returns JWT access token for admin authentication

### Posts

- **GET** `/posts/` - Get all posts with pagination (query params: `skip`, `limit`)
- **GET** `/posts/{post_id}` - Get a specific post by ID
- **GET** `/posts/slug/{slug}` - Get a specific post by slug
- **POST** `/posts/` - Create a new post (requires admin authentication)
- **PATCH** `/posts/{post_id}` - Update a post (requires admin authentication)
- **DELETE** `/posts/{post_id}` - Delete a post (requires admin authentication)

### Tags

- **GET** `/tags/` - Get all tags with pagination (query params: `skip`, `limit`)
- **GET** `/tags/{tag_id}` - Get a specific tag by ID
- **GET** `/tags/slug/{slug}` - Get a specific tag by slug
- **POST** `/tags/` - Create a new tag (requires admin authentication)
- **PATCH** `/tags/{tag_id}` - Update a tag (requires admin authentication)
- **DELETE** `/tags/{tag_id}` - Delete a tag (requires admin authentication)

### Comments

- **GET** `/comments/{comment_id}` - Get a specific comment by ID with replies
- **GET** `/comments/post/{post_id}` - Get all top-level comments for a post (query params: `skip`, `limit`)
- **POST** `/comments/` - Create a new comment (supports nested replies)
- **DELETE** `/comments/{comment_id}` - Delete a comment (requires admin authentication)

### Uploads

- **POST** `/uploads/photos` - Upload a photo file (requires admin authentication, max 10MB, formats: jpg, jpeg, png, gif, webp)
- **DELETE** `/uploads/photos/{filename}` - Delete a photo by filename (requires admin authentication)

### Search

- **GET** `/search/autocomplete` - Autocomplete search for posts and tags (query params: `q`)

### Sitemap & RSS

- **GET** `/sitemap.xml` - Generate and return XML sitemap for all posts and tags
- **GET** `/rss.xml` - Generate and return RSS 2.0 feed for all posts

### Root

- **GET** `/` - Welcome message

## Database Migrations

This project uses Alembic for database migrations. When you make changes to your models, follow these steps:

1. Make your changes to the model files in `app/models/`
2. Start the containers (if not already running):

   ```bash
   docker compose up -d --build
   ```

3. Generate a new migration:

   ```bash
   docker compose exec blog-api alembic revision --autogenerate -m "Message"
   ```

4. Restart the containers to apply the migration:

   ```bash
   docker compose restart
   ```

## Project Structure

```text
blog-api/
├── app/
│   ├── db/              # Database configuration
│   ├── models/          # SQLAlchemy models
│   ├── routers/         # API route handlers
│   ├── schemas/         # Pydantic schemas
│   ├── tests/           # Test suite
│   └── utils/           # Utility functions (auth, slugify)
├── alembic/             # Database migrations
├── uploads/             # Uploaded files storage
├── main.py              # Application entry point
└── docker-compose.yml   # Docker services configuration
```

## Testing

Run the test suite with pytest:

```bash
pytest
```

## Environment Setup

### Setting Up .env File

Create a `.env` file in the project root with the following variables:

```bash
# Database Configuration
DATABASE_URL=localhost
POSTGRES_USERNAME=blog_user
POSTGRES_PASSWORD=blog_password
POSTGRES_DB=blog_db

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ISSUER=blog-api
AUDIENCE=blog-client

# Admin User
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=<generated-hash>
```

**To generate a password hash for the admin user:**

```bash
python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('YourPasswordHere'))"
```

**To generate a secure SECRET_KEY:**

```bash
openssl rand -hex 32
```
