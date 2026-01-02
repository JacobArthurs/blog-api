from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PostSearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    created_at: datetime

class TagSearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str

class SearchResponse(BaseModel):
    posts: list[PostSearchResult]
    tags: list[TagSearchResult]
