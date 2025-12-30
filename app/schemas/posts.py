from pydantic import BaseModel
from datetime import datetime
from typing import List

class TagInPost(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True

class PostResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    view_count: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagInPost] = []

    class Config:
        from_attributes = True
