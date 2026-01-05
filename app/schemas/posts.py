from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

from app.schemas.tags import TagResponse

class PostCreate(BaseModel):
    title: str
    tldr: str
    content: str
    slug: Optional[str] = None
    tag_ids: Optional[List[int]] = []

class PostUpdate(BaseModel):
    title: Optional[str] = None
    tldr: Optional[str] = None
    content: Optional[str] = None
    slug: Optional[str] = None
    tag_ids: Optional[List[int]] = None

class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    tldr: str
    content: str
    view_count: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []
