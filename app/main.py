import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import posts, tags, comments, uploads, auth, sitemap, search

app = FastAPI(
    title="Blog API",
    description="A simple blog API with posts, tags, and comments",
    version="1.0.0",
    root_path="/blog-api"
)

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
