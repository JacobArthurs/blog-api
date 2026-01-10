from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.utils.auth import verify_admin

from ..db import get_db
from ..models import Comment, Post
from ..schemas import CommentResponse, CommentCreate

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

@router.post("/", response_model=CommentResponse, status_code=201)
def create_comment(comment_data: CommentCreate, db: Session = Depends(get_db)):
    """Create a comment"""
    post = db.query(Post).filter(Post.id == comment_data.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if comment_data.parent_id:
        parent_comment = db.query(Comment).filter(Comment.id == comment_data.parent_id).first()
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        if parent_comment.post_id != comment_data.post_id:
            raise HTTPException(status_code=400, detail="Parent comment does not belong to the specified post")

    new_comment = Comment(
        post_id=comment_data.post_id,
        parent_id=comment_data.parent_id,
        author_name=comment_data.author_name,
        author_email=comment_data.author_email,
        content=comment_data.content
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment

@router.post("/{comment_id}/like", response_model=CommentResponse)
def like_comment(comment_id: int, db: Session = Depends(get_db)):
    """Like a comment by incrementing its like count"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.like_count += 1
    db.commit()
    db.refresh(comment)

    return comment

@router.post("/{comment_id}/dislike", response_model=CommentResponse)
def dislike_comment(comment_id: int, db: Session = Depends(get_db)):
    """Dislike a comment by decrementing its like count"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.like_count -= 1
    db.commit()
    db.refresh(comment)

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
