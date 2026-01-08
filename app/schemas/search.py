from pydantic import BaseModel

from app.schemas.posts import PostResponse
from app.schemas.tags import TagResponse

class SearchResponse(BaseModel):
    posts: list[PostResponse]
    tags: list[TagResponse]
