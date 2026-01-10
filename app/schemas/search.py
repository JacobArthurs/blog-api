from pydantic import BaseModel

from app.schemas.pagination import PaginatedResponse
from app.schemas.posts import PostResponse
from app.schemas.tags import TagResponse

class SearchResponse(BaseModel):
    posts: PaginatedResponse[PostResponse]
    tags: list[TagResponse]
