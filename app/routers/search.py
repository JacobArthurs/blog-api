from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.database import get_db
from app.models.posts import Post
from app.models.tags import Tag
from app.schemas.search import SearchResponse

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/autocomplete", response_model=SearchResponse)
def autocomplete_search(q: str = Query(..., min_length=1), offset: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Autocomplete search endpoint for posts and tags"""

    # Search posts by title or summary
    posts = db.query(Post).filter(
        or_(
            Post.title.ilike(f"%{q}%"),
            Post.summary.ilike(f"%{q}%")
        )
    ).order_by(Post.view_count.desc(), Post.created_at.desc()).offset(offset).limit(limit).all()

    # Search tags by name
    tags = db.query(Tag).filter(
        Tag.name.ilike(f"%{q}%")
    ).order_by(Tag.created_at.desc()).limit(5).all()

    return SearchResponse(
        posts=posts,
        tags=tags
    )
