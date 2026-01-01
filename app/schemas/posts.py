from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class PostCreate(BaseModel):
    title: str
    content: str
    slug: Optional[str] = None
    tag_ids: Optional[List[int]] = []

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    slug: Optional[str] = None
    tag_ids: Optional[List[int]] = None

class TagInPost(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str

class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    slug: str
    content: str
    view_count: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagInPost] = []
