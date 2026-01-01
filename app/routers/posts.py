from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.utils.auth import verify_admin

from ..db import get_db
from ..models import Post, Tag
from ..schemas import PostResponse, PostCreate, PostUpdate
from ..utils import slugify, validate_unique_slug

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

@router.get("/", response_model=List[PostResponse])
def get_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all posts with pagination"""
    posts = db.query(Post).options(joinedload(Post.tags)).offset(skip).limit(limit).all()
    return posts

@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a post by ID"""
    post = db.query(Post).options(joinedload(Post.tags)).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.get("/slug/{slug}", response_model=PostResponse)
def get_post_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get a post by slug"""
    post = db.query(Post).options(joinedload(Post.tags)).filter(Post.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.post("/", response_model=PostResponse, status_code=201)
def create_post(post_data: PostCreate, db: Session = Depends(get_db), _ = Depends(verify_admin)):
    """Create a post"""
    if post_data.slug:
        slug = post_data.slug
    else:
        slug = slugify(post_data.title)

    validate_unique_slug(slug, Post, db)

    new_post = Post(
        title=post_data.title,
        slug=slug,
        content=post_data.content
    )

    if post_data.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(post_data.tag_ids)).all()
        if len(tags) != len(post_data.tag_ids):
            raise HTTPException(status_code=404, detail="One or more tags not found")
        new_post.tags = tags

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.patch("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_data: PostUpdate, db: Session = Depends(get_db), _ = Depends(verify_admin)):
    """Update a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post_data.title is not None:
        post.title = post_data.title

    if post_data.slug is not None:
        if post_data.slug != post.slug:
            validate_unique_slug(post_data.slug, Post, db)
            post.slug = post_data.slug
    elif post_data.title is not None:
        new_slug = slugify(post_data.title)
        if new_slug != post.slug:
            validate_unique_slug(new_slug, Post, db)
            post.slug = new_slug

    if post_data.content is not None:
        post.content = post_data.content

    if post_data.tag_ids is not None:
        if post_data.tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(post_data.tag_ids)).all()
            if len(tags) != len(post_data.tag_ids):
                raise HTTPException(status_code=404, detail="One or more tags not found")
            post.tags = tags
        else:
            post.tags = []

    db.commit()
    db.refresh(post)

    return post

@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db), _ = Depends(verify_admin)):
    """Delete a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()

    return None
