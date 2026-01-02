from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.database import get_db
from app.models.posts import Post
from app.models.tags import Tag
from app.schemas.search import SearchResponse, PostSearchResult, TagSearchResult

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/autocomplete", response_model=SearchResponse)
def autocomplete_search(q: str = Query(..., min_length=1, description="Search query string"), db: Session = Depends(get_db)
):
    """Autocomplete search endpoint for posts and tags"""

    # Search posts by title or content
    posts = db.query(Post).filter(
        or_(
            Post.title.ilike(f"%{q}%"),
            Post.content.ilike(f"%{q}%")
        )
    ).limit(10).all()

    # Search tags by name
    tags = db.query(Tag).filter(
        Tag.name.ilike(f"%{q}%")
    ).limit(5).all()

    return SearchResponse(
        posts=[PostSearchResult.model_validate(post) for post in posts],
        tags=[TagSearchResult.model_validate(tag) for tag in tags]
    )
