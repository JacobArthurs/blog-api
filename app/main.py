from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Welcome to FastAPI"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    """Get an item by ID with optional query parameter"""
    return {"item_id": item_id, "q": q}

@app.post("/items/")
def create_item(item: Item):
    """Create a new item"""
    return item

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    """Update an item"""
    return {"item_id": item_id, **item.dict()}
