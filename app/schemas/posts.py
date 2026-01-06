from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

from app.schemas.tags import TagResponse

class PostCreate(BaseModel):
    title: str
    summary: str
    content: str
    slug: Optional[str] = None
    tag_ids: Optional[List[int]] = []
    featured: bool = False

class PostUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    slug: Optional[str] = None
    tag_ids: Optional[List[int]] = None
    featured: Optional[bool] = None

class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    summary: str
    content: str
    view_count: int
    featured: bool
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []
