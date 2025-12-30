from fastapi import FastAPI
from .routers import posts, tags, comments

app = FastAPI(
    title="Blog API",
    description="A simple blog API with posts and tags",
    version="1.0.0",
    root_path="/blog-api"
)

# Include routers
app.include_router(posts.router)
app.include_router(tags.router)
app.include_router(comments.router)

@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Welcome to Jacob Arthurs Blog API"}
