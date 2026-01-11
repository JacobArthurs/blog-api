from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from app.utils import limiter, view_cache
from slowapi.util import get_remote_address
from app.utils.auth import verify_admin

from ..db import get_db
from ..models import Comment, Post
from ..schemas import CommentResponse, CommentCreate, PaginatedResponse

router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)

@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """Get a comment by ID"""
    comment = db.query(Comment).options(joinedload(Comment.replies)).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.get("/post/{post_id}", response_model=PaginatedResponse[CommentResponse])
def get_comments_by_post(post_id: int, offset: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get all comments for a specific post"""
    query = db.query(Comment).options(joinedload(Comment.replies)).filter(Comment.post_id == post_id, Comment.parent_id == None).order_by(Comment.like_count.desc(), Comment.created_at.desc())
    total = query.count()
    comments = query.offset(offset).limit(limit).all()
    return PaginatedResponse(items=comments, total=total, offset=offset, limit=limit)

@router.post("/", response_model=CommentResponse, status_code=201)
@limiter.limit("3/minute")
@limiter.limit("20/hour")
def create_comment(request: Request, comment_data: CommentCreate, db: Session = Depends(get_db)):
    """Create a comment"""
    post = db.query(Post).filter(Post.id == comment_data.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if comment_data.parent_id is not None:
        parent_comment = db.query(Comment).filter(Comment.id == comment_data.parent_id).first()
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        if parent_comment.post_id != comment_data.post_id:
            raise HTTPException(status_code=400, detail="Parent comment does not belong to the specified post")
        if parent_comment.depth >= 4:
            raise HTTPException(status_code=400, detail="Maximum comment reply depth reached")

    new_comment = Comment(
        post_id=comment_data.post_id,
        parent_id=comment_data.parent_id,
        depth=parent_comment.depth + 1 if comment_data.parent_id else 0,
        author_name=comment_data.author_name,
        author_email=comment_data.author_email,
        content=comment_data.content
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment

@router.post("/{comment_id}/like", response_model=CommentResponse)
@limiter.limit("10/minute")
@limiter.limit("100/hour")
def like_comment(request: Request, comment_id: int, db: Session = Depends(get_db)):
    """Like a comment by incrementing its like count"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    client_ip = get_remote_address(request)
    cache_key = f"like:{comment.id}:{client_ip}"

    if cache_key not in view_cache:
        comment.like_count += 1
        db.commit()
        db.refresh(comment)
        view_cache[cache_key] = True

    return comment

@router.post("/{comment_id}/dislike", response_model=CommentResponse)
@limiter.limit("10/minute")
@limiter.limit("100/hour")
def dislike_comment(request: Request, comment_id: int, db: Session = Depends(get_db)):
    """Dislike a comment by decrementing its like count"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    client_ip = get_remote_address(request)
    cache_key = f"dislike:{comment.id}:{client_ip}"

    if cache_key not in view_cache:
        comment.like_count -= 1
        db.commit()
        db.refresh(comment)
        view_cache[cache_key] = True

    return comment

@router.delete("/{comment_id}", status_code=204)
def delete_comment(comment_id: int, db: Session = Depends(get_db), _ = Depends(verify_admin)):
    """Delete a comment"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()

    return None
