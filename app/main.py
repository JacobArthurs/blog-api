import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .routers import posts, tags, comments, uploads, auth, sitemap, search

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Blog API",
    description="A simple blog API with posts, tags, and comments",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

cors_origins = os.getenv("CORS_ORIGINS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(posts.router)
app.include_router(tags.router)
app.include_router(comments.router)
app.include_router(uploads.router)
app.include_router(auth.router)
app.include_router(sitemap.router)
app.include_router(search.router)

app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")

@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Welcome to Jacob Arthurs Blog API"}
