from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

class CommentResponse(BaseModel):
    id: int
    post_id: int
    parent_id: Optional[int]
    author_name: str
    author_email: EmailStr
    content: str
    created_at: datetime
    replies: List["CommentResponse"] = []

    class Config:
        from_attributes = True

CommentResponse.model_rebuild()
