from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional

class CommentCreate(BaseModel):
    post_id: int
    parent_id: Optional[int] = None
    author_name: str = Field(..., min_length=2, max_length=100)
    content: str = Field(..., min_length=1, max_length=2000)

class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    parent_id: int | None
    depth: int
    author_name: str
    content: str
    like_count: int
    created_at: datetime
    replies: List["CommentResponse"] = []

CommentResponse.model_rebuild()
