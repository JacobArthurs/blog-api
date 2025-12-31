from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from ..db import get_db
from ..models import Comment
from ..schemas import CommentResponse

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

@router.get("/post/{post_id}", response_model=List[CommentResponse])
def get_comments_by_post(post_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all comments for a specific post"""
    comments = db.query(Comment).options(joinedload(Comment.replies)).filter(Comment.post_id == post_id, Comment.parent_id == None).offset(skip).limit(limit).all()
    return comments
