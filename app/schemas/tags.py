from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TagCreate(BaseModel):
    name: str
    slug: Optional[str] = None

class TagUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None

class TagResponse(BaseModel):
    id: int
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
