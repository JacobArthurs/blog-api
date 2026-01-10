from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import List, Optional

class CommentCreate(BaseModel):
    post_id: int
    parent_id: Optional[int] = None
    author_name: str
    author_email: EmailStr
    content: str

class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    parent_id: Optional[int]
    author_name: str
    author_email: EmailStr
    content: str
    like_count: int
    created_at: datetime
    replies: List["CommentResponse"] = []

CommentResponse.model_rebuild()
