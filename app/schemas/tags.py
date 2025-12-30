from pydantic import BaseModel
from datetime import datetime

class TagResponse(BaseModel):
    id: int
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
